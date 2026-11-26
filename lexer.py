import re

TOKEN_PATTERN = re.compile(
    r'(?P<STRING>"[^"\n]*"|\'[^\'\n]*\')'
    r'|(?P<NUMBER>-?\d+(?:\.\d+)?)'
    r'|(?P<OPERATOR>==|!=|>=|<=|[=+\-*/<>])'
    r'|(?P<IDENTIFIER>[a-zA-Z_][a-zA-Z0-9_]*)'
    r'|(?P<SYMBOL>[()])'
    r'|(?P<NEWLINE>\n)'
    r'|(?P<SKIP>[ \t]+)'
    r'|(?P<INVALID>.)'
)

KEYWORDS = {
    "number", "text", "lo",
    "print", "karo", "ko",
    "aur", "jama", "dikhao",
    "agar", "warna", "khatam",
    "jabtak", "se", "ho"
}

COMPARISON_WORDS = {
    "bara", "chota", "barabar"
}


def tokenize(code):

    tokens = []
    line_number = 1

    for match in TOKEN_PATTERN.finditer(code):

        kind = match.lastgroup
        value = match.group()

        if kind == "NEWLINE":
            line_number += 1
            continue

        if kind == "SKIP":
            continue

        if kind == "INVALID":
            raise SyntaxError(
                f"Invalid character '{value}' at line {line_number}"
            )

        if kind == "IDENTIFIER":

            if value in KEYWORDS:
                kind = "KEYWORD"

            elif value in COMPARISON_WORDS:
                kind = "COMPARISON"

        tokens.append((value, kind))

    return tokens