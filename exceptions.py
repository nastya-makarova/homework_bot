class TokenNotFoundError(Exception):
    """Исключение выбрасывается при недоступности переменных с токенами."""

    pass


class TimestampError(ValueError):
    """Исключение выбрасывается при некорректном значении метки времени."""

    pass


class HomeworkNotFoundError(Exception):
    """Исключение выбрасывается при пустом списке домашних работ."""

    pass


class APIResponseError(Exception):
    """Исключение выбрасывается при несоответсвии ответа API документации."""

    pass


class StatusError(Exception):
    """Исключение выбрасывается при неизвестном статусе работы."""

    pass