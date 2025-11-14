import asyncio
import aiohttp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from datetime import datetime

TOKEN = "8498822249:AAF-maWYShYpNMuWJJuguDxf5uvLZhl_Gl4"
CHAT_ID = "7342381562"

active_alerts = {"above": {}, "below": {}}
alert_state = {}  # {price_level: True/False}

async def get_eth_price():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd") as r:
            data = await r.json()
            return float(data["ethereum"]["usd"])

async def send_alert(context: ContextTypes.DEFAULT_TYPE, msg):
    await context.bot.send_message(chat_id=CHAT_ID, text=msg)

async def check_alerts(context: ContextTypes.DEFAULT_TYPE):
    price = await get_eth_price()
    for level, active in list(alert_state.items()):
        if active:
            level = float(level)
            if price >= level and "above" in active_alerts:
                await send_alert(context, f"🚨 ETH/USD above {level}! Current: ${price:.2f}")
            elif price <= level and "below" in active_alerts:
                await send_alert(context, f"🚨 ETH/USD below {level}! Current: ${price:.2f}")

async def above(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        level = float(context.args[0])
        alert_state[level] = True
        active_alerts["above"][level] = True
        await update.message.reply_text(f"✅ ETH/USD alert set: above ${level}")
    except:
        await update.message.reply_text("❌ Usage: /above <price>")

async def below(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        level = float(context.args[0])
        alert_state[level] = True
        active_alerts["below"][level] = True
        await update.message.reply_text(f"✅ ETH/USD alert set: below ${level}")
    except:
        await update.message.reply_text("❌ Usage: /below <price>")

async def deactivate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        level = float(context.args[0])
        if level in alert_state:
            alert_state[level] = False
            await update.message.reply_text(f"🛑 Alert at ${level} deactivated.")
        else:
            await update.message.reply_text("⚠️ No such alert active.")
    except:
        await update.message.reply_text("❌ Usage: /deactivate <price>")

async def active(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not any(alert_state.values()):
        await update.message.reply_text("📭 No active alerts.")
    else:
        actives = [f"${k}" for k, v in alert_state.items() if v]
        await update.message.reply_text("📡 Active alerts:\n" + "\n".join(actives))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 ETH/USD Bot Ready!\nUse /above <price>, /below <price>, /active, /deactivate <price>.")

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("above", above))
    app.add_handler(CommandHandler("below", below))
    app.add_handler(CommandHandler("deactivate", deactivate))
    app.add_handler(CommandHandler("active", active))
    app.job_queue.run_repeating(check_alerts, interval=180, first=5)
    print("Bot started for ETH/USD 🚀")
    await app.run_polling()

if __name__ == "__main__":
    import nest_asyncio
    import asyncio

    nest_asyncio.apply()
    asyncio.get_event_loop().run_until_complete(main())

