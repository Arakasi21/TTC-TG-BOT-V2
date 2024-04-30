import logging

from telegram import Update, CallbackQuery
from telegram.ext import CallbackContext

from commands.chat import handle_chat_action, close_chat
from commands.choose_request import choose_request
from commands.close_request import close_request
from commands.get_requests import get_requests
from commands.take_request import take_request

logger = logging.getLogger(__name__)

async def callback_query_handler(update: Update, context: CallbackContext) -> None:
    query: CallbackQuery = update.callback_query
    data = query.data.split(' ')
    command = data[0]
    args = data[1:]

    if command == '/get_requests':
        await get_requests(update, context)
    elif command == '/choose_request':
        context.args = args
        await choose_request(update, context)
    elif command == '/take_request':
        context.args = args
        await take_request(update, context)
    elif command == '/chat':
        if len(args) > 1:
            await handle_chat_action(update, context, int(args[0]), int(args[1]))
        else:
            await query.answer("Invalid command.")
    elif command == '/close_chat':
        if len(args) > 1:
            await close_chat(update, context, int(args[0]), int(args[1]))
        else:
            await query.answer("Invalid command.")
    elif command == '/close_request':
        await close_request(update, context, int(args[0]))
    else:
        await query.answer("Unknown command.")

    await query.edit_message_reply_markup(reply_markup=None)
    await query.answer()