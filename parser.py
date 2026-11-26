import re

IDENTIFIER = r"[A-Za-z_]\w*"

STRING = r'''(?:"[^"\n]*"|'[^'\n]*')'''

VALUE = rf"(?:{STRING}|-?\d+(?:\.\d+)?|{IDENTIFIER})"

CONDITION = (
    rf"agar\s+({IDENTIFIER})\s+"
    rf"(-?\d+(?:\.\d+)?)\s+se\s+"
    r"(bara|chota|barabar)\s+ho"
)

DECLARATION = (
    rf"(?:number\s+lo\s+({IDENTIFIER})|"
    rf"text\s+lo\s+({IDENTIFIER})|"
    rf"({IDENTIFIER})\s+lo)"
)

ASSIGNMENT = (
    rf"{IDENTIFIER}\s*=\s*{VALUE}"
    rf"(?:\s*[+\-*/]\s*{VALUE})*"
)


def syntax_check(code):

    lines = code.splitlines()
    block_stack = []

    for line_number, original in enumerate(lines, 1):

        line = original.strip()

        if not line or line.startswith("#"):
            continue

        # IF condition
        if re.fullmatch(CONDITION, line):

            block_stack.append(False)
            continue

        # ELSE
        if line == "warna":

            if not block_stack:
                raise SyntaxError(
                    f"'warna' without 'agar' at line {line_number}"
                )

            if block_stack[-1]:
                raise SyntaxError(
                    f"Duplicate 'warna' at line {line_number}"
                )

            block_stack[-1] = True
            continue

        # END IF
        if line == "khatam":

            if not block_stack:
                raise SyntaxError(
                    f"Unexpected 'khatam' at line {line_number}"
                )

            block_stack.pop()
            continue

        if re.match(r"^(agar|warna|khatam)\b", line):
            raise SyntaxError(
                f"Invalid conditional syntax at line {line_number}: {line}"
            )

        # Variable declarations
        if re.fullmatch(DECLARATION, line):
            continue

        # String printing
        if re.fullmatch(rf"{STRING}\s+dikhao", line):
            continue

        # Multiple variable printing
        if re.fullmatch(
            rf"{IDENTIFIER}(?:\s+aur\s+{IDENTIFIER})+\s+dikhao",
            line
        ):
            continue

        # Single variable printing
        if re.fullmatch(rf"{IDENTIFIER}\s+dikhao", line):
            continue

        # Old print syntax
        if re.fullmatch(rf"print\s+karo\s+{IDENTIFIER}", line):
            continue

        # Roman Urdu addition
        if re.fullmatch(
            rf"{IDENTIFIER}\s+aur\s+{IDENTIFIER}\s+ko\s+jama\s+karo",
            line
        ):
            continue

        # Direct assignment
        if re.fullmatch(ASSIGNMENT, line):
            continue

        raise SyntaxError(
            f"Invalid syntax at line {line_number}: {line}"
        )

    if block_stack:
        raise SyntaxError(
            "Missing 'khatam': If block is not closed."
        )

    return "Syntax is correct!"