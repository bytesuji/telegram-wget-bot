#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

import logging
import mimetypes
import requests
import traceback
import urllib

from driver import WebDriverResource
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO,
    filename="/tmp/wgetbot.log")

logger = logging.getLogger(__name__)
resource = WebDriverResource()

with open('./bot-api-key.txt') as fp:
    api_key = fp.read().strip()
logger.info("Using API key " + api_key)

def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr"""Hi {user.mention_markdown_v2()}\! This bot is for downloading things from the Internet\.
/google \<terms\> \- search the web \(may not work on mobile\)
/get \<URL\> \- download a resource""",
        reply_markup=ForceReply(selective=True))

def help_command(update: Update, context: CallbackContext) -> None:
    msg = ('Send any URL to receive a copy of the file at that location.'
           '\nYou can use `/google <search terms>` to search the net.')
    update.message.reply_text(msg)

def get_file_ext(mime_type):
    mt = mimetypes.MimeTypes()
    lookup = mt.types_map_inv[1]
    return lookup[mime_type][0]

def get_url_doc(url):
    if not ("http://" in url or "https://" in url):
       url = "http://" + url

    try:
        response = requests.get(url)
        mimetype = response.headers['Content-Type']
        file_ext = get_file_ext(mimetype)
        filename = f"document.{file_ext}"
    except:
        filename = "document.html"

    logger.info(f"Getting URL {url}")
    resource.get(url)
    doc = resource.driver.page_source.encode()

    return filename, doc

def wget(update, context):
    url = context.args[0]
    try:
        filename, doc = get_url_doc(url)
        update.message.reply_document(doc, filename=filename)
    except:
        update.message.reply_text("Sorry, something went wrong! Please contact the maintainer.")
        logger.critical(traceback.format_exc())

def google(update, context):
    term = urllib.parse.quote_plus(' '.join(context.args))
    url = f"https://google.com/search?q={term}"

    try:
        filename, doc = get_url_doc(url)
        update.message.reply_document(doc, filename=filename)
    except:
        update.message.reply_text("Sorry, something went wrong! Please contact the maintainer.")
        logger.critical(traceback.format_exc())

def unknown_command(update, context):
    msg = """Unrecognized command. Try these instead:
/google <terms> - search the web (may not work on mobile)
/get <URL> - download a resource"""
    logger.info("Received unknown command: " + update.message.text)
    update.message.reply_text(msg)

def main() -> None:
    # Initialize bot
    updater = Updater(api_key)

    # Register commands
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("google", google))
    dispatcher.add_handler(CommandHandler("get", wget))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, unknown_command))

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
