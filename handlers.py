import logging
import os

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


class TelegramHandler(logging.Handler):
    """Отправляет сообщения в телеграм, когда происходит ошибка."""

    def __init__(self, bot, telegram_chat_id, last_log_message):
        """Инициализирует обработчик для отправки сообщений в Telegram."""
        super().__init__()
        self.bot = bot
        self.telegram_chat_id = telegram_chat_id
        self.last_log_message = None

    def emit(self, record):
        """
        Метод отправляет сообщение в Telegram.
        Сообщение будет отправлено, если уровень логирования является ERROR
        и сообщение не совпадает с последним отправленным.
        """
        if record.levelname == 'ERROR':
            log_message = self.format(record)
            if log_message != self.last_log_message:
                self.send_log_message(log_message)
                self.last_log_message = log_message

    def send_log_message(self, bot, message):
        """Метод отправляет сообщение в Telegram с помощью указанного бота."""
        if not self.telegram_chat_id:
            logging.error(
                'Отсутствует обязательная переменная окружения:'
                'telegram chat_id '
            )
            return
        try:
            bot.send_message(chat_id=self.telegram_chat_id, text=message)
        except Exception as error:
            logging.error(error, 'Невозможно отправить сообщение об ошибке.')
