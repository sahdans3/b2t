from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import Forbidden, BadRequest

from app.database import (
    register_user, set_searching, find_partner,
    stop_chat, get_partner
)
from app.keyboards import feedback_keyboard

PARTNER_FOUND_MESSAGE = (
    "Partner found 😺\n\n"
    "/next — find a new partner\n"
    "/stop — stop this chat\n\n"
    "https://t.me/Annonymous_Chat_Bot"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update.effective_user.id)
    await update.message.reply_text(
        "👋 Welcome!\n\nType /search to find a partner."
    )


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    register_user(user_id)
    set_searching(user_id, 1)

    partner = find_partner(user_id)

    if partner:
        await update.message.reply_text(PARTNER_FOUND_MESSAGE)

        try:
            await context.bot.send_message(
                chat_id=partner["user_id"],
                text=PARTNER_FOUND_MESSAGE
            )
        except Forbidden:
            stop_chat(partner["user_id"])
    else:
        await update.message.reply_text("🔍 Looking for a new partner...")


async def next_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    partner_id = stop_chat(user_id)

    if partner_id:
        try:
            await context.bot.send_message(
                chat_id=partner_id,
                text="Your partner has left the chat 😞"
            )
        except Forbidden:
            pass

    set_searching(user_id, 1)
    await update.message.reply_text("🔍 Looking for a new partner...")

    partner = find_partner(user_id)

    if partner:
        await update.message.reply_text(PARTNER_FOUND_MESSAGE)

        try:
            await context.bot.send_message(
                chat_id=partner["user_id"],
                text=PARTNER_FOUND_MESSAGE
            )
        except Forbidden:
            stop_chat(partner["user_id"])


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    partner_id = stop_chat(user_id)

    if not partner_id:
        await update.message.reply_text("❌ You are not in a chat.")
        return

    try:
        await context.bot.send_message(
            chat_id=partner_id,
            text="😞 Your partner has ended the chat."
        )
    except Forbidden:
        pass

    await update.message.reply_text(
        "Chat ended 😞",
        reply_markup=feedback_keyboard()
    )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    partner_id = get_partner(update.effective_user.id)

    if not partner_id:
        return

    try:
        await context.bot.send_message(
            chat_id=partner_id,
            text=update.message.text
        )
    except Forbidden:
        stop_chat(partner_id)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    try:
        await query.answer()
    except BadRequest:
        return

    await query.edit_message_text("✅ Feedback saved")