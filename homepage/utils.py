from django.utils.text import slugify


_CYRILLIC = dict(zip(
    "абвгдеёжзийклмнопрстуфхцчшщъыьэюя",
    ("a", "b", "v", "g", "d", "e", "yo", "zh", "z", "i", "y", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u", "f", "kh", "ts", "ch", "sh", "shch", "", "y", "", "e", "yu", "ya"),
))


def event_slug(title):
    """Читаемый ASCII-slug для русских и латинских названий."""
    return slugify("".join(_CYRILLIC.get(char, char) for char in title.lower()))[:190] or "event"
