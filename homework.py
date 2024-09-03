import os
import requests
import time

from dotenv import load_dotenv
from telebot import TeleBot

from exceptions import TokenNotFoundError, TimestampError, HomeworkNotFoundError, APIResponseError

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Функция проверяет доступность переменных окружения."""
    tokens = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    if any(token is None for token in tokens):
        raise TokenNotFoundError
    else:
        return True


def send_message(bot, message):
    """Функция отправляет сообщение в чат, определяемый TELEGRAM_CHAT_ID."""
    # message = parse_status(homework)
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)


def get_api_answer(timestamp):
    """Функция делает запрос к единственному эндпоинту API-сервиса."""
    if not isinstance(timestamp, int) or timestamp < 0:
        raise TimestampError

    if check_tokens():
        payload = {'from_date': timestamp}
        try:
            homework_statuses = requests.get(
                ENDPOINT,
                headers=HEADERS,
                params=payload
            )
        except Exception as error:
            print(f'Ошибка при запросе к основному API: {error}')
        else:
            return homework_statuses.json()


def check_response(response):
    """Функция проверяет ответ API на соответствие документации."""
    # response = get_api_answer(timestamp)
    if 'homeworks' not in response and 'current_date' not in response:
        raise APIResponseError
    elif response.get('homeworks') == []:
        raise HomeworkNotFoundError
    else:
        return True


def parse_status(homework):
    """Функция извлекает статус конкретной домашней работы."""
    # homework = homework_statuses.json().get('homeworks')[0]
    # homework_statuses.json() = get_api_answer(timestamp)
    homework_name = homework.get('homework_name')
    status = homework.get('status')
    verdict = HOMEWORK_VERDICTS.get(status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    bot = TeleBot(token=TELEGRAM_TOKEN)
    #timestamp = int(time.time())
    timestamp = 0

    while True:
        try:
            response = get_api_answer(timestamp)
            if check_response(response):
                homework = response.get('homeworks')[0]
                homework_id = homework.get('id')
                statuses = {}
                if homework_id not in statuses:
                    statuses[homework_id] = homework.get('status')
                old_status = statuses.get(homework_id)
                if old_status != homework.get('status'):
                    statuses[homework_id] = homework.get('status')
                    message = parse_status(homework)
                    send_message(bot, message)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
