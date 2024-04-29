from telegram import Update
from telegram.ext import ApplicationBuilder, ConversationHandler, filters, CommandHandler, MessageHandler, \
    CallbackContext, CallbackQueryHandler

from commands.callbackqueryhandler import callback_query_handler
from commands.choose_request import choose_request
from commands.get_requests import get_requests
from commands.handle_photo import handle_photo, handle_description
from commands.take_request import take_request
from settings.config import TOKEN
import logging

from settings.constants import GET_REQUESTS, CHOOSE_REQUEST, TAKE_REQUEST, CLOSE_CHAT, CLOSE_REQUEST, SUBMIT_PHOTO, \
    SUBMIT_DESCRIPTION

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(message)s', level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Вы завершили request cycle")
    return ConversationHandler.END
def main(client_handler=None) -> None:
    application = ApplicationBuilder().token(TOKEN).build()

    # Admin conversation handler
    admin_handler = ConversationHandler(
        entry_points=[CommandHandler('start', get_requests)],
        states={
            GET_REQUESTS: [CommandHandler('get_requests', get_requests)],
            CHOOSE_REQUEST: [CommandHandler('choose_request', choose_request)],
            TAKE_REQUEST: [CommandHandler('take_request', take_request)],
            # CHAT: [CommandHandler('chat', chat)],
            # CLOSE_CHAT: [CommandHandler('close_chat', close_chat)],
            # CLOSE_REQUEST: [CommandHandler('close_request', close_request)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Client conversation handler
    client_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.PHOTO, handle_photo)],
        states={
            SUBMIT_PHOTO: [MessageHandler(filters.PHOTO, handle_photo)],
            SUBMIT_DESCRIPTION: [MessageHandler(filters.TEXT, handle_description)],
            # SUBMIT_FEEDBACK: [MessageHandler(filters.TEXT, handle_feedback)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(admin_handler)
    application.add_handler(client_handler)
    application.add_handler(CallbackQueryHandler(callback_query_handler))
    application.run_polling()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())