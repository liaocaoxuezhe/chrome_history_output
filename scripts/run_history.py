#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Browser History Wrapper Script
用于从外部调用 browser_history.py，支持通过命令行参数指定日期。

用法:
    python run_history.py --history-dir /path/to/chrome_history --relative-day -1
    python run_history.py --history-dir /path/to/chrome_history --date 2026-02-25
"""

import argparse
import sys
import os
from datetime import datetime, timedelta


def parse_args():
    parser = argparse.ArgumentParser(description='提取浏览器历史记录并生成日报')
    parser.add_argument(
        '--history-dir',
        required=True,
        help='chrome_history 目录的绝对路径（包含 browser_history.py 的目录）'
    )

    date_group = parser.add_mutually_exclusive_group()
    date_group.add_argument(
        '--relative-day',
        type=int,
        default=-1,
        help='相对于今天的天数偏移（0=今天，-1=昨天，-2=前天，以此类推）'
    )
    date_group.add_argument(
        '--date',
        type=str,
        help='指定具体日期，格式: YYYY-MM-DD'
    )

    return parser.parse_args()


def date_to_relative_day(date_str):
    """将 YYYY-MM-DD 字符串转换为相对于今天的偏移天数"""
    target = datetime.strptime(date_str, '%Y-%m-%d')
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    delta = (target - today).days
    return delta


def main():
    args = parse_args()

    # 验证 history-dir 是否存在
    history_dir = os.path.abspath(args.history_dir)
    if not os.path.isdir(history_dir):
        print(f"错误: 目录不存在: {history_dir}")
        sys.exit(1)

    browser_history_script = os.path.join(history_dir, 'scripts', 'browser_history.py')
    if not os.path.isfile(browser_history_script):
        print(f"错误: 在 {history_dir}/scripts 中找不到 browser_history.py")
        sys.exit(1)

    # 计算 relative_day
    if args.date:
        try:
            relative_day = date_to_relative_day(args.date)
            target_date_str = args.date
        except ValueError:
            print(f"错误: 日期格式不正确，请使用 YYYY-MM-DD 格式: {args.date}")
            sys.exit(1)
    else:
        relative_day = args.relative_day
        target_date_str = (datetime.now() + timedelta(days=relative_day)).strftime('%Y-%m-%d')

    print(f"目标日期: {target_date_str}（relative_day={relative_day}）")
    print(f"从目录读取: {history_dir}")

    scripts_dir = os.path.join(history_dir, 'scripts')
    # 将 scripts 目录加入 sys.path，以便 import browser_history
    sys.path.insert(0, scripts_dir)

    # 切换工作目录到 history_dir（browser_history.py 使用项目根目录定位输出）
    original_dir = os.getcwd()
    os.chdir(history_dir)

    try:
        import browser_history as bh

        # 覆盖 RELATIVE_DAY 全局变量
        bh.RELATIVE_DAY = relative_day

        all_history_data = []

        # 浏览器列表和对应的获取函数
        browsers = [
            ('Chrome', bh.get_chrome_profile_paths),
            ('Edge', bh.get_edge_profile_paths),
            ('Safari', bh.get_safari_history_path),
            ('Arc', bh.get_arc_history_path),
            ('Firefox', bh.get_firefox_profile_paths),
            ('Brave', bh.get_brave_profile_paths),
            ('Vivaldi', bh.get_vivaldi_profile_paths),
            ('Opera', bh.get_opera_profile_paths),
            ('Dia', bh.get_dia_profile_paths),
            ('Atlas', bh.get_atlas_profile_paths),
            ('Comet', bh.get_comet_profile_paths),
            ('Tabbit', bh.get_tabbit_profile_paths),
            ('Tabbit Browser', bh.get_tabbit_browser_profile_paths),
            ('Zen', bh.get_zen_profile_paths),
            ('SigmaOS', bh.get_sigmaos_profile_paths),
        ]

        for browser_name, path_func in browsers:
            try:
                paths = path_func()
                if not paths:
                    continue
                if isinstance(paths, str):
                    paths = [paths]
                for p in paths:
                    try:
                        data = bh.get_history_from_db(p, browser_name)
                        all_history_data.extend(data)
                        print(f"{browser_name}: 获取 {len(data)} 条记录 [{p}]")
                    except Exception as e:
                        print(f"{browser_name} 配置文件跳过 {p}: {e}")
            except Exception as e:
                print(f"{browser_name} 跳过: {e}")

        # 汇总与导出
        if all_history_data:
            all_history_data.sort(key=lambda x: x[2], reverse=True)
            csv_file = bh.export_to_csv(all_history_data)
            total = len(all_history_data)
            print(f"\n✅ 共导出 {total} 条记录 → {csv_file}")

            # AI 分析（需要配置 api_key）
            summary = bh.summarize_history(all_history_data)
            if summary:
                md_file = bh.save_summary_as_markdown(summary)
                print(f"✅ 日报已生成 → {md_file}")
                print(f"\nSUMMARY_FILE:{md_file}")
            else:
                print("⚠️  AI API 未配置或调用失败，跳过 AI 分析")
                print(f"CSV_FILE:{csv_file}")

            print(f"TOTAL_RECORDS:{total}")
            print(f"TARGET_DATE:{target_date_str}")
        else:
            print(f"⚠️  {target_date_str} 没有找到任何浏览记录")
            print(f"NO_RECORDS:{target_date_str}")

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        os.chdir(original_dir)


if __name__ == '__main__':
    main()
