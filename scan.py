#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import re
from pathlib import Path

def parse_filename(filename: str):
    """解析文件名，返回 (插件名, 版本号)"""
    name = filename.rsplit('.zip', 1)[0]          # 去除 .zip 后缀
    # 匹配最后一个分隔符（- 或 _）后的版本号，版本号可含 v 前缀，数字段数 >= 2
    match = re.search(r'[-_](v?\d+(?:\.\d+)+)$', name)
    if not match:
        return None, None
    version = match.group(1)
    # 如果版本号以 'v' 开头，去掉它
    if version.startswith('v'):
        version = version[1:]
    plugin_raw = name[:match.start()]            # 分隔符之前的部分作为插件名
    if not plugin_raw:
        return None, None
    # 将插件名中的 '-' 替换为空格，并清理多余空格
    plugin_display = plugin_raw.replace('-', ' ')
    plugin_display = ' '.join(plugin_display.split())
    return plugin_display, version

def get_download_url(file_path: Path, repo_root: Path) -> str:
    """生成该文件的可下载 URL（优先从环境变量读取，否则使用 GitHub Raw）"""
    abs_file = file_path.resolve()
    abs_repo = repo_root.resolve()
    try:
        rel_path = abs_file.relative_to(abs_repo)
    except ValueError:
        # 如果相对路径计算失败，直接使用文件名（兜底）
        rel_path = Path(file_path.name)
    base_url = os.environ.get('BASE_URL')
    if base_url:
        return f"{base_url.rstrip('/')}/{rel_path.as_posix()}"
    repository = os.environ.get('GITHUB_REPOSITORY')
    ref = os.environ.get('GITHUB_REF_NAME', 'main')
    if repository:
        return f"https://raw.githubusercontent.com/{repository}/{ref}/{rel_path.as_posix()}"
    # 本地开发时返回相对路径
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
                'plugin_name': plugin,
                'version': version,
                'filename': file.name,
                'path': str(file),
                'download_url': download_url
            })
        else:
            print(f"⏭️ 跳过无效文件名: {file.name}")

    results.sort(key=lambda x: x['plugin_name'])
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