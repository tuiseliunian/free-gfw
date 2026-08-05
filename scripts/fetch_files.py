import os
import requests
from datetime import datetime
from pathlib import Path

# 生成日期字符串
today = datetime.now()
date_path = today.strftime("%Y/%m/%d")      # 用于 URL 中的路径，如 2026/08/03
date_compact = today.strftime("%Y%m%d")     # 用于文件名，如 20260803
date_dir = today.strftime("%Y-%m-%d")       # 用于归档目录名，如 2026-08-03

# 创建目录
latest_dir = Path("latest")
latest_dir.mkdir(exist_ok=True)

archive_dir = Path("archive") / date_dir
archive_dir.mkdir(parents=True, exist_ok=True)

# 定义下载任务：(URL, latest目标文件名)
tasks = []

# ------ 第一批：clash-v2ray-free.github.io ------
for idx in range(5):
    url = f"https://clash-v2ray-free.github.io/uploads/{date_path}/{idx}-{date_compact}.yaml"
    tasks.append((url, f"clash{idx}.yaml"))

for idx in range(5):
    url = f"https://clash-v2ray-free.github.io/uploads/{date_path}/{idx}-{date_compact}.txt"
    tasks.append((url, f"v2ray{idx}.txt"))

url_json = f"https://clash-v2ray-free.github.io/uploads/{date_path}/{date_compact}.json"
tasks.append((url_json, f"{date_compact}.json"))

# ------ 第二批：freenode.yoyapai.com ------
url_clash100 = f"https://freenode.yoyapai.com/{date_path}-yoyapai.com-clash-vpn-mian-feijiedian.yaml"
tasks.append((url_clash100, "clash100.yaml"))

url_v2ray100 = f"https://freenode.yoyapai.com/{date_path}-yoyapai.com-ssrv2ray-vpn-mian-feijiedian.txt"
tasks.append((url_v2ray100, "v2ray100.yaml"))

# -------------------------------------------------
# 执行下载（每个任务独立，互不影响）
# -------------------------------------------------
for url, latest_name in tasks:
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code != 200:
            print(f"❌ {url} -> HTTP {resp.status_code} (跳过)")
            continue

        content = resp.content

        # 1. 保存原始文件到归档目录（文件名从 URL 提取）
        original_filename = url.split('/')[-1]
        archive_path = archive_dir / original_filename
        with open(archive_path, 'wb') as f:
            f.write(content)
        print(f"📁 归档: {archive_path}")

        # 2. 保存重命名文件到 latest 目录
        latest_path = latest_dir / latest_name
        with open(latest_path, 'wb') as f:
            f.write(content)
        print(f"🔄 更新 latest: {latest_path}")

    except Exception as e:
        print(f"⚠️ 下载失败 {url} : {e} (继续下一个)")