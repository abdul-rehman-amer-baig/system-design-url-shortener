from sqids import Sqids

_sqids = Sqids(
    alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    min_length=6,
)


def generate_shortcode(counter: int) -> str:
    return _sqids.encode([counter])


def decode_shortcode(code: str) -> int:
    numbers = _sqids.decode(code)
    return numbers[0] if numbers else -1
