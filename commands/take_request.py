import logging
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext

from database.connection import connect_to_db
from settings.constants import CLOSE_CHAT

logger = logging.getLogger(__name__)

async def take_request(update: Update, context: CallbackContext) -> int:
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
    logger.info("take_request function called")
    user_id = update.effective_chat.id
    admin_id = 577163143  # replace with actual admin_id

    if user_id != admin_id:
        logger.warning("Access denied for user_id: %s", user_id)
        await context.bot.send_message(chat_id=user_id, text="No access!")
        return

    if not context.args or len(context.args) != 1:
        logger.warning("Invalid arguments: %s", context.args)
        await update.message.reply_text("Usage: /take_request <request_id>")
        return

    request_id = context.args[0]
    logger.info(f"Request ID: {request_id}")

    connection = connect_to_db()
    if not connection:
        logger.error("Error with connection to db.")
        await context.bot.send_message(chat_id=user_id, text="Error with connection to db.")
        return

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT photo_id, client_id, problem_description FROM Requests WHERE request_id = %s",
                       (request_id,))
        result = cursor.fetchone()

        if not result:
            logger.warning("Request not found.")
            await context.bot.send_message(chat_id=admin_id, text="Request not found.")
            return

        photo_info, client_id, problem_description = result
        logger.info(f"Photo info: {photo_info}, Client ID: {client_id}, Problem description: {problem_description}")

        cursor.execute("UPDATE Requests SET status = 'In process', admin_id = %s WHERE request_id = %s",
                       (user_id, request_id))
        connection.commit()
        logger.info("Request status updated to 'In process'")

        if client_id:
            await context.bot.send_message(chat_id=client_id, text="Your request is being processed.")

        if photo_info:
            photo_path = photo_info
            try:
                if photo_path.startswith("http"):
                    await context.bot.send_message(chat_id=admin_id, text=f"Photo URL: {photo_path}")
                else:
                    with open(photo_path, 'rb') as photo:
                        await context.bot.send_photo(chat_id=admin_id, photo=photo)
                        await context.bot.send_message(chat_id=admin_id,
                                                       text=f"Problem Description: {problem_description}")
            except BadRequest as e:
                logger.error(f"Error sending photo to admin: {e}")
                await context.bot.send_message(chat_id=admin_id, text="Error sending photo.")
        else:
            await context.bot.send_message(chat_id=admin_id, text="No photo associated with this request.")

        await context.bot.send_message(chat_id=admin_id,
                                       text=f"Request {request_id} is now marked as 'In process' and assigned to you.")

        if client_id:
            keyboard = [[InlineKeyboardButton("Start Chat", callback_data="/chat " + str(client_id) + " " + str(request_id))]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(chat_id=admin_id, text="Press the button below to start a chat with the client.",
                                           reply_markup=reply_markup)
            return CLOSE_CHAT

    except Exception as e:
        logger.error(f"Error updating request status or fetching photo: {e}")
        await context.bot.send_message(chat_id=user_id, text="Error updating request status or fetching photo.")
    finally:
        if connection:
            cursor.close()
            connection.close()
        logger.info("take_request function finished")