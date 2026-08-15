#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ---------- 请求头伪装 ----------
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://node.freeclashnode.com/'
}

def download_with_retry(url, timeout=30, retries=3, delay=5):
    """带重试的下载函数，成功返回 (bytes, last_modified_datetime_or_None)，失败返回 (None, None)"""
    from email.utils import parsedate_to_datetime
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, timeout=timeout, headers=HEADERS)
            if resp.status_code == 200:
                # 尝试解析 Last-Modified 头（如果存在）
                lm = resp.headers.get('Last-Modified')
                if lm:
                    try:
                        dt = parsedate_to_datetime(lm)
                        # 转为 +08:00 时区（中国标准时间）
                        tz8 = timezone(timedelta(hours=8))
                        if dt.tzinfo is None:
                            dt = dt.replace(tzinfo=timezone.utc)
                        dt = dt.astimezone(tz8)
                    except Exception:
                        dt = None
                else:
                    dt = None
                return resp.content, dt
            else:
                print(f"  尝试 {attempt}/{retries}: {url} -> HTTP {resp.status_code}")
                if attempt == retries:
                    return None, None
                time.sleep(delay)
        except Exception as e:
            print(f"  尝试 {attempt}/{retries}: {url} 异常: {e}")
            if attempt == retries:
                return None, None
            time.sleep(delay)
    return None, None

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

# 2. freenode.yoyapai.com (2个文件) - 尝试最多回溯 3 天（今天、-1、-2）以适应发布时间差或命名变更
freenode_base = "https://freenode.yoyapai.com"
clash_candidates = []
ssrv_candidates = []
# 对于每个日期偏移，生成若干常见命名格式
for offset in range(0, 3):
    d = today - timedelta(days=offset)
    ymd = d.strftime("%Y/%m/%d")
    compact = d.strftime("%Y%m%d")

    # clash 候选格式（移除 -clash-vpn-mian-feijiedian 的老格式）
    cands = [
        f"{freenode_base}/{ymd}-yoyapai.com-clashvpnmian-fei-jiedian.yaml",
        f"{freenode_base}/{compact}-yoyapai.com-clashvpnmian-fei-jiedian.yaml",
    ]
    for u in cands:
        if u not in clash_candidates:
            clash_candidates.append(u)

    # ssrv 候选格式（移除 -ssrv2ray-vpn-mian-feijiedian 的老格式）
    s_cands = [
        f"{freenode_base}/{ymd}-yoyapai.com-ssrv2rayvpnmian-fei-jiedian.txt",
        f"{freenode_base}/{compact}-yoyapai.com-ssrv2rayvpnmian-fei-jiedian.txt",
    ]
    for u in s_cands:
        if u not in ssrv_candidates:
            ssrv_candidates.append(u)

# 将候选列表作为任务的一部分，下载循环会尝试每个候选 URL
tasks.append((clash_candidates, "clash100.yaml"))
tasks.append((ssrv_candidates, "v2ray100.txt"))

# ---------- 执行下载 ----------
# 存储每个 latest 文件对应的生成时间（+08:00）
timestamps = {}
for url_entry, latest_name in tasks:
    chosen_url = None
    content = None
    last_modified = None

    # 支持单个字符串或候选 URL 列表
    if isinstance(url_entry, (list, tuple)):
        for candidate in url_entry:
            print(f"⬇️ 尝试候选 URL: {candidate}")
            content, last_modified = download_with_retry(candidate)
            if content is not None:
                chosen_url = candidate
                break
            else:
                print(f"  候选失败: {candidate}")
    else:
        chosen_url = url_entry
        print(f"⬇️ 正在下载: {chosen_url}")
        content, last_modified = download_with_retry(chosen_url)

    if content is None:
        print(f"❌ 跳过任务: {latest_name}（所有候选均不可用）")
        continue

    # 保存原始文件到归档（文件名取自 URL）
    original_filename = chosen_url.split('/')[-1]
    archive_path = archive_dir / original_filename
    with open(archive_path, 'wb') as f:
        f.write(content)
    print(f"📁 归档: {archive_path}")

    # 保存重命名文件到 latest
    latest_path = latest_dir / latest_name
    with open(latest_path, 'wb') as f:
        f.write(content)
    print(f"🔄 更新 latest: {latest_path}")

    # 如果是当天的 json（例如 20260816.json），同时另存为 sing-box.json 作为别名
    try:
        if latest_name.endswith('.json') and latest_name == f"{date_compact}.json":
            alias_path = latest_dir / 'sing-box.json'
            with open(alias_path, 'wb') as f:
                f.write(content)
            print(f"🔁 另存为别名: {alias_path}")
    except Exception:
        pass

    # 格式化并记录时间（优先使用 Last-Modified，若无则使用当前时间）
    if last_modified:
        try:
            fmt = last_modified.strftime('%Y-%m-%d %H:%M:%S %z')
            # 将 +0800 转为 +08:00
            if len(fmt) >= 5 and (fmt.endswith('+0000') is False):
                fmt = fmt[:-5] + fmt[-5:-2] + ':' + fmt[-2:]
        except Exception:
            fmt = None
    else:
        tz8 = timezone(timedelta(hours=8))
        now8 = datetime.now(tz8)
        fmt = now8.strftime('%Y-%m-%d %H:%M:%S %z')
        fmt = fmt[:-5] + fmt[-5:-2] + ':' + fmt[-2:]

    if fmt:
        timestamps[latest_name] = fmt

# ---------- 生成 README.txt ----------
readme_path = Path("README.txt")
base_url = "https://raw.githubusercontent.com/tuiseliunian/free-gfw/main/latest/"
link_lines = []

for file_path in sorted(latest_dir.glob("*")):
    if file_path.is_file():
        size = file_path.stat().st_size
        size_str = human_readable_size(size)
        ts = timestamps.get(file_path.name)
        if ts:
            link_lines.append(f"{base_url}{file_path.name}?ts={ts}  ({size_str})")
        else:
            link_lines.append(f"{base_url}{file_path.name}  ({size_str})")

with open(readme_path, 'w', encoding='utf-8') as f:
    f.write("\n".join(link_lines))

print(f"✅ 已生成 {readme_path}，共 {len(link_lines)} 个链接")