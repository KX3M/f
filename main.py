from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from motor.motor_asyncio import AsyncIOMotorClient
import requests
import asyncio  # Make sure this is imported at the top
import time

API_TOKEN = '7212402737:AAEyhlFTNXm9po5sDlssV8r-z9_Pqyi-mSg'
bot = Bot(token=API_TOKEN, parse_mode='HTML')
dp = Dispatcher(bot)

mongo_url = "mongodb+srv://hamzann:hamza00@cluster0.id2lo.mongodb.net/?retryWrites=true&w=majority"
mongo = AsyncIOMotorClient(mongo_url)
db = mongo["fflikes"]
users = db["users"]

# Replace with your actual admin Telegram user IDs
ADMIN_IDS = [7387793694]  # ← Replace with your Telegram ID
ALLOWED_GROUP_ID = -1002422214461
GROUP_LINK = 'https://t.me/FFLikesGC'
CHANNEL_ID = '@SoulTyped'
DEV_USERNAME = '@metaui'

# UPI Premium Message
message_content = '''👋 <b>Hey {first}</b>

🎖️ <u>Available Plans</u>:
<blockquote expandable>
<i>● ₹30 for 7 Days Prime  
● ₹110 for 1 Month Prime  
● ₹299 for 3 Months Prime  
● ₹550 for 6 Months Prime  
● ₹999 for 1 Year Prime</i>
</blockquote>

💵 <b>UPI ID:</b> <code>trustable@upi</code>  
(Tap to copy)

♻️ <b>If UPI fails, contact Admin for new QR</b>

‼️ <i>Send payment screenshot to confirm</i>
'''

# Keyboards
def vip_keyboard():
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton("💎 Buy Premium", callback_data="premium")
    )

def join_keyboard():
    return InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton("🔥 Join Group", url=GROUP_LINK),
        InlineKeyboardButton("👨‍💻 Developer", url=f"https://t.me/{DEV_USERNAME[1:]}")
    )

def channel_button():
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton("📲 Join Channel", url=f"https://t.me/{CHANNEL_ID[1:]}")
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

        try:
            res = requests.get(f"https://arolinks.com/api?api=5ba1b9f950d09e04c0ff351012dacbbc2472641d&url={verify_url}")
            short = res.json().get("shortenedUrl") or verify_url
        except:
            short = verify_url

        return await message.reply(
            "🚫 <b>Free like limit reached.</b>\nUnlock 6 hours access 👇",
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton("🔓 Unlock Free Access", url=short),
                InlineKeyboardButton("💎 Buy Premium", callback_data="premium")
            )
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
                f"🌍 Region: {region}\n"
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

# Token verify
@dp.message_handler(lambda m: m.text.startswith("/start verify_"))
async def verify_token(message: types.Message):
    parts = message.text.split("_")
    if len(parts) != 3:
        return await message.reply("❌ Invalid token.")
    user_id, token = parts[1], parts[2]
    data = await get_prop(f"token_{user_id}")
    if data and data["token"] == token:
        expiry = int(time.time() * 1000) + 6 * 60 * 60 * 1000
        await set_prop(f"premium_{int(user_id)}", { "until": expiry })
        return await message.reply("✅ Access Granted for 6 Hours.")
    return await message.reply("❌ Invalid or expired token.")

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
  
