from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = PROJECT_ROOT / "思忆集app"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from app_context import AppContext


def main() -> int:
    parser = argparse.ArgumentParser(description="思忆集桌面端统一 Doctor 入口")
    parser.add_argument("--deep", action="store_true", help="执行远端连通性和 LLM 深度探测")
    parser.add_argument("--json", action="store_true", help="输出 JSON 结果")
    parser.add_argument("--debug-assets-json", action="store_true", help="输出结构化诊断资产 JSON")
    parser.add_argument("--output", default="", help="将结果写入指定文件")
    args = parser.parse_args()

    try:
        app_context = AppContext()
        report = app_context.run_desktop_doctor(deep=bool(args.deep))
    except Exception as exc:
        print(f"错误: 桌面 Doctor 初始化失败: {exc}", file=sys.stderr)
        return 1

    try:
        if args.debug_assets_json:
            assets = app_context.build_desktop_doctor_debug_assets(report)
            rendered = json.dumps(assets, ensure_ascii=False, indent=2)
        elif args.json:
            rendered = json.dumps(report, ensure_ascii=False, indent=2)
        else:
            rendered = app_context.format_desktop_doctor_report(report)
    except Exception as exc:
        print(f"错误: 渲染 Doctor 输出失败: {exc}", file=sys.stderr)
        return 1

    if args.output:
        try:
            Path(args.output).expanduser().resolve().write_text(rendered + "\n", encoding="utf-8")
        except OSError as exc:
            print(f"错误: 写入输出文件失败: {exc}", file=sys.stderr)
            return 1

    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())