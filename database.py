import json
import os

DB_FILE = "subscriptions.json"

def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if not content:
            return {}
        return json.loads(content)

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def subscribe(guild_id: str, channel_id: str, anime_id: int, anime_title: str):
    db = load_db()
    key = f"{guild_id}:{anime_id}"
    db[key] = {
        "guild_id": guild_id,
        "channel_id": channel_id,
        "anime_id": anime_id,
        "anime_title": anime_title,
        "last_episode": None
    }
    save_db(db)

def unsubscribe(guild_id: str, anime_id: int):
    db = load_db()
    key = f"{guild_id}:{anime_id}"
    if key in db:
        del db[key]
        save_db(db)
        return True
    return False

def update_last_episode(guild_id: str, anime_id: int, episode: int):
    db = load_db()
    key = f"{guild_id}:{anime_id}"
    if key in db:
        db[key]["last_episode"] = episode
        save_db(db)

def set_offset(guild_id: str, anime_id: int, offset_minutes: int):
    db = load_db()
    key = f"{guild_id}:{anime_id}"
    if key in db:
        db[key]["offset_minutes"] = offset_minutes
        save_db(db)
        return True
    return False

def get_offset(guild_id: str, anime_id: int) -> int:
    db = load_db()
    key = f"{guild_id}:{anime_id}"
    return db.get(key, {}).get("offset_minutes", 0)

def get_subscriptions():
    return list(load_db().values())

def get_guild_subscriptions(guild_id: str):
    db = load_db()
    return [v for k, v in db.items() if k.startswith(f"{guild_id}:")]