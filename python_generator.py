import re



IDENTIFIER = r"[A-Za-z_]\w*"
STRING = r'''(?:"[^"\n]*"|'[^'\n]*')'''

CONDITION = (
    rf"agar\s+({IDENTIFIER})\s+"
    rf"(-?\d+(?:\.\d+)?)\s+se\s+"
    r"(bara|chota|barabar)\s+ho"
)


def generate_python_code(code):

    result = []
    block_stack = []

    operators = {
        "bara": ">",
        "chota": "<",
        "barabar": "=="
    }

    for line_number, original in enumerate(code.splitlines(), 1):

        line = original.strip()

        if not line or line.startswith("#"):
            continue

        indentation = "    " * len(block_stack)

        # IF
        match = re.fullmatch(CONDITION, line)

        if match:

            variable, value, word = match.groups()

            result.append(
                f"{indentation}if {variable} {operators[word]} {value}:"
            )

            block_stack.append(False)
            continue

        # ELSE
        if line == "warna":

            if not block_stack or block_stack[-1]:
                raise Exception(
                    f"Invalid warna at line {line_number}"
                )

            result.append(
                "    " * (len(block_stack) - 1) + "else:"
            )

            block_stack[-1] = True
            continue

        # END IF
        if line == "khatam":

            if not block_stack:
                raise Exception(
                    f"Unexpected khatam at line {line_number}"
                )

            block_stack.pop()
            continue

        indentation = "    " * len(block_stack)

        # Input
        match = re.fullmatch(rf"({IDENTIFIER})\s+lo", line)

        if match:

            variable = match.group(1)

            result.append(
                f"{indentation}{variable} = int(input('Enter {variable}: '))"
            )
            continue

        # Old integer input
        match = re.fullmatch(
            rf"number\s+lo\s+({IDENTIFIER})",
            line
        )

        if match:

            variable = match.group(1)

            result.append(
                f"{indentation}{variable} = int(input('Enter {variable}: '))"
            )
            continue

        # Text input
        match = re.fullmatch(
            rf"text\s+lo\s+({IDENTIFIER})",
            line
        )

        if match:

            variable = match.group(1)

            result.append(
                f"{indentation}{variable} = input('Enter {variable}: ')"
            )
            continue

        # String print
        match = re.fullmatch(
            rf"({STRING})\s+dikhao",
            line
        )

        if match:

            result.append(
                f"{indentation}print({match.group(1)})"
            )
            continue

        # Multiple variable print
        match = re.fullmatch(
            rf"({IDENTIFIER}(?:\s+aur\s+{IDENTIFIER})+)\s+dikhao",
            line
        )

        if match:

            variables = re.split(r"\s+aur\s+", match.group(1))

            for variable in variables:
                result.append(
                    f"{indentation}print({variable})"
                )

            continue

        # Roman Urdu addition
        match = re.fullmatch(
            rf"({IDENTIFIER})\s+aur\s+({IDENTIFIER})\s+ko\s+jama\s+karo",
            line
        )

        if match:

            first, second = match.groups()

            result.append(
                f"{indentation}jawab = {first} + {second}"
            )
            continue

        # Variable print
        match = re.fullmatch(
            rf"({IDENTIFIER})\s+dikhao",
            line
        )

        if match:

            result.append(
                f"{indentation}print({match.group(1)})"
            )
            continue

        # Old print
        match = re.fullmatch(
            rf"print\s+karo\s+({IDENTIFIER})",
            line
        )

        if match:

            result.append(
                f"{indentation}print({match.group(1)})"
            )
            continue

        # Direct assignment
        match = re.fullmatch(
            rf"({IDENTIFIER})\s*=\s*(.+)",
            line
        )

        if match:

            variable, expression = match.groups()

            valid = (
                re.fullmatch(r"-?\d+(?:\.\d+)?", expression)
                or re.fullmatch(STRING, expression)
                or re.fullmatch(
                    rf"{IDENTIFIER}\s*[+\-*/]\s*{IDENTIFIER}",
                    expression
                )
                or re.fullmatch(IDENTIFIER, expression)
            )

            if not valid:
                raise Exception(
                    f"Invalid assignment at line {line_number}: {line}"
                )

            result.append(
                f"{indentation}{variable} = {expression}"
            )
            continue

        raise Exception(
            f"Cannot generate Python code at line {line_number}: {line}"
        )

    if block_stack:
        raise Exception("Missing khatam in if block")

    return "\n".join(result)