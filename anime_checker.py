import aiohttp

JIKAN_BASE = "https://api.jikan.moe/v4"

async def search_anime(query: str):
    """ค้นหาอนิเมะ คืนค่า list ของผลลัพธ์"""
    async with aiohttp.ClientSession() as session:
        url = f"{JIKAN_BASE}/anime?q={query}&limit=5&type=tv&status=airing"
        async with session.get(url) as resp:
            if resp.status != 200:
                return []
            data = await resp.json()
            return data.get("data", [])

async def get_latest_episode(anime_id: int):
    """ดึงตอนล่าสุดของอนิเมะ"""
    async with aiohttp.ClientSession() as session:
        url = f"{JIKAN_BASE}/anime/{anime_id}"
        async with session.get(url) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            anime = data.get("data", {})
            return {
                "title": anime.get("title"),
                "title_thai": anime.get("title_thai"),
                "episode_count": anime.get("episodes"),
                "airing_episode": anime.get("aired", {}).get("to"),
                "image": anime.get("images", {}).get("jpg", {}).get("large_image_url"),
                "url": anime.get("url"),
                "score": anime.get("score"),
            }

async def get_airing_episodes(anime_id: int):
    """ดึงข้อมูล episodes ล่าสุด"""
    async with aiohttp.ClientSession() as session:
        url = f"{JIKAN_BASE}/anime/{anime_id}/episodes"
        async with session.get(url) as resp:
            if resp.status != 200:
                return None, None
            data = await resp.json()
            episodes = data.get("data", [])
            if not episodes:
                return None, None
            latest = max(episodes, key=lambda e: e.get("mal_id", 0))
            return latest.get("mal_id"), latest.get("title")
        
async def get_seasonal_anime(limit: int = 20):
    """ดึงอนิเมะที่กำลังออกอากาศ season นี้"""
    async with aiohttp.ClientSession() as session:
        url = f"{JIKAN_BASE}/seasons/now?limit={limit}"
        async with session.get(url) as resp:
            if resp.status != 200:
                return []
            data = await resp.json()
            return data.get("data", [])
        
async def get_episode_list(anime_id: int):
    """ดึงรายการตอนทั้งหมดของอนิเมะ"""
    async with aiohttp.ClientSession() as session:
        url = f"{JIKAN_BASE}/anime/{anime_id}/episodes"
        async with session.get(url) as resp:
            if resp.status != 200:
                return None, []
            data = await resp.json()
            episodes = data.get("data", [])

        # ดึงข้อมูลชื่อเรื่องด้วย
        info_url = f"{JIKAN_BASE}/anime/{anime_id}"
        async with session.get(info_url) as resp:
            if resp.status != 200:
                return None, episodes
            info = await resp.json()
            anime_info = info.get("data", {})

    return anime_info, episodes