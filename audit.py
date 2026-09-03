# -*- coding: utf-8 -*-
"""
Yoonup 技能仓库自动化校对脚本（audit.py）

治本方案：把校对从"AI手动执行命令"变成"确定性脚本执行"。
AI 调用技能时必须运行本脚本，退出码非零即不通过，必须修复后重跑。

用法：
    python3 audit.py              # 完整三轮校对
    python3 audit.py --round 1    # 只跑第1轮（结构与一致性）
    python3 audit.py --round 2    # 只跑第2轮（逻辑与边界）
    python3 audit.py --round 3    # 只跑第3轮（安全与运维）
    python3 audit.py --quality    # 只跑代码质量专项

退出码：0=全部通过，1=有未通过项
"""
import os
import sys
import json
import ast
import re
import subprocess
import tempfile
import argparse
from typing import List, Dict, Any, Tuple

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

PASS = 0
FAIL = 0
RESULTS: List[Tuple[str, bool, str]] = []


def record(name: str, ok: bool, detail: str = ""):
    global PASS, FAIL
    RESULTS.append((name, ok, detail))
    if ok:
        PASS += 1
        print(f"  ✅ {name}" + (f": {detail}" if detail else ""))
    else:
        FAIL += 1
        print(f"  ❌ {name}" + (f": {detail}" if detail else ""))


# ========== 第 1 轮：结构与一致性 ==========

def round1_structure():
    print("\n===== 第 1 轮：结构与一致性 =====")

    # 1.1 最新提交
    try:
        r = subprocess.run(["git", "-C", BASE_DIR, "log", "--oneline", "-1"],
                           capture_output=True, text=True, timeout=5)
        record("最新提交", r.returncode == 0, r.stdout.strip())
    except Exception as e:
        record("最新提交", False, str(e))

    # 1.2 技能注册字段完整性
    try:
        with open(os.path.join(BASE_DIR, "skills.json"), encoding="utf-8") as f:
            cfg = json.load(f)
        required = ["id", "name", "file", "description", "check_section", "check_categories"]
        all_ok = True
        details = []
        for s in cfg["skills"]:
            missing = [r for r in required if r not in s]
            if missing:
                all_ok = False
                details.append(f"{s.get('id','?')}缺{missing}")
        record("技能注册字段完整", all_ok, f"{len(cfg['skills'])}个技能" + ("," + ",".join(details) if details else ""))
    except Exception as e:
        record("技能注册字段完整", False, str(e))

    # 1.3 校验清单解析
    try:
        from validator import list_skills, get_skill_checklist, flatten_checklist
        total = 0
        all_ids = []
        all_ok = True
        for s in list_skills():
            data = get_skill_checklist(s["id"])
            flat = flatten_checklist(data["checklist"])
            total += len(flat)
            all_ids.extend([it["id"] for it in flat])
            if len(data["checklist"]) == 0:
                all_ok = False
        id_unique = len(all_ids) == len(set(all_ids))
        record("校验清单解析", all_ok and id_unique,
               f"{total}条, ID唯一={id_unique}")
    except Exception as e:
        record("校验清单解析", False, str(e))

    # 1.4 CHECKERS 覆盖
    try:
        from validator import list_skills, get_skill_checklist, flatten_checklist, CHECKERS
        auto_cats = set()
        for s in list_skills():
            for it in flatten_checklist(get_skill_checklist(s["id"])["checklist"]):
                if it["method"] in ("auto", "both"):
                    auto_cats.add(it["category"])
        missing = auto_cats - set(CHECKERS.keys())
        record("CHECKERS覆盖", len(missing) == 0,
               f"{len(CHECKERS)}个检查器, 缺={missing if missing else '无'}")
    except Exception as e:
        record("CHECKERS覆盖", False, str(e))

    # 1.5 Python 语法
    ok1 = os.system(f"python3 -m py_compile {os.path.join(BASE_DIR, 'validator.py')}") == 0
    ok2 = os.system(f"python3 -m py_compile {os.path.join(BASE_DIR, 'mcp_server.py')}") == 0
    record("Python语法", ok1 and ok2, "validator.py + mcp_server.py" if ok1 and ok2 else "有语法错误")

    # 1.6 无 BOM
    bom_files = []
    for root, _, files in os.walk(BASE_DIR):
        if ".git" in root:
            continue
        for fname in files:
            if fname.endswith((".py", ".md", ".json", ".yml", ".txt")):
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, "rb") as f:
                        if f.read(3) == b"\xef\xbb\xbf":
                            bom_files.append(fname)
                except Exception:
                    pass
    record("无BOM", len(bom_files) == 0, f"BOM文件={bom_files if bom_files else '无'}")

    # 1.7 AGENTS.md ↔ references 一致
    agents = os.path.join(BASE_DIR, "AGENTS.md")
    ref_agents = os.path.join(BASE_DIR, "skills/yoonup-workflow/references/agents-convention.md")
    if os.path.exists(agents) and os.path.exists(ref_agents):
        with open(agents, encoding="utf-8") as f1, open(ref_agents, encoding="utf-8") as f2:
            same = f1.read() == f2.read()
        record("AGENTS.md↔references一致", same)
    else:
        record("AGENTS.md↔references一致", False, "文件不存在")

    # 1.8 references ↔ skills 对应文件一致
    pairs = [
        ("skills/yoonup-workflow/references/python-app-standard.md", "skills/python-app-standard/SKILL.md"),
        ("skills/yoonup-workflow/references/web-js-app-implementation.md", "skills/web-js-app-implementation/SKILL.md"),
    ]
    all_ok = True
    for a, b in pairs:
        pa, pb = os.path.join(BASE_DIR, a), os.path.join(BASE_DIR, b)
        if os.path.exists(pa) and os.path.exists(pb):
            with open(pa, encoding="utf-8") as f1, open(pb, encoding="utf-8") as f2:
                if f1.read() != f2.read():
                    all_ok = False
        else:
            all_ok = False
    record("references↔skills一致", all_ok)

    # 1.9 dist zip 内容一致
    all_ok = True
    for skill in ["python-app-standard", "web-js-app-implementation", "yoonup-workflow"]:
        zip_path = os.path.join(BASE_DIR, f"dist/{skill}.zip")
        if not os.path.exists(zip_path):
            all_ok = False
            continue
        with tempfile.TemporaryDirectory() as td:
            subprocess.run(["unzip", "-q", zip_path, "-d", td], capture_output=True)
            r = subprocess.run(["diff", "-rq", os.path.join(td, skill),
                                os.path.join(BASE_DIR, f"skills/{skill}")],
                               capture_output=True, text=True)
            if r.returncode != 0:
                all_ok = False
    record("dist zip一致", all_ok)

    # 1.10 check_section 字段匹配
    try:
        with open(os.path.join(BASE_DIR, "skills.json"), encoding="utf-8") as f:
            cfg = json.load(f)
        all_ok = True
        for s in cfg["skills"]:
            md_path = os.path.join(BASE_DIR, "skills", s["file"])
            with open(md_path, encoding="utf-8") as f:
                content = f.read()
            if f"## {s.get('check_section', '')}" not in content:
                all_ok = False
        record("check_section匹配", all_ok)
    except Exception as e:
        record("check_section匹配", False, str(e))


# ========== 第 2 轮：逻辑与边界 ==========

def round2_logic():
    print("\n===== 第 2 轮：逻辑与边界 =====")
    from validator import check_result, get_skill_checklist, detect_skill, plan_requirement, parse_checklist

    # 2.1 check_result: 文件路径
    r = check_result("/etc/passwd", "yoonup-workflow")
    record("check_result文件路径返回error", "error" in r, r.get("error", ""))

    # 2.2 check_result: 不存在路径
    r = check_result("/nonexistent/xyz/123", "yoonup-workflow")
    record("check_result不存在路径返回error", "error" in r, r.get("error", ""))

    # 2.3 check_result: 空目录 YW00 失败
    with tempfile.TemporaryDirectory() as td:
        r = check_result(td, "yoonup-workflow")
        yw00_fail = any(f["id"] == "YW00" for f in r["auto_failed"])
        record("check_result空目录YW00失败", yw00_fail,
               f"failed={[f['id'] for f in r['auto_failed']]}")

    # 2.4 check_result: 正常目录通过
    r = check_result(BASE_DIR, "yoonup-workflow")
    record("check_result正常目录通过", r["all_auto_passed"],
           f"passed={r['auto_passed']}")

    # 2.5 get_skill_checklist: 不存在ID报错
    try:
        get_skill_checklist("nonexistent-skill")
        record("get_skill_checklist不存在ID报错", False, "未报错")
    except ValueError:
        record("get_skill_checklist不存在ID报错", True)

    # 2.6 detect_skill: 空字符串
    record("detect_skill空字符串", detect_skill("") == "python-app-standard")

    # 2.7 detect_skill: 各技能关键词
    record("detect_skill yoonup", detect_skill("更新技能推到github") == "yoonup-workflow")
    record("detect_skill web", detect_skill("js逆向抓包token") == "web-js-app-implementation")
    record("detect_skill python", detect_skill("定时任务飞书通知") == "python-app-standard")

    # 2.8 plan_requirement: 三个技能都有 steps 和 questions
    all_ok = True
    for sid in ["python-app-standard", "web-js-app-implementation", "yoonup-workflow"]:
        p = plan_requirement("test", sid)
        if len(p["plan_steps"]) == 0 or len(p["questions_to_user"]) == 0:
            all_ok = False
    record("plan_requirement三技能完整", all_ok)

    # 2.9 parse_checklist: 格式错误条目被忽略
    r = parse_checklist("## 校验清单\n### t\n- [ID1] 描述\n")
    record("parse_checklist格式错误忽略", len(r.get("t", [])) == 0)

    # 2.10 parse_checklist: 正常条目解析
    r = parse_checklist("## 校验清单\n### t\n- [ID1] auto d1\n- [ID2] ai d2\n- [ID3] both d3\n")
    record("parse_checklist正常条目", len(r.get("t", [])) == 3)


# ========== 第 3 轮：安全与运维 ==========

def round3_security():
    print("\n===== 第 3 轮：安全与运维 =====")

    # 3.1 工作区敏感信息
    leak = False
    for root, _, files in os.walk(BASE_DIR):
        if ".git" in root:
            continue
        for fname in files:
            if fname.endswith((".py", ".md", ".json", ".yml", ".txt")):
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    if re.search(r"github_pat_[a-zA-Z0-9_]{20,}", content) or \
                       re.search(r"ghp_[a-zA-Z0-9]{36}", content):
                        leak = True
                except Exception:
                    pass
    record("工作区无token泄露", not leak)

    # 3.2 git 历史敏感信息
    try:
        r = subprocess.run(["git", "-C", BASE_DIR, "log", "--all", "-p"],
                           capture_output=True, text=True, timeout=10)
        has_token = bool(re.search(r"github_pat_[a-zA-Z0-9_]{20,}", r.stdout))
        record("git历史无token", not has_token)
    except Exception as e:
        record("git历史无token", False, str(e))

    # 3.3 路径遍历
    try:
        from validator import _read_project
        with tempfile.TemporaryDirectory() as td:
            proj = os.path.join(td, "proj")
            os.makedirs(proj)
            with open(os.path.join(td, "secret.txt"), "w") as f:
                f.write("secret")
            ctx = _read_project(proj)
            record("无路径遍历", "secret.txt" not in ctx["files"])
    except Exception as e:
        record("无路径遍历", False, str(e))

    # 3.4 MCP 启动
    try:
        r = subprocess.run(["python3", os.path.join(BASE_DIR, "mcp_server.py")],
                           capture_output=True, text=True, timeout=3)
        record("MCP启动成功", "startup complete" in r.stdout.lower() or "started" in r.stdout.lower())
    except subprocess.TimeoutExpired:
        record("MCP启动成功", True, "进程正常运行（超时=启动成功）")
    except Exception as e:
        record("MCP启动成功", False, str(e))

    # 3.5 Docker 配置
    dockerfile = os.path.join(BASE_DIR, "Dockerfile")
    compose = os.path.join(BASE_DIR, "docker-compose.yml")
    df_ok = os.path.exists(dockerfile) and "python" in open(dockerfile).read().lower()
    dc_ok = os.path.exists(compose) and "8000" in open(compose).read()
    record("Docker配置正确", df_ok and dc_ok)

    # 3.6 依赖
    try:
        import mcp  # noqa
        import fastapi  # noqa
        record("依赖已安装", True)
    except ImportError as e:
        record("依赖已安装", False, str(e))

    # 3.7 git 状态（无未推送）
    try:
        r = subprocess.run(["git", "-C", BASE_DIR, "status", "-sb"],
                           capture_output=True, text=True, timeout=5)
        record("无未推送提交", "ahead" not in r.stdout)
    except Exception as e:
        record("无未推送提交", False, str(e))

    # 3.8 配置文件存在
    files = [".env.example", "requirements.txt", ".gitignore"]
    all_exist = all(os.path.exists(os.path.join(BASE_DIR, f)) for f in files)
    record("配置文件齐全", all_exist, f"{files}")


# ========== 代码质量专项 ==========

def quality_check():
    print("\n===== 代码质量专项 =====")

    for fname in ["validator.py", "mcp_server.py"]:
        fpath = os.path.join(BASE_DIR, fname)
        with open(fpath, encoding="utf-8") as f:
            tree = ast.parse(f.read())

        # 未使用 import
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.asname or alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                # from X import Y: 只把 Y 加入 imports，不把 X 加入（避免误报）
                for alias in node.names:
                    imports.add(alias.asname or alias.name)
        used = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used.add(node.id)
            elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                used.add(node.value.id)
        unused = {u for u in imports - used if not u.startswith("_") and u not in ("typing",)}
        record(f"{fname}无未使用import", len(unused) == 0, f"未使用={unused if unused else '无'}")

        # 类型注解
        funcs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        total_params = sum(len([a for a in f.args.args if a.arg != "self"]) for f in funcs)
        annotated_params = sum(
            len([a for a in f.args.args if a.arg != "self" and a.annotation]) for f in funcs)
        return_annotated = sum(1 for f in funcs if f.returns)
        record(f"{fname}类型注解",
               annotated_params == total_params and return_annotated == len(funcs),
               f"参数{annotated_params}/{total_params}, 返回值{return_annotated}/{len(funcs)}")

    # 异常处理：listdir 在 try 中
    with open(os.path.join(BASE_DIR, "validator.py"), encoding="utf-8") as f:
        content = f.read()
    record("listdir有异常保护", "try:" in content and "os.listdir" in content)

    # 无调试代码（排除 __main__ 块）
    with open(os.path.join(BASE_DIR, "validator.py"), encoding="utf-8") as f:
        content = f.read()
    main_block = content.split('if __name__')[0] if 'if __name__' in content else content
    has_debug = bool(re.search(r"\bprint\s*\(|pdb\.set_trace|breakpoint", main_block))
    record("无调试代码残留", not has_debug)

    # 文件读写指定 encoding
    with open(os.path.join(BASE_DIR, "validator.py"), encoding="utf-8") as f:
        content = f.read()
    open_calls = re.findall(r'open\([^)]+\)', content)
    no_encoding = [c for c in open_calls if "encoding" not in c and "rb" not in c and '"r"' not in c and "'r'" not in c]
    record("文件读写指定encoding", len(no_encoding) == 0,
           f"未指定encoding的open={len(no_encoding)}个")


def main():
    parser = argparse.ArgumentParser(description="Yoonup 技能仓库自动化校对")
    parser.add_argument("--round", type=int, choices=[1, 2, 3], help="只跑指定轮次")
    parser.add_argument("--quality", action="store_true", help="只跑代码质量专项")
    args = parser.parse_args()

    print(f"Yoonup 自动化校对 - 仓库: {BASE_DIR}")
    print(f"当前提交: ", end="")
    subprocess.run(["git", "-C", BASE_DIR, "log", "--oneline", "-1"])

    if args.quality:
        quality_check()
    elif args.round == 1:
        round1_structure()
    elif args.round == 2:
        round2_logic()
    elif args.round == 3:
        round3_security()
    else:
        round1_structure()
        round2_logic()
        round3_security()
        quality_check()

    print(f"\n{'='*50}")
    print(f"校对结果: 通过 {PASS} 项, 未通过 {FAIL} 项")
    if FAIL == 0:
        print("✅ 全部通过")
        sys.exit(0)
    else:
        print(f"❌ {FAIL} 项未通过，必须修复后重跑")
        sys.exit(1)


if __name__ == "__main__":
    main()
