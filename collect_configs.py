import requests
import base64
import re
import os

GITHUB_API = "https://api.github.com"
HEADERS = {"Accept": "application/vnd.github.v3+json"}

if os.environ.get("GITHUB_TOKEN"):
    HEADERS["Authorization"] = f"token {os.environ['GITHUB_TOKEN']}"

REPOS = [
    ("kort0881", "vpn-checker-backend", "checked"),
    ("kort0881", "vpn-vless-configs-russia", "githubmirror"),
]

PROTOCOLS = ("vmess://", "vless://", "trojan://", "ss://", "hy2://", "tuic://")

def get_files_recursive(owner, repo, path):
    url = f"{GITHUB_API}/repos/{owner}/{repo}/contents/{path}"
    resp = requests.get(url, headers=HEADERS, timeout=15)
    if resp.status_code != 200:
        return []
    items = resp.json()
    files = []
    for item in items:
        if item["type"] == "file":
            files.append(item["download_url"])
        elif item["type"] == "dir":
            files.extend(get_files_recursive(owner, repo, item["path"]))
    return files

def extract_configs(text):
    configs = []
    try:
        decoded = base64.b64decode(text + "==").decode("utf-8", errors="ignore")
        if any(p in decoded for p in PROTOCOLS):
            text = decoded
    except:
        pass
    for line in text.splitlines():
        line = line.strip()
        if any(line.startswith(p) for p in PROTOCOLS):
            configs.append(line)
    return configs

def main():
    all_configs = []
    for owner, repo, path in REPOS:
        files = get_files_recursive(owner, repo, path)
        for file_url in files:
            try:
                resp = requests.get(file_url, timeout=10)
                if resp.status_code == 200:
                    configs = extract_configs(resp.text)
                    all_configs.extend(configs)
            except:
                pass
    all_configs = list(dict.fromkeys(all_configs))
    combined = "\n".join(all_configs)
    encoded = base64.b64encode(combined.encode("utf-8")).decode("utf-8")
    with open("configs.txt", "w") as f:
        f.write(encoded)

if __name__ == "__main__":
    main()
