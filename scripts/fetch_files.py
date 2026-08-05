#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
from datetime import datetime
from pathlib import Path

# ---------- 请求头伪装 ----------
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://node.freeclashnode.com/'
}

def download_with_retry(url, timeout=30, retries=3, delay=5):
    """带重试的下载函数，成功返回 bytes，失败返回 None"""
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, timeout=timeout, headers=HEADERS)
            if resp.status_code == 200:
                return resp.content
            else:
                print(f"  尝试 {attempt}/{retries}: {url} -> HTTP {resp.status_code}")
                if attempt == retries:
                    return None
                time.sleep(delay)
        except Exception as e:
            print(f"  尝试 {attempt}/{retries}: {url} 异常: {e}")
            if attempt == retries:
                return None
            time.sleep(delay)
    return None

def human_readable_size(size_bytes):
    """将字节数转换为易读格式 (B, KB, MB, ...)"""
    if size_bytes == 0:
        return "0 B"
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    i = 0
    size = float(size_bytes)
    while size >= 1024 and i < len(units) - 1:
        size /= 1024.0
        i += 1
    return f"{size:.2f} {units[i]}"

# ---------- 日期变量 ----------
today = datetime.now()
ym_path = today.strftime("%Y/%m")          # 2026/08
ymd_path = today.strftime("%Y/%m/%d")      # 2026/08/05
date_compact = today.strftime("%Y%m%d")    # 20260805
date_dir = today.strftime("%Y-%m-%d")      # 2026-08-05

# ---------- 创建目录 ----------
latest_dir = Path("latest")
latest_dir.mkdir(exist_ok=True)

archive_dir = Path("archive") / date_dir
archive_dir.mkdir(parents=True, exist_ok=True)

# ---------- 构建下载任务列表 ----------
tasks = []  # 每个元素为 (url, latest_target_name)

# 1. node.freeclashnode.com (5个yaml, 5个txt, 1个json)
for idx in range(5):
    tasks.append((f"https://node.freeclashnode.com/uploads/{ym_path}/{idx}-{date_compact}.yaml", f"clash{idx}.yaml"))
    tasks.append((f"https://node.freeclashnode.com/uploads/{ym_path}/{idx}-{date_compact}.txt", f"v2ray{idx}.txt"))
tasks.append((f"https://node.freeclashnode.com/uploads/{ym_path}/{date_compact}.json", f"{date_compact}.json"))

# 2. freenode.yoyapai.com (2个文件)
tasks.append((f"https://freenode.yoyapai.com/{ymd_path}-yoyapai.com-clash-vpn-mian-feijiedian.yaml", "clash100.yaml"))
tasks.append((f"https://freenode.yoyapai.com/{ymd_path}-yoyapai.com-ssrv2ray-vpn-mian-feijiedian.txt", "v2ray100.txt"))

# ---------- 执行下载 ----------
for url, latest_name in tasks:
    print(f"⬇️ 正在下载: {url}")
    content = download_with_retry(url)
    if content is None:
        print(f"❌ 跳过 {url}")
        continue

    # 保存原始文件到归档（文件名取自 URL）
    original_filename = url.split('/')[-1]
    archive_path = archive_dir / original_filename
    with open(archive_path, 'wb') as f:
        f.write(content)
    print(f"📁 归档: {archive_path}")

    # 保存重命名文件到 latest
    latest_path = latest_dir / latest_name
    with open(latest_path, 'wb') as f:
        f.write(content)
    print(f"🔄 更新 latest: {latest_path}")

# ---------- 生成 README.txt ----------
readme_path = Path("README.txt")
base_url = "https://github.com/tuiseliunian/free-gfw/tree/main/latest"
link_lines = []

for file_path in sorted(latest_dir.glob("*")):
    if file_path.is_file():
        size = file_path.stat().st_size
        size_str = human_readable_size(size)
        link_lines.append(f"{base_url}/{file_path.name}  ({size_str})")

with open(readme_path, 'w', encoding='utf-8') as f:
    f.write("\n".join(link_lines))

print(f"✅ 已生成 {readme_path}，共 {len(link_lines)} 个链接")