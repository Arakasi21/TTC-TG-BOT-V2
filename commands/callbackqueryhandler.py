import logging

from telegram import Update, CallbackQuery
from telegram.error import BadRequest
from telegram.ext import CallbackContext

from commands.chat import handle_chat_action, close_chat, handle_feedback
from commands.choose_request import choose_request
from commands.close_request import close_request
from commands.get_requests import get_requests
from commands.take_request import take_request

logger = logging.getLogger(__name__)

COMMANDS = {
    '/get_requests': get_requests,
    '/choose_request': choose_request,
    '/take_request': take_request,
    '/chat': handle_chat_action,
    '/close_chat': close_chat,
    '/close_request': close_request,
    # TODO redo this
    '/feedback': handle_feedback,
}

async def callback_query_handler(update: Update, context: CallbackContext) -> None:
    query: CallbackQuery = update.callback_query
    data = query.data.split(' ')
    command = data[0]
    args = data[1:]

    try:
        if command in COMMANDS:
            if command in ['/chat', '/close_chat'] and len(args) <= 1:
                error_message = f"The command {command} requires two arguments."
                logger.error(error_message)
                raise ValueError(error_message)
            elif command == '/close_request' and len(args) != 1:
                error_message = "The command /close_request requires one argument."
                logger.error(error_message)
                raise ValueError(error_message)
            else:
                if command in ['/chat', '/close_chat']:
                    client_id = int(args[0])
                    request_id = int(args[1])
                    await COMMANDS[command](update, context, client_id, request_id)
                elif command == '/close_request':
                    request_id = int(args[0])
                    await COMMANDS[command](update, context, request_id)
                else:
                    context.args = args
                    await COMMANDS[command](update, context)
        else:
            error_message = f"Unknown command: {command}"
            logger.error(error_message)
            raise ValueError(error_message)
    except ValueError as e:
        await query.answer(str(e))
        logger.error(f"Error occurred: {str(e)}")

    try:
        await query.edit_message_reply_markup(reply_markup=None)
    except BadRequest:
        pass
    await query.answer()
