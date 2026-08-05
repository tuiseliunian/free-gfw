import requests
from datetime import datetime
from pathlib import Path

today = datetime.now()

# 日期格式
ymd_path = today.strftime("%Y/%m/%d")      # 例如 2026/08/05（用于 yoyapai）
ym_path  = today.strftime("%Y/%m")         # 例如 2026/08（用于 clash）
date_compact = today.strftime("%Y%m%d")    # 例如 20260803（文件名中的日期）
date_dir = today.strftime("%Y-%m-%d")      # 归档目录名，例如 2026-08-05

latest_dir = Path("latest")
latest_dir.mkdir(exist_ok=True)

archive_dir = Path("archive") / date_dir
archive_dir.mkdir(parents=True, exist_ok=True)

tasks = []

# ------ 1. node.freeclashnode.com （路径只有 年/月）------
for idx in range(5):
    url = f"https://node.freeclashnode.com/uploads/{ym_path}/{idx}-{date_compact}.yaml"
    tasks.append((url, f"clash{idx}.yaml"))
    
    url = f"https://node.freeclashnode.com/uploads/{ym_path}/{idx}-{date_compact}.txt"
    tasks.append((url, f"v2ray{idx}.txt"))

url_json = f"https://node.freeclashnode.com/uploads/{ym_path}/{date_compact}.json"
tasks.append((url_json, f"{date_compact}.json"))

# ------ 2. freenode.yoyapai.com （路径包含 年/月/日）------
url_clash100 = f"https://freenode.yoyapai.com/{ymd_path}-yoyapai.com-clash-vpn-mian-feijiedian.yaml"
tasks.append((url_clash100, "clash100.yaml"))

url_v2ray100 = f"https://freenode.yoyapai.com/{ymd_path}-yoyapai.com-ssrv2ray-vpn-mian-feijiedian.txt"
tasks.append((url_v2ray100, "v2ray100.yaml"))

# ------ 执行下载（每个任务独立）------
for url, latest_name in tasks:
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code != 200:
            print(f"❌ {url} -> HTTP {resp.status_code} (跳过)")
            continue
        content = resp.content

        # 保存原始文件到归档（文件名从 URL 提取）
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

    except Exception as e:
        print(f"⚠️ 下载失败 {url} : {e} (继续下一个)")