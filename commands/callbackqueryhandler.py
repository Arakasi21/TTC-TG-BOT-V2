import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import CallbackContext

from commands.choose_request import choose_request
from commands.close_request import close_request
from commands.get_requests import get_requests
from commands.take_request import take_request
from settings.constants import CLOSE_REQUEST, SUBMIT_FEEDBACK

logger = logging.getLogger(__name__)

chat_sessions = {}
print(chat_sessions)
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

    # elif data == '/about':
    #     await about(update, context)
    # elif data == '/help':
    #     await help(update, context)
    # elif data == 'register':
    #     await register(update, context)
    else:
        await query.answer("Unknown command.")

    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except Exception as e:
        logger.error(f"Error removing inline keyboard: {e}")

    await query.answer()

async def handle_chat_action(update: Update, context: CallbackContext, client_id: int, request_id: int) -> None:
    chat_id = update.effective_chat.id
    chat_sessions[chat_id] = {"client_id": client_id, "request_id": request_id}
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Close Chat", callback_data="/close_chat " + str(request_id) + " " + str(client_id))],
    ])
    await context.bot.send_message(chat_id=chat_id, text=f"Чат с пользователем {client_id} начат.", reply_markup=reply_markup)
    await context.bot.send_message(chat_id=client_id,
                                   text="Здравствуйте! С вами связывается сотрудник Transtelecom. Ниже вы будете общаться с человеком.")


async def message_handler(update: Update, context: CallbackContext) -> None:
    from_id = update.effective_chat.id
    text = update.message.text
    # ОТ админа К клиенту
    if from_id in chat_sessions:
        client_id = chat_sessions[from_id]["client_id"]
        await context.bot.send_message(chat_id=client_id, text=text)
    # ОТ клиента К админу
    else:
        for admin_id, session_info in chat_sessions.items():
            if session_info["client_id"] == str(from_id):
                await context.bot.send_message(chat_id=admin_id, text=text)

async def close_chat(update: Update, context: CallbackContext, client_id: int, request_id: int) -> tuple[any, any]:
    from_id = update.effective_chat.id
    if from_id in chat_sessions:
        del chat_sessions[from_id]

        await context.bot.send_message(chat_id=from_id, text="Chat session closed.")

        print("Request id in commands/chat/close_chat: " + str(request_id))
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Close Request", callback_data="/close_request " + str(request_id))]
        ])
        await context.bot.send_message(chat_id=from_id, text="Would you like to close the request?",
                                       reply_markup=reply_markup)

        await context.bot.send_message(chat_id=client_id, text="Your request was closed, want to give feedback?")
        return CLOSE_REQUEST
