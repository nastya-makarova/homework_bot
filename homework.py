import os
import requests
import time

from dotenv import load_dotenv
from telebot import TeleBot

from exceptions import TokenNotFoundError, TimestampError

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 10
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Функция проверяет доступность переменных окружения."""
    if PRACTICUM_TOKEN or TELEGRAM_TOKEN or TELEGRAM_CHAT_ID is None:
        return False
    else:
        return True


def send_message(bot, message):
    """Функция отправляет сообщение в чат, определяемый TELEGRAM_CHAT_ID."""
    # message = parse_status(homework)
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)


def get_api_answer(timestamp):
    """Функция делает запрос к единственному эндпоинту API-сервиса."""
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
    return 'homeworks' in response and 'current_date' in response


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
    # timestamp = int(time.time())
    timestamp = 0

    if not isinstance(timestamp, int) or timestamp < 0:
        raise TimestampError

    while True:
        try:
            response = get_api_answer(timestamp)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
        else:
            print(response)
            print('homeworks' in response and 'current_date' in response)
            if not check_tokens(response):
                raise TokenNotFoundError

            homework = response.get('homeworks')[0]
            print(homework)
            
            message = parse_status(homework)
            send_message(bot, message)

        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
