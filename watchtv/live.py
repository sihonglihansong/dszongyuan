import requests
import re
import os
# ========== 填写源的地址 ==========
URL_LIST = [
    "https://raw.githubusercontent.com/lihansong888/DSZBYS/refs/heads/main/watchtv/live.m3u8",
    # ========== 2026.10.19以下OK ==========
    "https://raw.githubusercontent.com/lihansong888/DSZBHY/refs/heads/main/watchtv/huya.m3u8",
    # ========== 2026.10.19以下OK ==========
    "https://raw.githubusercontent.com/lihansong888/DSZBDFT/refs/heads/main/watchtv/live.m3u8",
    # ========== 2026.10.19以下OK ==========
    "https://raw.githubusercontent.com/lihansong888/DSZBSZPD/refs/heads/main/watchtv/live.m3u8",
    # ========== 2026.10.19以下OK-handdong ==========
    "https://raw.githubusercontent.com/lihansong888/DSZBxinfengyun/refs/heads/main/HS.m3u",
    "https://raw.githubusercontent.com/lihansong888/DSZBxianggangtaiwan/refs/heads/main/watchtv/live.m3u8",
    
    "https://raw.githubusercontent.com/lihansong888/DSZByangwei/refs/heads/main/watchtv/live.m3u8",
    # ========== 2026.10.19以下OK ==========
    "https://raw.githubusercontent.com/lihansong888/DSZBDSJ/refs/heads/main/watchtv/live.m3u8",
    # ========== 2026.10.19以下OK ==========
    "https://raw.githubusercontent.com/lihansong888/DSZBHY/refs/heads/main/watchtv/douyu.m3u8",
    # ========== 2026.10.19以下OK ==========
    "https://raw.githubusercontent.com/lihansong888/DSZBHY/refs/heads/main/watchtv/yy.m3u8",
    # ========== 2026.10.18以下OK ==========
    "https://raw.githubusercontent.com/lihansong888/DSZBKULAOER/refs/heads/main/watchtv/live.m3u8",
    "https://raw.githubusercontent.com/lihansong888/DSZBZONGYUAN/refs/heads/main/watchtv/daili.txt",
    # ========== 2026.10.18以下OK ==========
    "https://raw.githubusercontent.com/lihansong888/DSZBYANGWEITWO/refs/heads/main/watchtv/live.m3u8",
    "https://raw.githubusercontent.com/lihansong888/DSZBMIGU/refs/heads/main/watchtv/live.m3u8",
    "https://raw.githubusercontent.com/lihansong888/DSZBZUBOYUAN/refs/heads/main/watchtv/live.m3u8",
    
    
    
]
# ========== 分组映射：左边是源里的分组名，右边是输出时改后的分组名 ==========
GROUP_MAP = {
    "HSali云": "HSali云央卫",
    "HS咪咕央卫直播": "HS咪咕央卫直播",
    "咪咕视频": "HS咪咕央卫直播",
    "HS咪咕": "HSali云央卫",
    
    "hansong央视频道": "HS央视频道",
    "lihansong央视备用": "HS央视频道",
    
    "HS央视频道": "HS央视频道",
    "SH央视频道": "HS央视频道",
    "HS卫视频道": "HS卫视频道",
    "SH卫视频道": "HS卫视频道",
    "hansong卫视频道": "HS卫视频道",
    "HS央卫IPTV": "HS央卫IPTV",
    "Free-TV/IPTV": "HS央卫IPTV",
    "IPTV组播源": "HSIPTV组播",
    "Z视介": "HS-Z视介",
    "咪-世-界": "HS-咪世界",
    "咪咕央卫": "HS咪咕央卫直播",
    "hansong-央卫直播": "HS央卫直播",
    "lihansong央卫": "HS央卫直播",
    "lihansong央卫备用": "HS央卫直播",
    "hansong国内地方": "HS国内地方",
    "地方频道": "HS国内地方",
    "地方台": "HS国内地方",
    "HS風雲港澳臺頻道": "HS風雲港澳臺頻道",
    "风云极速频道": "HS風雲港澳臺頻道",
    "4gtv直播": "HS4gtv港台直播",
    "HS极速代理": "HS港台极速代理",
    "hansong-音乐直播": "HS音乐直播",
    "hansong数字频道": "HS数字频道",
    "HS数字频道": "HS数字频道",
    "HS数字频道二线": "HS数字频道二线",
    "HS短剧直播": "HS短剧直播",
    "港澳台电视直播频道": "HS港澳台直播频道",
    "港澳台": "HS港澳台直播频道",
    
    "HS休闲频道": "HS休闲频道",
    "HS电影直播频道": "HS电影直播频道",
    "HS爱奇艺直播频道": "HS爱奇艺直播频道",
    "HS爱奇艺频道": "HS爱奇艺直播频道",
    "HS音乐直播": "HS音乐直播频道",
    "hansong虎牙原创": "HS虎牙原创",
    "hansong虎牙一起看": "HS虎牙一起看",
    "hansong斗鱼原创": "HS斗鱼原创",
    "hansong斗鱼一起看": "HS斗鱼一起看",
    "hansongYY一起看": "HS-YY一起看",
    "HS纪录片直播": "HS纪录片直播",
    
    
}
# ========== 说明：原存活检测已停用 ==========
# GitHub Actions 服务器在美国，访问国内直播源超时/抖动严重，
# 5 秒阈值会把大量国内可用源误杀（如 221.226.xxx 等国内 IP 源）。
# 存活筛选全部交给宝塔端（国内、100并发、5秒阈值、一天2次），
# 本仓库只负责：拉取12个子仓库 -> 分组映射 -> 合并去重 -> 输出全量 live.m3u8。

def parse_any(text: str):
    res = []
    extinf_line = None
    current_group = None
    for raw_line in text.splitlines():
        ln = raw_line.strip()
        if not ln:
            continue
        if ln.startswith("#EXTINF:"):
            extinf_line = ln
            continue
        if extinf_line is not None and not ln.startswith("#"):
            res.append((extinf_line, ln))
            extinf_line = None
            continue
        if ',' in ln and not ln.startswith("#"):
            sp = ln.split(',',1)
            name_part = sp[0].strip()
            url_part = sp[1].strip()
            if url_part == "#genre#":
                current_group = name_part
                continue
            if current_group:
                fake_ext = f'#EXTINF:-1 group-title="{current_group}",{name_part}'
            else:
                fake_ext = f'#EXTINF:-1,{name_part}'
            res.append((fake_ext, url_part))
    return res

def get_channel_name(extinf):
    if "," in extinf:
        return extinf.split(",")[-1].strip()
    return ""

def get_group_title(extinf):
    m = re.search(r'group-title="([^"]+)"', extinf)
    if m:
        return m.group(1).strip()
    return ""

def main():
    # 用改后的分组名初始化空列表
    group_bucket = {v: [] for v in GROUP_MAP.values()}
    seen = set()
    all_candidate = []
    # ========= 拉取、解析、分组过滤、去重逻辑 =========
    for url in URL_LIST:
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            channels = parse_any(resp.text)
            for extinf, play_url in channels:
                ch_name = get_channel_name(extinf)
                ch_group = get_group_title(extinf)
                # 只保留 GROUP_MAP 里有的分组，其他全屏蔽
                if ch_group not in GROUP_MAP:
                    continue
                # 关键：查映射表，把源分组名改成输出分组名
                output_group = GROUP_MAP[ch_group]
                item_key = (ch_name, play_url)
                if item_key not in seen:
                    seen.add(item_key)
                    all_candidate.append((output_group, ch_name, play_url))
        except Exception as e:
            print(f"⚠️ 拉取 {url} 失败：{e}")

    # ========== 存活检测已停用：全部源直接输出，筛选交给宝塔端 ==========
    valid_items = all_candidate
    print(f"\n🔍 跳过存活检测（Actions 在美国测国内源不准），本次输出全量：{len(all_candidate)} 个频道")

    # 把频道回填分组桶
    for gname, cname, curl in valid_items:
        group_bucket[gname].append((cname, curl))

    total_cnt = sum(len(v) for v in group_bucket.values())
    print(f"✅筛选结束，共提取 {total_cnt} 个频道")
    for gname, ch_list in group_bucket.items():
        print(f"  - {gname}: {len(ch_list)} 个频道")
    out_dir = os.path.dirname(os.path.abspath(__file__))
    output_m3u = ["#EXTM3U"]
    for gname, ch_list in group_bucket.items():
        for cname, curl in ch_list:
            # 输出时用改后的分组名
            fake_ext = f'#EXTINF:-1 group-title="{gname}",{cname}'
            output_m3u.append(fake_ext)
            output_m3u.append(curl)
    m3u8_path = os.path.join(out_dir, "live.m3u8")
    with open(m3u8_path, "w", encoding="utf-8") as f:
        f.write("\n".join(output_m3u))
    print(f"✅已输出 m3u8：{m3u8_path}")

if __name__ == "__main__":
    main()
