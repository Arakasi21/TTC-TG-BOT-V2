import psycopg2
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
import logging
from telegram.ext import CallbackContext

from database.connection import connect_to_db
logger = logging.getLogger(__name__)

async def start(update: Update, context: CallbackContext) -> None:
    # TODO remove this line

    user_id = update.effective_chat.id
    connection = connect_to_db()

    if not connection:
        await update.message.reply_text("Error with connection to DB /start.")
        return

    try:
        await context.bot.set_my_commands([])
        cursor = connection.cursor()
        cursor.execute("SELECT phone_number FROM Clients WHERE client_id = %s", (user_id,))
        user = cursor.fetchone()

        if user:
            cursor.execute("SELECT admin_id FROM Admins WHERE admin_id = %s", (user_id,))
            admin = cursor.fetchone()

            if admin:
                await update.message.reply_text(
                    "Здравствуйте, Admin!",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton('Profile', callback_data='/profile'),
                         InlineKeyboardButton('Requests', callback_data='/get_requests'),
                         InlineKeyboardButton('Help', callback_data='/help')]
                    ])
                )
            else:
                await update.message.reply_text(
                    "Здравствуйте! Отправьте Фото для обработки вашего запроса.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton('About', callback_data='/about'),
                         InlineKeyboardButton('Help', callback_data='/help')]
                    ])
                )
        else:
            await update.message.reply_text(
                "Please /register with your <phone number>.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton('Register', callback_data='register')]
                ])
            )

    except (Exception, psycopg2.Error) as error:
        logger.error("Error with DB /start: %s", error)
        await update.message.reply_text("Error /start.")
    finally:
        if connection:
            connection.close()