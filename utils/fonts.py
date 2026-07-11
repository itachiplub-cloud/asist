BOLD_UPPER = {
    'A': '\U0001D400', 'B': '\U0001D401', 'C': '\U0001D402', 'D': '\U0001D403',
    'E': '\U0001D404', 'F': '\U0001D405', 'G': '\U0001D406', 'H': '\U0001D407',
    'I': '\U0001D408', 'J': '\U0001D409', 'K': '\U0001D40A', 'L': '\U0001D40B',
    'M': '\U0001D40C', 'N': '\U0001D40D', 'O': '\U0001D40E', 'P': '\U0001D40F',
    'Q': '\U0001D410', 'R': '\U0001D411', 'S': '\U0001D412', 'T': '\U0001D413',
    'U': '\U0001D414', 'V': '\U0001D415', 'W': '\U0001D416', 'X': '\U0001D417',
    'Y': '\U0001D418', 'Z': '\U0001D419',
}

BOLD_LOWER = {
    'a': '\U0001D41A', 'b': '\U0001D41B', 'c': '\U0001D41C', 'd': '\U0001D41D',
    'e': '\U0001D41E', 'f': '\U0001D41F', 'g': '\U0001D420', 'h': '\U0001D421',
    'i': '\U0001D422', 'j': '\U0001D423', 'k': '\U0001D424', 'l': '\U0001D425',
    'm': '\U0001D426', 'n': '\U0001D427', 'o': '\U0001D428', 'p': '\U0001D429',
    'q': '\U0001D42A', 'r': '\U0001D42B', 's': '\U0001D42C', 't': '\U0001D42D',
    'u': '\U0001D42E', 'v': '\U0001D42F', 'w': '\U0001D430', 'x': '\U0001D431',
    'y': '\U0001D432', 'z': '\U0001D433',
}

BOLD_DIGITS = {
    '0': '\U0001D7CE', '1': '\U0001D7CF', '2': '\U0001D7D0', '3': '\U0001D7D1',
    '4': '\U0001D7D2', '5': '\U0001D7D3', '6': '\U0001D7D4', '7': '\U0001D7D5',
    '8': '\U0001D7D6', '9': '\U0001D7D7',
}

SMALL_CAPS = {
    'a': '\u1D00', 'b': '\u0299', 'c': '\u1D04', 'd': '\u1D05',
    'e': '\u1D07', 'f': '\uA730', 'g': '\u0262', 'h': '\u029C',
    'i': '\u026A', 'j': '\u1D0A', 'k': '\u1D0B', 'l': '\u029F',
    'm': '\u1D0D', 'n': '\u0274', 'o': '\u1D0F', 'p': '\u1D18',
    'q': '\uA7AF', 'r': '\u0280', 's': '\uA731', 't': '\u1D1B',
    'u': '\u1D1C', 'v': '\u1D20', 'w': '\u1D21', 'x': '\u02E3',
    'y': '\u028F', 'z': '\u1D22',
}

_BOLD_MAP = {}
_BOLD_MAP.update(BOLD_UPPER)
_BOLD_MAP.update(BOLD_LOWER)
_BOLD_MAP.update(BOLD_DIGITS)

_SMALL_CAPS_UPPER = {k.upper(): v for k, v in SMALL_CAPS.items()}
_SMALL_CAPS_ALL = {}
_SMALL_CAPS_ALL.update(SMALL_CAPS)
_SMALL_CAPS_ALL.update(_SMALL_CAPS_UPPER)


def to_bold(text: str) -> str:
    chars = []
    for ch in text:
        chars.append(_BOLD_MAP.get(ch, ch))
    return ''.join(chars)


def to_smallcaps(text: str) -> str:
    chars = []
    for ch in text:
        chars.append(_SMALL_CAPS_ALL.get(ch, ch))
    return ''.join(chars)


def to_fancy(text: str) -> str:
    chars = []
    i = 0
    while i < len(text):
        if text[i].isalpha():
            start = i
            while i < len(text) and text[i].isalpha():
                i += 1
            word = text[start:i]
            first = BOLD_UPPER.get(word[0].upper(), word[0])
            rest_list = []
            for ch in word[1:]:
                rest_list.append(SMALL_CAPS.get(ch.lower(), ch))
            rest = ''.join(rest_list)
            chars.append(first + rest)
        else:
            chars.append(text[i])
            i += 1
    return ''.join(chars)


def fancy(text: str) -> str:
    return to_bold(text)


def format_menu(title: str, sections: list, footer: str = "") -> str:
    lines = [to_fancy(title)]
    lines.append("")
    for section_title, items in sections:
        lines.append(to_fancy(section_title))
        for item in items:
            lines.append(item)
        lines.append("")
    if footer:
        lines.append(footer)
    return "\n".join(lines)
