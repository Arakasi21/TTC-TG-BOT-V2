import psycopg2
from telegram.ext import CallbackContext, ConversationHandler
from telegram import Update
from database.connection import connect_to_db
import uuid
import os

from settings.constants import SUBMIT_DESCRIPTION

# from settings.constants import SUBMIT_PHOTO, SUBMIT_TEXT, SEND_FEEDBACK

# A dictionary to store the temporary photo paths for each user
temp_photo_paths = {}

async def handle_photo(update: Update, context: CallbackContext):
    client_id = update.message.from_user.id
    if update.message.photo:
        photo_file = update.message.photo[-1]

        photo_number = str(uuid.uuid4())
        photo_name = f"{client_id}_{photo_number}.jpg"

        temp_photo_dir = "./temp_photos"
        temp_photo_path = os.path.join(temp_photo_dir, photo_name)

        if not os.path.exists(temp_photo_dir):
            os.makedirs(temp_photo_dir)

        try:
            telegram_file = await photo_file.get_file()
            await telegram_file.download_to_drive(temp_photo_path)

            # Store the temporary photo path for this user
            temp_photo_paths[client_id] = temp_photo_path

            await context.bot.send_message(chat_id=update.effective_chat.id, text="Пожалуйста опишите проблему.")
            return SUBMIT_DESCRIPTION

        except AttributeError:
            print("Warning:.")

async def handle_description(update: Update, context: CallbackContext):
    client_id = update.message.from_user.id
    problem_description = update.message.text

    temp_photo_path = temp_photo_paths.get(client_id)

    if temp_photo_path:
        await save_photo_path_in_database(client_id, temp_photo_path, problem_description)
        await update.message.reply_text("Запрос отправлен. Ожидайте ответа.")
        del temp_photo_paths[client_id]
    else:
        await update.message.reply_text("No photo found. Please send a photo first.")
    return ConversationHandler.END

async def save_photo_path_in_database(client_id, photo_path, problem_description):
    conn = connect_to_db()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Requests (client_id, photo_id, timestamp, status, problem_description) VALUES (%s, %s, CURRENT_TIMESTAMP, 'New', %s)",
                (client_id, photo_path, problem_description))
            conn.commit()
        except (Exception, psycopg2.Error) as error:
            print(f"Error while inserting into database: {error}")
        finally:
            cursor.close()
            conn.close()
    else:
        print("Failed to connect to database.")