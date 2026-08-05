import requests
import time
from datetime import datetime
from pathlib import Path

# 伪装请求头，防止 403
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://node.freeclashnode.com/'
}

def download_with_retry(url, timeout=30, retries=3, delay=5):
    """带重试的下载函数，返回 bytes 或 None"""
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

# 日期格式
today = datetime.now()
ym_path = today.strftime("%Y/%m")          # 例如 2026/08（用于 node 链接）
ymd_path = today.strftime("%Y/%m/%d")      # 例如 2026/08/05（用于 yoyapai 链接）
date_compact = today.strftime("%Y%m%d")    # 例如 20260803
date_dir = today.strftime("%Y-%m-%d")      # 归档目录名

# 创建目录
latest_dir = Path("latest")
latest_dir.mkdir(exist_ok=True)

archive_dir = Path("archive") / date_dir
archive_dir.mkdir(parents=True, exist_ok=True)

# 构建下载任务列表：(URL, 目标文件名)
tasks = []

# ------ 1. node.freeclashnode.com （替代原来的 clash-v2ray-free）------
for idx in range(5):
    tasks.append((f"https://node.freeclashnode.com/uploads/{ym_path}/{idx}-{date_compact}.yaml", f"clash{idx}.yaml"))
    tasks.append((f"https://node.freeclashnode.com/uploads/{ym_path}/{idx}-{date_compact}.txt", f"v2ray{idx}.txt"))
tasks.append((f"https://node.freeclashnode.com/uploads/{ym_path}/{date_compact}.json", f"{date_compact}.json"))

# ------ 2. freenode.yoyapai.com （保持不变）------
tasks.append((f"https://freenode.yoyapai.com/{ymd_path}-yoyapai.com-clash-vpn-mian-feijiedian.yaml", "clash100.yaml"))
tasks.append((f"https://freenode.yoyapai.com/{ymd_path}-yoyapai.com-ssrv2ray-vpn-mian-feijiedian.txt", "v2ray100.txt"))  # 目标改为 .txt

# ------ 执行下载 ------
for url, latest_name in tasks:
    print(f"⬇️ 正在下载: {url}")
    content = download_with_retry(url)
    if content is None:
        print(f"❌ 跳过 {url}")
        continue

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