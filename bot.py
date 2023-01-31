#!/usr/bin/env python

import logging
import requests
from telegram import __version__ as TG_VER
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes
from panel import Panel
from utils import load_config, get_timestamp
import argparse
import datetime
import random

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


async def instructions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="""Download the applications below and import the generated link.
                                                                          <b>Android:</b> V2rayNG
                                                                          <b>IOS:</b> NapsternetV, shadowrocket
                                                                          <b>Windows:</b> v2rayN
                                                                          <b>MacOS:</b> V2RayXS """, parse_mode="HTML")
    
async def gen_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Gave link to {str(update.effective_user.username)}")
    config = load_config(config_path)
    item = panel.search_user_by_email_prefix(str(update.effective_user.id),page_size=150)
    if item:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="شما قبلا ثبت نام کرده اید.") 
        sub_url = item['subscribe_url']
        await context.bot.send_message(chat_id=update.effective_chat.id, text=sub_url) 
    else:
        result, message = panel.add_user(str(update.effective_user.id), str(update.effective_user.username), get_timestamp(config['expiry_days']),config['default_user_password'],plan_id=config['plan_id'])
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message) 

        result, sub_url = panel.get_sub(str(update.effective_user.id), str(update.effective_user.username))
        await context.bot.send_message(chat_id=update.effective_chat.id, text=sub_url)       
        
    text = f"""{update.effective_chat.id}@{update.effective_user.username}
نام کاربری شما می باشد جهت پشتیبانی های آینده مورد استفاده قرار میگیرد.
در صورت نیاز به پشتیبانی این پیام را برای پشتیبان ارسال کنید."""

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message with three inline buttons attached."""
    
    keyboard = [[InlineKeyboardButton("دریافت لینک شخصی", callback_data="gen_link")],
                [InlineKeyboardButton("گزارش استفاده", callback_data="usage")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Please choose one of the following options:", reply_markup=reply_markup)
    
async def gen_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    config = load_config(config_path)    
    result, usage = panel.get_usage(str(update.effective_user.id))
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"مقدار مصرفی شما: \n {usage} GB")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    await query.answer()
    if query.data == "gen_link":
        await gen_link(update,context)
    elif query.data == "usage":
        await gen_report(update, context)  


def main() -> None:
    # Parse the config file path from the command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--config_path', help='Path to the config file', default='config.yaml')
    args = parser.parse_args()
    global config_path
    config_path = args.config_path
    global panel
    # Load the config file
    config = load_config(config_path)    
    panel = Panel(**config['panel'])

    
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(config['telegram_bot_token']).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()

