from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
from telegram.ext import CallbackContext

from settings.constants import CLOSE_REQUEST

chat_sessions = {}
print("chat_sessions: " + str(chat_sessions))

async def handle_chat_action(update: Update, context: CallbackContext, client_id: int, request_id: int) -> None:
    chat_id = update.effective_chat.id
    chat_sessions[chat_id] = {"client_id": client_id, "request_id": request_id}

    # commands = [
    #     BotCommand(command=f"close_chat_{request_id}_{client_id}", description="Close the chat")]
    # await context.bot.set_my_commands(commands)

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
            if str(session_info["client_id"]) == str(from_id):
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