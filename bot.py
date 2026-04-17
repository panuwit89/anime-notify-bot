import discord
from discord.ext import commands
from discord import app_commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os
from dotenv import load_dotenv
import asyncio

from database import (
    subscribe, unsubscribe, get_subscriptions,
    update_last_episode, get_guild_subscriptions
)
from anime_checker import search_anime, get_latest_episode, get_airing_episodes, get_seasonal_anime, get_episode_list

load_dotenv()

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
scheduler = AsyncIOScheduler()

# ==================== COMMANDS ====================

@bot.tree.command(name="subscribe", description="ติดตามอนิเมะเพื่อรับแจ้งเตือนตอนใหม่")
@app_commands.describe(query="ชื่ออนิเมะที่ต้องการติดตาม")
async def cmd_subscribe(interaction: discord.Interaction, query: str):
    await interaction.response.defer()

    results = await search_anime(query)
    
    if not results:
        await interaction.followup.send("❌ ไม่พบอนิเมะที่ค้นหา ลองใช้ชื่อภาษาอังกฤษดูนะครับ")
        return

    # สร้าง dropdown ให้เลือก
    options = []
    for anime in results[:5]:
        title = anime.get("title", "Unknown")
        anime_id = anime.get("mal_id")
        ep = anime.get("episodes", "?")
        status = anime.get("status", "")
        options.append(discord.SelectOption(
            label=title[:100],
            value=str(anime_id),
            description=f"ตอน: {ep} | {status}"[:100]
        ))

    class AnimeSelect(discord.ui.Select):
        def __init__(self):
            super().__init__(placeholder="เลือกอนิเมะ...", options=options)

        async def callback(self, select_interaction: discord.Interaction):
            anime_id = int(self.values[0])
            selected = next((a for a in results if a["mal_id"] == anime_id), None)
            title = selected["title"] if selected else "Unknown"

            # ดึง episode ล่าสุดเพื่อ set baseline
            ep_num, ep_title = await get_airing_episodes(anime_id)
            subscribe(
                str(interaction.guild_id),
                str(interaction.channel_id),
                anime_id,
                title
            )
            if ep_num:
                update_last_episode(str(interaction.guild_id), anime_id, ep_num)

            embed = discord.Embed(
                title="✅ ติดตามสำเร็จ!",
                description=f"จะแจ้งเตือนเมื่อ **{title}** มีตอนใหม่ในช่อง <#{interaction.channel_id}>",
                color=discord.Color.green()
            )
            if selected and selected.get("images", {}).get("jpg", {}).get("image_url"):
                embed.set_thumbnail(url=selected["images"]["jpg"]["image_url"])

            await select_interaction.response.edit_message(content=None, embed=embed, view=None)

    view = discord.ui.View()
    view.add_item(AnimeSelect())
    await interaction.followup.send("🔍 พบอนิเมะต่อไปนี้ เลือกที่ต้องการติดตาม:", view=view)


@bot.tree.command(name="unsubscribe", description="ยกเลิกการติดตามอนิเมะ")
@app_commands.describe(anime_id="Anime ID (จาก /list)")
async def cmd_unsubscribe(interaction: discord.Interaction, anime_id: int):
    success = unsubscribe(str(interaction.guild_id), anime_id)
    if success:
        await interaction.response.send_message(f"✅ ยกเลิกการติดตาม Anime ID `{anime_id}` แล้ว")
    else:
        await interaction.response.send_message("❌ ไม่พบอนิเมะที่ติดตามอยู่")


@bot.tree.command(name="list", description="ดูรายการอนิเมะที่ติดตามอยู่")
async def cmd_list(interaction: discord.Interaction):
    subs = get_guild_subscriptions(str(interaction.guild_id))
    if not subs:
        await interaction.response.send_message("📋 ยังไม่ได้ติดตามอนิเมะเรื่องใด ใช้ `/subscribe` เพื่อเริ่มต้น")
        return

    embed = discord.Embed(
        title="📺 อนิเมะที่ติดตามอยู่",
        color=discord.Color.blue()
    )
    for sub in subs:
        ep = sub.get("last_episode", "?")
        embed.add_field(
            name=sub["anime_title"],
            value=f"ID: `{sub['anime_id']}` | ตอนล่าสุด: {ep} | Channel: <#{sub['channel_id']}>",
            inline=False
        )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="onair", description="ดูอนิเมะที่กำลังออกอากาศอยู่ตอนนี้")
@app_commands.describe(limit="จำนวนที่ต้องการแสดง (สูงสุด 30, default 20)")
async def cmd_onair(interaction: discord.Interaction, limit: int = 20):
    await interaction.response.defer()

    from anime_checker import get_seasonal_anime
    results = await get_seasonal_anime(min(limit, 30))

    if not results:
        await interaction.followup.send("❌ ดึงข้อมูลไม่ได้ในตอนนี้ ลองใหม่อีกครั้งนะครับ")
        return

    # เรียงตาม score
    results.sort(key=lambda x: x.get("score") or 0, reverse=True)

    embed = discord.Embed(
        title="📺 อนิเมะที่กำลัง On Air อยู่ตอนนี้",
        color=discord.Color.purple()
    )

    for anime in results[:limit]:
        title = anime.get("title", "Unknown")
        anime_id = anime.get("mal_id", "?")
        score = anime.get("score") or "ยังไม่มีคะแนน"
        ep_count = anime.get("episodes") or "?"
        day = anime.get("broadcast", {}).get("day") or "ไม่ระบุ"

        embed.add_field(
            name=title,
            value=f"⭐ {score} | 📅 ออกทุก {day} | 🎬 {ep_count} ตอน | ID: `{anime_id}`",
            inline=False
        )

    embed.set_footer(text="ใช้ /subscribe <ชื่อเรื่อง> เพื่อติดตาม | ใช้ /episodes <id> เพื่อดูตอน")
    await interaction.followup.send(embed=embed)
    
@bot.tree.command(name="episodes", description="ดูว่าอนิเมะออกมากี่ตอนแล้ว")
@app_commands.describe(anime_id="Anime ID จาก /onair หรือ /list")
async def cmd_episodes(interaction: discord.Interaction, anime_id: int):
    await interaction.response.defer()

    from anime_checker import get_episode_list
    anime_info, episodes = await get_episode_list(anime_id)

    if anime_info is None:
        await interaction.followup.send("❌ ไม่พบอนิเมะ ID นี้")
        return

    title = anime_info.get("title", "Unknown")
    total_ep = anime_info.get("episodes") or "ยังไม่ระบุ"
    status = anime_info.get("status", "")
    aired_count = len(episodes)
    image = anime_info.get("images", {}).get("jpg", {}).get("large_image_url")
    url = anime_info.get("url")

    embed = discord.Embed(
        title=f"🎬 {title}",
        url=url,
        color=discord.Color.blue()
    )

    if image:
        embed.set_thumbnail(url=image)

    embed.add_field(name="สถานะ", value=status, inline=True)
    embed.add_field(name="ออกแล้ว", value=f"{aired_count} ตอน", inline=True)
    embed.add_field(name="ทั้งหมด", value=f"{total_ep} ตอน", inline=True)

    # แสดง 5 ตอนล่าสุด
    if episodes:
        recent = episodes[-5:]
        recent_text = "\n".join(
            f"ตอน {ep.get('mal_id')} — {ep.get('title') or 'ไม่มีชื่อ'}"
            for ep in reversed(recent)
        )
        embed.add_field(name="5 ตอนล่าสุด", value=recent_text, inline=False)

    embed.set_footer(text=f"Anime ID: {anime_id} | ใช้ /subscribe เพื่อติดตาม")
    await interaction.followup.send(embed=embed)

# ==================== SCHEDULER ====================

async def check_new_episodes():
    """ตรวจสอบอนิเมะทุกชั่วโมง"""
    print("🔍 กำลังตรวจสอบตอนใหม่...")
    subs = get_subscriptions()

    for sub in subs:
        try:
            anime_id = sub["anime_id"]
            guild_id = sub["guild_id"]
            channel_id = sub["channel_id"]
            last_ep = sub.get("last_episode")

            ep_num, ep_title = await get_airing_episodes(anime_id)
            if not ep_num:
                continue

            # มีตอนใหม่!
            if last_ep is None or ep_num > last_ep:
                update_last_episode(guild_id, anime_id, ep_num)

                channel = bot.get_channel(int(channel_id))
                if not channel:
                    continue

                anime_info = await get_latest_episode(anime_id)
                embed = discord.Embed(
                    title=f"🎬 {sub['anime_title']} — ตอนที่ {ep_num} ออกแล้ว!",
                    description=ep_title or "ตอนใหม่เพิ่งอัปโหลดแล้ว!",
                    color=discord.Color.orange(),
                    url=anime_info.get("url") if anime_info else None
                )
                if anime_info and anime_info.get("image"):
                    embed.set_thumbnail(url=anime_info["image"])
                if anime_info and anime_info.get("score"):
                    embed.add_field(name="⭐ คะแนน MAL", value=anime_info["score"])

                embed.set_footer(text="ข้อมูลจาก MyAnimeList")

                await channel.send("@here", embed=embed)
                print(f"✅ แจ้งเตือน {sub['anime_title']} ตอน {ep_num}")

            await asyncio.sleep(1)  # หน่วงเวลาเพื่อไม่ให้ hit rate limit

        except Exception as e:
            print(f"❌ Error ตรวจสอบ {sub.get('anime_title')}: {e}")


# ==================== EVENTS ====================

@bot.event
async def on_ready():
    print(f"✅ Bot เริ่มทำงาน: {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"📡 Sync {len(synced)} commands แล้ว")
    except Exception as e:
        print(f"❌ Sync error: {e}")

    # เริ่ม scheduler
    scheduler.add_job(check_new_episodes, "interval", hours=1, id="anime_check")
    scheduler.start()
    print("⏰ Scheduler เริ่มทำงาน (ตรวจทุก 1 ชั่วโมง)")


bot.run(os.getenv("DISCORD_TOKEN"))