import logging
from telegram import Update, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from database.connection import connect_to_db

logger = logging.getLogger(__name__)

async def choose_request(update: Update, context: CallbackContext) -> int:

    logger.info("choose_request function called")
    query: CallbackQuery = update.callback_query
    request_id = query.data.split()[1]  # get the request_id from the callback_data
    logger.info(f"Request ID: {request_id}")

    connection = connect_to_db()
    if not connection:
        logger.error("Error with connection to db.")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Error with connection to db.")
        return

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Requests WHERE request_id = %s", (request_id,))
        row = cursor.fetchone()

        if row is None:
            logger.warning(f"Request not found for ID: {request_id}")
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Request not found.")
        else:
            request_details = f"Request ID: {row[0]}\nStatus: {row[4]}\nProblem: {row[6]}"
            photo_url = row[2]
            if photo_url:
                message = await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo_url)
                context.user_data['photo_message_id'] = message.message_id


            logger.info(f"Request details: {request_details}")
            message = await context.bot.send_message(chat_id=update.effective_chat.id, text=request_details)
            context.user_data['request_details_message_id'] = message.message_id

            # Add inline keyboard with options to get back to get_requests or take request
            keyboard = [
                [InlineKeyboardButton('Get Requests', callback_data='/get_requests'),
                 InlineKeyboardButton('Take Request', callback_data='/take_request ' + request_id)]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            message = await context.bot.send_message(chat_id=update.effective_chat.id, text="Choose an option:",
                                                     reply_markup=reply_markup)
            context.user_data['choose_option_message_id'] = message.message_id

    except Exception as e:
        logger.error(f"Error with fetching request: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Error with fetching request.")
    finally:
        if connection:
            connection.close()
        logger.info("choose_request function finished")