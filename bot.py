import json, os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils import executor
from datetime import datetime

API_TOKEN = '7662511174:AAGTLAe3W5gxsqsZaKlE-xPWBIuSFkQ-ing'
CHANNEL_ID = -1002288001129  # Channel for orders
GROUP_ID = -1002378707943    # Verification group
CHANNEL_USERNAME = 'https://t.me/Starz_mine_bot'
ADMIN_IDS = [6417166594]      # Replace with your Telegram user ID(s)

bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

# Load users
if os.path.exists("users.json"):
    with open("users.json", "r") as f:
        users = json.load(f)
else:
    users = {}

def save_users():
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add("⭐ My Balance", "👥 Referrals")
main_menu.add("📈 Leaderboard", "🔗 My Referral Link")
main_menu.add("🎁 Redeem Gifts", "🎉 Daily Reward")
main_menu.add("🧠 Help")

gift_list = [
    {"name": "Pink Heart", "emoji": "💝", "cost": 15},
    {"name": "Teddy Bear", "emoji": "🧸", "cost": 15},
    {"name": "Gift Box", "emoji": "🎁", "cost": 25},
    {"name": "Red Rose", "emoji": "🌹", "cost": 25},
    {"name": "Birthday Cake", "emoji": "🎂", "cost": 50},
    {"name": "Flowers", "emoji": "💐", "cost": 50},
    {"name": "Rocket", "emoji": "🚀", "cost": 75},
    {"name": "Trophy", "emoji": "🏆", "cost": 75},
    {"name": "Ring", "emoji": "💍", "cost": 100}
]

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = str(message.from_user.id)
    referral = message.get_args()
    username = message.from_user.username or "N/A"

    try:
        member = await bot.get_chat_member(chat_id=GROUP_ID, user_id=message.from_user.id)
        if member.status in ['left', 'kicked']:
            raise Exception()
    except:
        join_keyboard = InlineKeyboardMarkup()
        join_keyboard.add(InlineKeyboardButton("🔗 Join Group", url="https://t.me/Cctip_Task_Group"))
        join_keyboard.add(InlineKeyboardButton("✅ I've Joined", callback_data="check_join"))
        await message.answer("🚫 Please join our group to use the bot.", reply_markup=join_keyboard)
        return

    if user_id not in users:
        users[user_id] = {
            "stars": 0,
            "referrals": [],
            "referred_by": None,
            "last_daily": "",
        }
        if referral and referral != user_id and referral in users:
            if user_id not in users[referral]["referrals"]:
                users[referral]["referrals"].append(user_id)
                users[referral]["stars"] += 1
                users[user_id]["referred_by"] = referral
    save_users()
    await message.answer("🌟 Welcome to <b>Starz Mine</b>!\nEarn Stars, Get Gifts 💫", reply_markup=main_menu)

@dp.callback_query_handler(lambda c: c.data == 'check_join')
async def check_join(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    try:
        member = await bot.get_chat_member(chat_id=GROUP_ID, user_id=user_id)
        if member.status in ['left', 'kicked']:
            raise Exception()
        await bot.send_message(user_id, "You're verified!", reply_markup=main_menu)
    except:
        await callback_query.answer("❌ Please join the group first.", show_alert=True)

@dp.message_handler(lambda m: m.text == "⭐ My Balance")
async def show_balance(message: types.Message):
    user_id = str(message.from_user.id)
    stars = users.get(user_id, {}).get("stars", 0)
    await message.answer(f"⭐ You have <b>{stars}</b> stars.")

@dp.message_handler(lambda m: m.text == "👥 Referrals")
async def show_referrals(message: types.Message):
    user_id = str(message.from_user.id)
    count = len(users.get(user_id, {}).get("referrals", []))
    await message.answer(f"👥 Total referrals: <b>{count}</b>")

@dp.message_handler(lambda m: m.text == "📈 Leaderboard")
async def leaderboard(message: types.Message):
    top = sorted(users.items(), key=lambda x: x[1].get("stars", 0), reverse=True)[:10]
    msg = "<b>🏆 Top 10 Users</b>\n"
    for i, (uid, data) in enumerate(top, 1):
        msg += f"{i}. <code>{uid}</code> – {data['stars']}⭐\n"
    await message.answer(msg)

@dp.message_handler(lambda m: m.text == "🔗 My Referral Link")
async def referral_link(message: types.Message):
    bot_user = await bot.get_me()
    uid = message.from_user.id
    link = f"https://t.me/{bot_user.username}?start={uid}"
    await message.answer(f"🔗 Share this link to earn stars:\n{link}")

@dp.message_handler(lambda m: m.text == "🎉 Daily Reward")
async def daily_reward(message: types.Message):
    user_id = str(message.from_user.id)
    today = str(datetime.utcnow().date())
    if users[user_id]["last_daily"] == today:
        await message.answer("🕒 You already claimed your reward today.")
    else:
        users[user_id]["last_daily"] = today
        users[user_id]["stars"] += 2
        save_users()
        await message.answer("🎉 You received <b>2⭐</b> daily reward!")

@dp.message_handler(lambda m: m.text == "🎁 Redeem Gifts")
async def redeem_gifts(message: types.Message):
    kb = InlineKeyboardMarkup(row_width=2)
    for g in gift_list:
        kb.insert(InlineKeyboardButton(f"{g['emoji']} {g['name']} – {g['cost']}⭐", callback_data=f"redeem:{g['name']}"))
    await message.answer("🎁 Choose a gift to redeem:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("redeem:"))
async def redeem_gift(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    username = callback.from_user.username or "N/A"
    gift_name = callback.data.split(":")[1]
    gift = next((g for g in gift_list if g["name"] == gift_name), None)

    if not gift:
        return await callback.answer("Invalid gift.")

    if users[user_id]["stars"] < gift["cost"]:
        return await callback.answer("Not enough stars.")

    users[user_id]["stars"] -= gift["cost"]
    save_users()

    msg = await bot.send_message(
        CHANNEL_ID,
        f"🎁 <b>Gift Redemption</b>\n👤 @{username} (ID: <code>{user_id}</code>)\n"
        f"Gift: {gift['emoji']} {gift['name']} – {gift['cost']}⭐\n\n"
        f"Status: <b>Pending</b>",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("✅ Approve", callback_data=f"approve:{user_id}:{gift_name}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject:{user_id}:{gift_name}")
        )
    )

    await callback.message.answer(
        f"{gift['emoji']} You redeemed <b>{gift['name']}</b> for {gift['cost']}⭐.\n\n"
        f"📢 You can track your order: {CHANNEL_USERNAME}"
    )

@dp.callback_query_handler(lambda c: c.data.startswith("approve:") or c.data.startswith("reject:"))
async def handle_admin_action(callback: CallbackQuery):
    action, uid, gift_name = callback.data.split(":")
    username = (await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=int(uid))).user.username
    status = "✅ Approved" if action == "approve" else "❌ Rejected"
    await bot.send_message(uid, f"{status} – Your order for {gift_name} has been {status.lower()}.")
    await callback.message.edit_text(callback.message.text.replace("Pending", status.replace("✅ ", "").replace("❌ ", "")))

@dp.message_handler(lambda m: m.text == "🧠 Help")
async def help_menu(message: types.Message):
    await message.answer("ℹ️ Use the menu to check your stars, refer friends, redeem gifts, and more!")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
