import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.error import BadRequest
from telegram.ext import CallbackContext

from commands.chat import handle_chat_action, close_chat
from commands.choose_request import choose_request
from commands.close_request import close_request
from commands.get_requests import get_requests
from commands.take_request import take_request
from settings.constants import CLOSE_REQUEST, SUBMIT_FEEDBACK

logger = logging.getLogger(__name__)

async def callback_query_handler(update: Update, context: CallbackContext) -> None:
    query: CallbackQuery = update.callback_query
    data = query.data

    print(f"Data: {data}")

    if data == '/get_requests':
        await get_requests(update, context)
    elif data.startswith('/choose_request'):
        request_id = data.split(' ')[1]
        context.args = [request_id]
        await choose_request(update, context)
    elif data.startswith('/take_request'):
        request_id = data.split(' ')[1]
        context.args = [request_id]
        await take_request(update, context)
    elif data.startswith('/chat'):
        parts = data.split(' ')
        if len(parts) > 2:
            client_id = parts[1]
            request_id = parts[2]
            await handle_chat_action(update, context, int(client_id), int(request_id))
        else:
            logger.error("Invalid data: %s", data)
            await query.answer("Invalid command.")
    elif data.startswith('/close_chat'):
        parts = data.split(' ')
        if len(parts) > 2:
            request_id = parts[1]
            client_id = parts[2]
            await close_chat(update, context, int(client_id), int(request_id))
        else:
            logger.error("Invalid data: %s", data)
            await query.answer("Invalid command.")
    elif data.startswith('/close_request'):
        request_id = data.split(' ')[1]
        await close_request(update, context, int(request_id))
    else:
        await query.answer("Unknown command.")

    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except Exception as e:
        logger.error(f"Error removing inline keyboard: {e}")

    try:
        await query.answer()
    except BadRequest as e:
        print(f"Failed to answer callback query: {e.message}")