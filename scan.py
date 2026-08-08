#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import re
from pathlib import Path

def parse_filename(filename: str):
    """解析 zip 文件名，返回 (插件名, 版本号)"""
    name = filename.replace('.zip', '')
    # 匹配最后一个分隔符（-或_）后的版本号，版本号至少两位数字（如1.2, 2.5.6, 3.0.0.1）
    match = re.search(r'[-_](v?\d+(?:\.\d+)+)$', name)
    if not match:
        return None, None
    version = match.group(1)
    plugin_raw = name[:match.start()]
    if not plugin_raw:
        return None, None
    plugin_display = plugin_raw.replace('-', ' ')
    # 清洗多余空格
    plugin_display = ' '.join(plugin_display.split())
    return plugin_display, version


def scan_directory(directory: str):
    results = []
    root = Path(directory)
    if not root.exists():
        print(f"⚠️ 目录不存在: {directory}")
        return results

    for file in root.glob('**/*.zip'):
        plugin, version = parse_filename(file.name)
        if plugin and version:
            results.append({
                'plugin': plugin,
                'version': version,
                'filename': file.name,
                'path': str(file)
            })
        else:
            print(f"⏭️ 跳过无效文件名: {file.name}")

    results.sort(key=lambda x: x['plugin'])
    return results


def main():
    scan_dir = os.environ.get('SCAN_DIR', './plugins')
    print(f"📂 扫描目录: {scan_dir}")
    data = scan_directory(scan_dir)
    print(f"✅ 找到 {len(data)} 个有效插件")
    with open('plugins.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("📄 已生成: plugins.json")


if __name__ == '__main__':
    main()