import requests
import time
from datetime import datetime
from pathlib import Path

# 伪装请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://node.freeclashnode.com/'
}

def download_with_retry(url, timeout=30, retries=3, delay=5):
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, timeout=timeout, headers=headers)
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

today = datetime.now()
ym_path = today.strftime("%Y/%m")
ymd_path = today.strftime("%Y/%m/%d")
date_compact = today.strftime("%Y%m%d")
date_dir = today.strftime("%Y-%m-%d")

latest_dir = Path("latest")
latest_dir.mkdir(exist_ok=True)

archive_dir = Path("archive") / date_dir
archive_dir.mkdir(parents=True, exist_ok=True)

tasks = []

# 1. node.freeclashnode.com
for idx in range(5):
    tasks.append((f"https://node.freeclashnode.com/uploads/{ym_path}/{idx}-{date_compact}.yaml", f"clash{idx}.yaml"))
    tasks.append((f"https://node.freeclashnode.com/uploads/{ym_path}/{idx}-{date_compact}.txt", f"v2ray{idx}.txt"))
tasks.append((f"https://node.freeclashnode.com/uploads/{ym_path}/{date_compact}.json", f"sing-box.json"))

# 2. freenode.yoyapai.com
tasks.append((f"https://freenode.yoyapai.com/{ymd_path}-yoyapai.com-clash-vpn-mian-feijiedian.yaml", "clash100.yaml"))
tasks.append((f"https://freenode.yoyapai.com/{ymd_path}-yoyapai.com-ssrv2ray-vpn-mian-feijiedian.txt", "v2ray100.txt"))

# 执行下载
for url, latest_name in tasks:
    print(f"⬇️ 正在下载: {url}")
    content = download_with_retry(url)
    if content is None:
        print(f"❌ 跳过 {url}")
        continue

    original_filename = url.split('/')[-1]
    archive_path = archive_dir / original_filename
    with open(archive_path, 'wb') as f:
        f.write(content)
    print(f"📁 归档: {archive_path}")

    latest_path = latest_dir / latest_name
    with open(latest_path, 'wb') as f:
        f.write(content)
    print(f"🔄 更新 latest: {latest_path}")

# ---------- 生成 README.txt ----------
readme_path = Path("README.txt")
base_url = "https://raw.githubusercontent.com/tuiseliunian/free-gfw/main/latest/"
file_links = []
for file_path in sorted(latest_dir.glob("*")):
    if file_path.is_file():
        file_links.append(f"{base_url}/{file_path.name}")

with open(readme_path, 'w', encoding='utf-8') as f:
    f.write("\n".join(file_links))

print(f"✅ 已生成 {readme_path}，共 {len(file_links)} 个链接")