from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import CallbackContext

from commands.choose_request import choose_request
from commands.get_requests import get_requests
from commands.take_request import take_request

chat_sessions = {}
print(chat_sessions)
async def callback_query_handler(update: Update, context: CallbackContext) -> int:
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
    # elif data == '/chat':
    #     await chat(update, context)
    # elif data == '/close_chat':
    #     await close_chat(update, context)
    # elif data == '/close_request':
    #     await close_request(update, context)
    # elif data == '/about':
    #     await about(update, context)
    # elif data == '/help':
    #     await help(update, context)
    # elif data == 'register':
    #     await register(update, context)
    else:
        await query.answer("Unknown command.")

    await query.answer()

