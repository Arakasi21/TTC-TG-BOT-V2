import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ContextTypes
from database.connection import connect_to_db
from settings.constants import CHOOSE_REQUEST

logger = logging.getLogger(__name__)


async def get_requests(update: Update, context:  ContextTypes.DEFAULT_TYPE) -> int:
    logger.info("get_requests function called")
    user_id = update.effective_chat.id
    admin_id = 577163143  # replace with actual admin_id

    if user_id != admin_id:
        logger.warning("Access denied for user_id: %s", user_id)
        await context.bot.send_message(chat_id=user_id, text="No access!")
        return

    connection = connect_to_db()
    if not connection:
        logger.error("Error with connection to db.")
        await context.bot.send_message(chat_id=user_id, text="Error with connection to db.")
        return

    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT request_id, status, problem_description FROM Requests WHERE status = 'New' OR status = 'Pending'")
        rows = cursor.fetchall()
        logger.info("Fetched rows from database: %s", rows)

        keyboard = [[InlineKeyboardButton(f"Request ID: {row[0]}, Status: {row[1]}, Problem: {row[2]}",
                                          callback_data="/choose_request " + str(row[0]))] for row in rows]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if update.callback_query:
            await update.callback_query.message.reply_text('Please select a request:', reply_markup=reply_markup)
        else:
            await update.message.reply_text('Please select a request:', reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Error with getting list of requests: {e}")
        await context.bot.send_message(chat_id=user_id, text="Error with getting list of requests.")
    finally:
        if connection:
            connection.close()
        logger.info("get_requests function finished")

    return CHOOSE_REQUEST
