import requests
import base64
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
        print(f"Taraniyor: {owner}/{repo}/{path}")
        files = get_files_recursive(owner, repo, path)
        print(f"  {len(files)} dosya bulundu")
        for file_url in files:
            try:
                resp = requests.get(file_url, timeout=10)
                if resp.status_code == 200:
                    configs = extract_configs(resp.text)
                    if configs:
                        all_configs.extend(configs)
            except:
                pass

    # Tekrarlari kaldir
    all_configs = list(dict.fromkeys(all_configs))
    print(f"Toplam benzersiz sunucu: {len(all_configs)}")

    # Tek buyuk dosya (ham)
    combined = "\n".join(all_configs)
    encoded = base64.b64encode(combined.encode("utf-8")).decode("utf-8")
    with open("configs.txt", "w") as f:
        f.write(encoded)
    print(f"configs.txt yazildi ({len(encoded)} byte)")

    # 500'er sunucuya bol (statically icin)
    chunk_size = 500
    chunks = [all_configs[i:i+chunk_size] for i in range(0, len(all_configs), chunk_size)]
    for idx, chunk in enumerate(chunks):
        combined_chunk = "\n".join(chunk)
        encoded_chunk = base64.b64encode(combined_chunk.encode("utf-8")).decode("utf-8")
        filename = f"configs_{idx}.txt"
        with open(filename, "w") as f:
            f.write(encoded_chunk)
        print(f"{filename} yazildi ({len(chunk)} sunucu)")

    print(f"Toplam {len(chunks)} parca olusturuldu.")

if __name__ == "__main__":
    main()
