#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import re
from pathlib import Path

def parse_filename(filename: str):
    name = filename.rsplit('.zip', 1)[0]
    match = re.search(r'[-_](v?\d+(?:\.\d+)+)$', name)
    if not match:
        return None, None
    version = match.group(1)
    plugin_raw = name[:match.start()]
    if not plugin_raw:
        return None, None
    plugin_display = plugin_raw.replace('-', ' ')
    plugin_display = ' '.join(plugin_display.split())  # 清理多余空格
    return plugin_display, version

def get_download_url(file_path: Path, repo_root: Path) -> str:
    rel_path = file_path.relative_to(repo_root)
    base_url = os.environ.get('BASE_URL')
    if base_url:
        return f"{base_url.rstrip('/')}/{rel_path.as_posix()}"
    repository = os.environ.get('GITHUB_REPOSITORY')
    ref = os.environ.get('GITHUB_REF_NAME', 'main')
    if repository:
        return f"https://raw.githubusercontent.com/{repository}/{ref}/{rel_path.as_posix()}"
    # 本地开发占位
    return f"/{rel_path.as_posix()}"

def scan_directory(directory: str, repo_root: Path):
    results = []
    root = Path(directory)
    if not root.exists():
        print(f"⚠️ 目录不存在: {directory}")
        return results

    for file in root.glob('**/*.zip'):
        plugin, version = parse_filename(file.name)
        if plugin and version:
            download_url = get_download_url(file, repo_root)
            results.append({
                'plugin': plugin,
                'version': version,
                'filename': file.name,
                'path': str(file),
                'download_url': download_url
            })
        else:
            print(f"⏭️ 跳过无效文件名: {file.name}")

    results.sort(key=lambda x: x['plugin'])
    return results

def main():
    scan_dir = os.environ.get('SCAN_DIR', './plugins')
    repo_root = Path.cwd()
    print(f"📂 扫描目录: {scan_dir}")
    data = scan_directory(scan_dir, repo_root)
    print(f"✅ 找到 {len(data)} 个有效插件")
    with open('plugins.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("📄 已生成: plugins.json")

if __name__ == '__main__':
    main()