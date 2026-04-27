#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动检测常见浏览器的历史记录数据库路径。
支持 macOS、Windows、Linux。

用法:
    python detect_browser_paths.py           # 检测所有浏览器
    python detect_browser_paths.py --init    # 生成 config.json 配置文件
    python detect_browser_paths.py --browser Chrome  # 只检测 Chrome
    python detect_browser_paths.py --scan ~/Library/Application Support  # 扫描自定义目录
"""

import os
import sys
import glob
import platform
import json
import argparse

# 各浏览器在不同平台的默认路径模板
BROWSER_PATH_TEMPLATES = {
    'Darwin': {  # macOS
        'Chrome': [
            '~/Library/Application Support/Google/Chrome/Default/History',
            '~/Library/Application Support/Google/Chrome/Profile */History',
        ],
        'Edge': [
            '~/Library/Application Support/Microsoft Edge/Default/History',
            '~/Library/Application Support/Microsoft Edge/Profile */History',
        ],
        'Safari': [
            '~/Library/Safari/History.db',
        ],
        'Arc': [
            '~/Library/Application Support/Arc/User Data/Default/History',
        ],
        'Firefox': [
            '~/Library/Application Support/Firefox/Profiles/*/places.sqlite',
        ],
        'Dia': [
            '~/Library/Application Support/Dia/Default/History',
            '~/Library/Application Support/Dia/Profile */History',
            '~/Library/Application Support/Dia/User Data/Default/History',
            '~/Library/Application Support/Dia/User Data/Profile */History',
            '~/Library/Containers/com.dia.browser/Data/Library/Application Support/Dia/Default/History',
        ],
        'Brave': [
            '~/Library/Application Support/BraveSoftware/Brave-Browser/Default/History',
            '~/Library/Application Support/BraveSoftware/Brave-Browser/Profile */History',
        ],
        'Opera': [
            '~/Library/Application Support/com.operasoftware.Opera/History',
        ],
        'Vivaldi': [
            '~/Library/Application Support/Vivaldi/Default/History',
            '~/Library/Application Support/Vivaldi/Profile */History',
        ],
        'Atlas': [
            '~/Library/Application Support/Atlas/Default/History',
            '~/Library/Application Support/Atlas/Profile */History',
            '~/Library/Application Support/Atlas/User Data/Default/History',
            '~/Library/Containers/com.openai.atlas/Data/Library/Application Support/Atlas/Default/History',
        ],
        'Comet': [
            '~/Library/Application Support/Comet/Default/History',
            '~/Library/Application Support/Comet/Profile */History',
        ],
        'Tabbit': [
            '~/Library/Application Support/Tabbit/Default/History',
            '~/Library/Application Support/Tabbit/Profile */History',
        ],
        'Zen': [
            '~/Library/Application Support/Zen/Default/History',
            '~/Library/Application Support/Zen/Profile */History',
        ],
        'SigmaOS': [
            '~/Library/Application Support/SigmaOS/Default/History',
        ],
    },
    'Windows': {
        'Chrome': [
            r'%LOCALAPPDATA%\Google\Chrome\User Data\Default\History',
            r'%LOCALAPPDATA%\Google\Chrome\User Data\Profile *\History',
        ],
        'Edge': [
            r'%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\History',
            r'%LOCALAPPDATA%\Microsoft\Edge\User Data\Profile *\History',
        ],
        'Firefox': [
            r'%APPDATA%\Mozilla\Firefox\Profiles\*\places.sqlite',
        ],
        'Brave': [
            r'%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default\History',
            r'%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Profile *\History',
        ],
        'Opera': [
            r'%APPDATA%\Opera Software\Opera Stable\History',
        ],
        'Vivaldi': [
            r'%LOCALAPPDATA%\Vivaldi\User Data\Default\History',
            r'%LOCALAPPDATA%\Vivaldi\User Data\Profile *\History',
        ],
        'Arc': [
            r'%LOCALAPPDATA%\Arc\User Data\Default\History',
        ],
    },
    'Linux': {
        'Chrome': [
            '~/.config/google-chrome/Default/History',
            '~/.config/google-chrome/Profile */History',
        ],
        'Edge': [
            '~/.config/microsoft-edge/Default/History',
            '~/.config/microsoft-edge/Profile */History',
        ],
        'Firefox': [
            '~/.mozilla/firefox/*/places.sqlite',
        ],
        'Brave': [
            '~/.config/BraveSoftware/Brave-Browser/Default/History',
            '~/.config/BraveSoftware/Brave-Browser/Profile */History',
        ],
        'Opera': [
            '~/.config/opera/History',
        ],
        'Vivaldi': [
            '~/.config/vivaldi/Default/History',
            '~/.config/vivaldi/Profile */History',
        ],
    }
}


def expand_path(path):
    """展开路径中的环境变量和 ~"""
    return os.path.expandvars(os.path.expanduser(path))


def find_browser_paths(browser_name=None):
    """
    检测系统中可用的浏览器历史记录路径。

    Args:
        browser_name: 指定浏览器名称，None 则检测所有

    Returns:
        dict: {浏览器名称: [路径列表]}
    """
    system = platform.system()
    templates = BROWSER_PATH_TEMPLATES.get(system, {})

    if not templates:
        print(f"警告: 暂不支持操作系统 {system}")
        return {}

    results = {}

    for name, patterns in templates.items():
        if browser_name and name.lower() != browser_name.lower():
            continue

        found = []
        for pattern in patterns:
            expanded = expand_path(pattern)
            matches = glob.glob(expanded)
            for match in matches:
                if os.path.exists(match):
                    found.append(match)

        if found:
            results[name] = found

    return results


def scan_custom_paths(base_dirs):
    """
    扫描用户指定的额外目录，查找 History 数据库文件。

    Args:
        base_dirs: 要扫描的目录列表

    Returns:
        list: 找到的 History 文件路径
    """
    found = []
    for base in base_dirs:
        base = expand_path(base)
        if not os.path.isdir(base):
            continue
        for root, dirs, files in os.walk(base):
            # 跳过常见的缓存和临时目录
            dirs[:] = [d for d in dirs if d.lower() not in
                      {'cache', 'caches', 'tmp', 'temp', 'logs', 'crashpad'}]
            for f in files:
                if f.lower() == 'history' or f.lower() == 'places.sqlite':
                    full = os.path.join(root, f)
                    found.append(full)
    return found


def generate_config(output_path='config.json'):
    """
    自动生成配置文件，包含检测到的浏览器路径。
    """
    detected = find_browser_paths()

    config = {
        'browsers': detected,
        'custom_paths': [],
        'api': {
            'api_key': '',
            'base_url': 'https://generativelanguage.googleapis.com/v1beta/openai/',
            'model_name': 'gemini-2.0-flash'
        },
        'output': {
            'relative_day': -1,
            'timezone_offset': 8,
            'max_records': 800
        }
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print(f"配置文件已生成: {output_path}")
    print(f"检测到 {len(detected)} 个浏览器:")
    for name, paths in detected.items():
        print(f"  {name}: {len(paths)} 个配置")
        for p in paths:
            print(f"    - {p}")

    return config


def print_detected():
    """打印检测到的浏览器路径"""
    detected = find_browser_paths()

    if not detected:
        print("未检测到任何浏览器历史记录数据库。")
        print("\n你可以:")
        print("1. 确认浏览器已安装并使用过")
        print("2. 使用 --scan 参数扫描自定义目录")
        print("3. 手动编辑 config.json 添加路径")
        return

    print("检测到的浏览器历史记录数据库:")
    print("=" * 50)
    for name, paths in detected.items():
        print(f"\n{name}:")
        for p in paths:
            print(f"  ✓ {p}")
    print("\n" + "=" * 50)
    print(f"共检测到 {len(detected)} 个浏览器")
    print("\n提示: 运行 python detect_browser_paths.py --init 生成配置文件")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='检测浏览器历史记录数据库路径')
    parser.add_argument('--browser', help='指定浏览器名称')
    parser.add_argument('--init', action='store_true', help='生成配置文件')
    parser.add_argument('--scan', nargs='+', help='扫描自定义目录')
    args = parser.parse_args()

    if args.init:
        generate_config()
    elif args.scan:
        print("扫描自定义目录...")
        custom = scan_custom_paths(args.scan)
        for p in custom:
            print(f"  发现: {p}")
    else:
        if args.browser:
            result = find_browser_paths(args.browser)
            for name, paths in result.items():
                print(f"{name}: {paths}")
        else:
            print_detected()
