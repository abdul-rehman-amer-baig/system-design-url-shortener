from sqids import Sqids

_sqids = Sqids(
    alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    min_length=6,
)


def generate_shortcode(counter: int) -> str:
    return _sqids.encode([counter]) 