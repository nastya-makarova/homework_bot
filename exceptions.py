class TokenNotFoundError(Exception):
    """Исключение выбрасывается при недоступности переменных с токенами."""


class TimestampError(ValueError):
    """Исключение выбрасывается при некорректном значении метки времени."""


class HomeworkNotFoundError(Exception):
    """Исключение выбрасывается при пустом списке домашних работ."""


class APIResponseError(TypeError):
    """Исключение выбрасывается при несоответсвии ответа API документации."""


class StatusError(Exception):
    """Исключение выбрасывается при неизвестном статусе работы."""


class HomeworksTypeError(TypeError):
    """Исключение выбрасывается при несоответсвии ответа API документации."""


class ResponseTypeError(TypeError):
    """Исключение выбрасывается при несоответсвии ответа API документации."""


class ResponseStatusError(Exception):
    """Исключение выбрасывается, если API возвращает код, отличный от 200."""


class APIStatusError(TypeError):
    """Исключение выбрасывается, ответ API не содержит ключ status."""


class APIHomeworkError(TypeError):
    """Исключение выбрасывается, ответ API не содержит ключ homework_name."""
