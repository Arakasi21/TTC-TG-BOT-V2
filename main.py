from telegram import Update
from telegram.ext import ApplicationBuilder, ConversationHandler, filters, CommandHandler, MessageHandler, \
    CallbackContext, CallbackQueryHandler

from commands.callbackqueryhandler import callback_query_handler
from commands.chat import close_chat, message_handler, handle_feedback
from commands.choose_request import choose_request
from commands.close_request import close_request
from commands.get_requests import get_requests
from commands.handle_photo import handle_photo, handle_description
from commands.start import start
from commands.take_request import take_request
from settings.config import TOKEN
import logging

from settings.constants import GET_REQUESTS, CHOOSE_REQUEST, TAKE_REQUEST, CLOSE_CHAT, CLOSE_REQUEST, SUBMIT_PHOTO, \
    SUBMIT_DESCRIPTION, SUBMIT_FEEDBACK

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(message)s', level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Вы завершили request cycle")
    return ConversationHandler.END

def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler('start', start)

    # Admin conversation handler
    admin_handler = ConversationHandler(
        entry_points=[CommandHandler('Requests', get_requests)],
        states={
            GET_REQUESTS: [CommandHandler('get_requests', get_requests)],
            CHOOSE_REQUEST: [CommandHandler('choose_request', choose_request)],
            TAKE_REQUEST: [CommandHandler('take_request', take_request)],
            CLOSE_CHAT: [CommandHandler('close_chat', close_chat)],
            CLOSE_REQUEST: [CommandHandler('close_request', close_request)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Client conversation handler
    client_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.PHOTO, handle_photo)],
        states={
            SUBMIT_PHOTO: [MessageHandler(filters.PHOTO, handle_photo)],
            SUBMIT_DESCRIPTION: [MessageHandler(filters.TEXT, handle_description)],
            # TODO redo this
            SUBMIT_FEEDBACK: [MessageHandler(filters.TEXT, handle_feedback)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(start_handler)

    application.add_handler(admin_handler)
    application.add_handler(client_handler)

    application.add_handler(CallbackQueryHandler(callback_query_handler))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message_handler))

    application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())