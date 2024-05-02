# TTC Telegram Bot

This project is a Telegram bot developed in Python using the python-telegram-bot library. The bot is designed to handle requests from users, allowing them to submit photos and descriptions of issues they are facing. Administrators can then review these requests and respond accordingly.

## Features

- Users can submit a request by sending a photo and a description of their issue.
- Administrators can review these requests and choose to take them on.
- Administrators can close a chat session with a user.
- Users can provide feedback after their request has been handled.

## Installation

1. Clone the repository:
    ```
    git clone https://github.com/username/TTC-telegram-bot-v2.git
    ```
2. Navigate to the project directory:
    ```
    cd TTC-telegram-bot-v2
    ```
3. Install the required dependencies:
    ```
    pip install -r requirements.txt
    ```

## Usage

1. Run the bot:
    ```
    python main.py
    ```
2. Interact with the bot on Telegram.

## Dependencies

- anyio==4.3.0
- certifi==2024.2.2
- h11==0.14.0
- httpcore==1.0.5
- httpx==0.27.0
- idna==3.7
- psycopg2==2.9.9
- python-dotenv==1.0.1
- python-telegram-bot==21.1.1
- sniffio==1.3.1
- telegram==0.0.1

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)