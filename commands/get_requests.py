import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ContextTypes
from database.connection import connect_to_db
from settings.constants import CHOOSE_REQUEST

logger = logging.getLogger(__name__)


async def get_requests(update: Update, context:  ContextTypes.DEFAULT_TYPE) -> int:
    if 'choose_option_message_id' in context.user_data:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id,
                                             message_id=context.user_data['choose_option_message_id'])
            del context.user_data['choose_option_message_id']
        except Exception as e:
            logger.error(f"Error deleting message: {e}")

    if 'request_details_message_id' in context.user_data:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id,
                                             message_id=context.user_data['request_details_message_id'])
            del context.user_data['request_details_message_id']
        except Exception as e:
            logger.error(f"Error deleting message: {e}")

    if 'photo_message_id' in context.user_data:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id,
                                             message_id=context.user_data['photo_message_id'])
            del context.user_data['photo_message_id']
        except Exception as e:
            logger.error(f"Error deleting message: {e}")
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
            message = await update.effective_message.reply_text('Please select a request:', reply_markup=reply_markup)
            context.user_data['select_request_message_id'] = message.message_id
        else:
            message = await update.effective_message.reply_text('Please select a request:', reply_markup=reply_markup)
            context.user_data['select_request_message_id'] = message.message_id

    except Exception as e:
        logger.error(f"Error with getting list of requests: {e}")
        await context.bot.send_message(chat_id=user_id, text="Error with getting list of requests.")
    finally:
        if connection:
            connection.close()
        logger.info("get_requests function finished")

    return CHOOSE_REQUEST