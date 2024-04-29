import logging
from database.connection import connect_to_db
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

logger = logging.getLogger(__name__)

async def close_request(update: Update, context: ContextTypes.DEFAULT_TYPE, request_id: int) -> int:
    user_id = update.effective_chat.id
    admin_id = 577163143  # переделать

    logger.info(f"Attempting to close request {request_id} by user {user_id}")

    if user_id != admin_id:
        logger.warning(f"User {user_id} attempted to close request but does not have access")
        await context.bot.send_message(chat_id=user_id, text="No access!")
        return ConversationHandler.END

    if not request_id:
        if not context.args or len(context.args) != 1:
            logger.warning("Invalid usage: /close_request <request_id>")
            await update.message.reply_text("Usage: /close_request <request_id>")
            return ConversationHandler.END
        request_id = context.args[0]

    connection = connect_to_db()
    if not connection:
        logger.error("Error with connection to db.")
        await context.bot.send_message(chat_id=user_id, text="Error with connection to db.")
        return ConversationHandler.END

    try:
        cursor = connection.cursor()
        cursor.execute("UPDATE Requests SET status = 'Closed', admin_id = %s WHERE request_id = %s",
                       (user_id, request_id))
        connection.commit()
        logger.info(f"Request {request_id} has been marked as 'Closed'.")
        await context.bot.send_message(chat_id=user_id, text=f"Request {request_id} has been marked as 'Closed'.")
    except Exception as e:
        logger.error(f"Error updating request status: {e}")
        await context.bot.send_message(chat_id=user_id, text="Error updating request status.")
    finally:
        if connection:
            connection.close()
    return ConversationHandler.END