from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import requests
import asyncio  # Make sure this is imported at the top
import time
import aiohttp
import random
import string


API_TOKEN = '7212402737:AAEErA5IujNL__6TWYytdv7gB8uEoPTiIow'
bot = Bot(token=API_TOKEN, parse_mode='HTML')
dp = Dispatcher(bot)

mongo_url = "mongodb+srv://hamzann:hamza00@cluster0.id2lo.mongodb.net/?retryWrites=true&w=majority"
mongo = AsyncIOMotorClient(mongo_url)
db = mongo["fflikes"]
users = db["users"]

# Replace with your actual admin Telegram user IDs
ADMIN_IDS = [7387793694]  # ← Replace with your Telegram ID
ALLOWED_GROUP_ID = -1002602441954
GROUP_LINK = 'https://t.me/FFLikesGC'
CHANNEL_ID = '@Drsudo'
DEV_USERNAME = '@metaui'

# UPI Premium Message
message_content =  '''👋 <b>Hey {first}\n
🎖️ <u>Available Plans</u>:</b>\n
<blockquote expandable><i>● 30 rs For 7 Days Prime Membership\n
● 110 rs For 1 Month Prime Membership\n
● 299 rs For 3 Months Prime Membership\n
● 550 rs For 6 Months Prime Membership\n
● 999 rs For 1 Year Prime Membership</i></blockquote>\n
💵 UPI ID - <code>trustable@upi</code>
<b>(Tap to copy UPI Id)</b>\n\n
♻️ <b>If payment is not getting sent on above given QR code then inform Admin, He will give you new QR code</b>\n
‼️ ᴍᴜsᴛ sᴇɴᴅ sᴄʀᴇᴇɴsʜᴏᴛ ᴀғᴛᴇʀ ᴘᴀʏᴍᴇɴᴛ'''

# Keyboards
def vip_keyboard():
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton("💎 Buy Premium", callback_data="premium")
    )

def join_keyboard():
    return InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton("🔥 Join Channel", url="t.me/pythonbotz"),
        InlineKeyboardButton("👨‍💻 Developer", url=f"https://t.me/{DEV_USERNAME[1:]}")
    )

def channel_button():
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton(" Join Channel", url=f"https://t.me/{CHANNEL_ID[1:]}")
    )

# DB functions
async def get_prop(key):
    doc = await users.find_one({"_id": key})
    return doc["value"] if doc else None

async def set_prop(key, value):
    await users.update_one({"_id": key}, {"$set": {"value": value}}, upsert=True)

# /start
@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    if message.text.startswith('/start verify_'):
        await verify_token(message)
        return      
    btn = InlineKeyboardMarkup().add(
        InlineKeyboardButton("🔥 Join Group", url=GROUP_LINK),
        InlineKeyboardButton("👨‍💻 Developer", url=f"https://t.me/{DEV_USERNAME[1:]}")
    )
    await message.reply(
        "<b>🎮 Welcome to Free Fire Likes Bot!</b>\n\n🚀 Boost your UID with likes!\n\nType:\n<code>/like 1234567890</code>",
        reply_markup=btn
    )

# /like command
@dp.message_handler(commands=['like'])
async def like_cmd(message: types.Message):
    if message.chat.id != ALLOWED_GROUP_ID:
        return await message.reply(
            f"⛔ <b>This feature is available only in our group.</b>\n<a href='{GROUP_LINK}'>Join to use</a>",
            disable_web_page_preview=True
        )

    try:
        member = await bot.get_chat_member(CHANNEL_ID, message.from_user.id)
        if member.status in ['left', 'kicked']:
            return await message.reply(
                f"⚠️ <b>You must join our channel first!</b>\n<a href='https://t.me/{CHANNEL_ID[1:]}'>Join now</a>",
                reply_markup=channel_button()
            )
    except:
        return await message.reply(
            f"❌ <b>Can't verify your channel join status.</b>\nJoin manually: <a href='https://t.me/{CHANNEL_ID[1:]}'>Click</a>",
            reply_markup=channel_button()
        )

    args = message.text.strip().split()
    if len(args) != 2 or not args[1].isdigit():
        return await message.reply("<b>⚠ Invalid format!</b>\nUse like this:\n<code>/like 1234567890</code>")

    uid = args[1]
    user_id = message.from_user.id
    now = int(time.time() * 1000)

    like_count = await get_prop(f"like_count_{user_id}") or 0
    token_data = await get_prop(f"token_{user_id}")
    premium = await get_prop(f"premium_{user_id}")

    has_access = (
        (token_data and now - token_data["created"] < 6 * 60 * 60 * 1000) or
        (premium and now < premium["until"])
    )

    if like_count >= 3 and not has_access:
        token = str(time.time()).replace('.', '')[-10:]
        await set_prop(f"token_{user_id}", {"token": token, "created": now})
        verify_url = f"https://t.me/fflikes_Robot?start=verify_{user_id}_{token}"

        # 🔁 Random 6-character alias like "likes_a1b2c3"
    random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    alias = f"likes_{random_part}"

    try:
        res = requests.get(
            f"https://arolinks.com/api?api=5ba1b9f950d09e04c0ff351012dacbbc2472641d"
            f"&url={verify_url}&alias={alias}"
        )
            short = res.json().get("shortenedUrl") or verify_url
        except:
            short = verify_url

        return await message.reply(
    "🚫 <b>Your free like limit has been reached!</b>\n\n"
    "🔓 You can unlock 6 hours of free access by completing a simple verification.\n\n"
    "💎 Or upgrade to Premium for unlimited access and faster delivery.\n\n"
    "👇 Choose an option below:",
    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("🔓 Unlock Free Access", url=short)],
        [InlineKeyboardButton("💎 Buy Premium", callback_data="premium"),
        InlineKeyboardButton("ℹ️ Tutorial", url="https://t.me/ChipsTutorial/8")]
    ])
)

    if not has_access:
        await set_prop(f"like_count_{user_id}", like_count + 1)

    wait = await message.reply("⏳ <b>Sending likes...</b>")
    try:
        r = requests.get(f"https://anish-likes.vercel.app/like?server_name=ind&uid={uid}&key=jex4rrr")
        data = r.json()
        region = data.get("Region", "India")

        if data.get("status") == 2:
            return await wait.edit_text(
                f"🚫 Max Likes Reached for Today\n\n"
                f"👤 Name: {data.get('PlayerNickname', 'N/A')}\n"
                f"🆔 UID: {uid}\n"
                f"🌍 Region: India\n"
                f"❤️ Current Likes: {data.get('LikesNow', 'N/A')}",
                reply_markup=vip_keyboard()
            )

        await wait.edit_text(
            f"✅ Likes Sent Successfully!\n\n"
            f"👤 Name: {data.get('PlayerNickname', 'N/A')}\n"
            f"🆔 UID: {uid}\n"
            f"❤️ Before Likes: {data.get('LikesbeforeCommand', 'N/A')}\n"
            f"👍 Current Likes: {data.get('LikesafterCommand', 'N/A')}\n"
            f"🎯 Likes Sent By Bot: {data.get('LikesGivenByAPI', 'N/A')}",
            reply_markup=join_keyboard()
        )

    except Exception as e:
        await wait.edit_text(f"❌ Failed to send likes.\n<i>{e}</i>")


# /verify (via /start verify_)
async def verify_token(message: types.Message):
    parts = message.text.split("_")
    if len(parts) != 3:
        return await message.reply("❌ Invalid verify link.")
    user_id, token = parts[1], parts[2]
    token_data = await get_prop(f"token_{user_id}")
    if token_data and token_data["token"] == token:
        await set_prop(f"verified_{int(user_id)}", int(time.time() * 1000))
        return await message.reply("✅ <b>Access Unlocked!</b>\n\nYou now have unlimited likes for 6 hours.")
    else:
        return await message.reply("❌ Invalid or expired token.")


# ✅ /get Command — Simple Format: /get 8431487083
@dp.message_handler(commands=["get"])
async def get_player_info(message: types.Message):
    args = message.text.split()
    if len(args) != 2 or not args[1].isdigit():
        return await message.reply("❌ Invalid format.\n✅ Use: <code>/get 8431487083</code>")

    uid = args[1]
    region = "ind"
    processing = await message.reply("⏳ Fetching player details... Please wait...")
    await asyncio.sleep(2)

    url = f"https://fred-fire-info-gj.vercel.app/player-info?uid={uid}&region={region}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                data = await r.json()

        def unix_to_readable(ts):
            return datetime.fromtimestamp(int(ts) / 1000).strftime('%d-%m-%Y %H:%M:%S') if ts else "N/A"

        b = data.get("basicInfo", {})
        c = data.get("clanBasicInfo", {})
        p = data.get("petInfo", {})
        s = data.get("socialInfo", {})

        text = f"""<blockquote expandable>
<b>📋 Player Info:</b>
├👤 Name: {b.get('nickname', 'N/A')}
├🆔 UID: {b.get('accountId', 'N/A')}
├🌍 Region: {b.get('region', 'N/A')}
├🎮 Level: {b.get('level', 'N/A')}
├🧪 EXP: {int(b.get('exp', 0)):,}
├❤️ Likes: {b.get('liked', 'N/A')}
├🏷️ Title: {b.get('title', 'N/A')}
├🗓️ Created: {unix_to_readable(b.get('createAt', 0))}
└🔓 Last Login: {unix_to_readable(b.get('lastLoginAt', 0))}

<b>🏅 Rank Info:</b>
├🎖️ BR Rank: {b.get('rank', 'N/A')} ({b.get('rankingPoints', 0)} pts)
├🥇 Max BR: {b.get('maxRank', 'N/A')}
├🏆 CS Rank: {b.get('csRank', 'N/A')} ({b.get('csRankingPoints', 0)} pts)
└🥈 Max CS: {b.get('csMaxRank', 'N/A')}

<b>🎫 Extra:</b>
├🎫 Elite Pass: {"Yes ✅" if b.get('hasElitePass') else "No ❌"}
├🎖️ Badges: {b.get('badgeCnt', 0)}
├💎 Diamonds: {data.get('diamondCostRes', {}).get('diamondCost', 'N/A')}
└🛡️ Credit Score: {data.get('creditScoreInfo', {}).get('creditScore', 'N/A')}

<b>🏰 Guild:</b>
├🏷️ Name: {c.get('clanName', 'N/A')}
├👑 Leader: {c.get('captainId', 'N/A')}
├👥 Members: {c.get('memberNum', 0)} / {c.get('capacity', 0)}
└🔢 Level: {c.get('clanLevel', 'N/A')}

<b>🐾 Pet:</b>
├🐶 Name: {p.get('name', 'N/A')}
└🎚️ Level: {p.get('level', 'N/A')}

<b>🧬 Social:</b>
├🚻 Gender: {s.get('gender', 'N/A').replace('Gender_', '')}
├🌐 Language: {s.get('language', 'N/A').replace('Language_', '')}
├⏱️ Online: {s.get('timeOnline', 'N/A').replace('TimeOnline_', '')}
├🕰️ Active: {s.get('timeActive', 'N/A').replace('TimeActive_', '')}
└ 📝 Signature: {s.get('signature', 'N/A').replace('[b][c][i]', '').strip()} </blockquote>
<b>🎗️ BOT DEVLOPER</b>
└👑 @Metaui"""

        btn = InlineKeyboardMarkup().add(
            InlineKeyboardButton("Join Channel", url="https://t.me/PythonBotz")
        )
        await processing.edit_text(text, reply_markup=btn)

    except Exception as e:
        await processing.edit_text(f"❌ Failed to fetch data.\nError: <code>{e}</code>")

        
# Admin: Give Premium Command
@dp.message_handler(commands=['givepremium'])
async def give_premium(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return await message.reply("❌ You are not authorized to use this command.")

    args = message.text.split()
    if len(args) != 3 or not args[1].isdigit() or not args[2].isdigit():
        return await message.reply("⚠️ Format: /givepremium <user_id> <hours>")

    user_id = int(args[1])
    hours = int(args[2])
    expiry = int(time.time() * 1000) + hours * 60 * 60 * 1000

    await set_prop(f"premium_{user_id}", {"until": expiry})
    await message.reply(f"✅ Premium given to <code>{user_id}</code> for {hours} hours.")

# Premium Plans Popup
@dp.callback_query_handler(lambda c: c.data == "premium")
async def buy_premium(query: types.CallbackQuery):
    sent = await query.message.reply_photo(
        photo="https://graph.org/file/ac61481c6c90015545d83-6b573a858fa21d40c6.jpg",
        caption=message_content.format(first=query.from_user.mention),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton("Owner", url="https://t.me/metaui"),
                InlineKeyboardButton("Channel", url="https://t.me/Pythonbotz")
            ],
            [
                InlineKeyboardButton("🔒 Close", callback_data="close")
            ]
        ])
    )

    # 🕒 Wait 60 seconds and auto-delete
    await asyncio.sleep(60)
    try:
        await sent.delete()
    except:
        pass  # Ignore if already deleted manually


# Close inline messages
@dp.callback_query_handler(lambda c: c.data == "close")
async def close_cb(query: types.CallbackQuery):
    await query.message.delete()
    try:
        await query.message.reply_to_message.delete()
    except: pass

if __name__ == '__main__':
    print("✅ Bot deployed successfully!")
    executor.start_polling(dp, skip_updates=True)
  
