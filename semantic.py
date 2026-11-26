import re

IDENTIFIER = r"[A-Za-z_]\w*"
STRING = r'''(?:"[^"\n]*"|'[^'\n]*')'''

CONDITION = (
    rf"agar\s+({IDENTIFIER})\s+"
    rf"(-?\d+(?:\.\d+)?)\s+se\s+"
    r"(bara|chota|barabar)\s+ho"
)

RESERVED = {
    "aur", "agar", "warna", "khatam", "lo",
    "dikhao", "jama", "karo", "ko", "number",
    "text", "print", "se", "ho", "bara",
    "chota", "barabar", "jabtak"
}


def semantic_check(code):

    symbol_table = {}

    def check_variable(variable, line_number):

        if variable in RESERVED:
            raise Exception(
                f"'{variable}' is a reserved word at line {line_number}"
            )

        if variable in symbol_table:
            raise Exception(
                f"Variable '{variable}' already declared at line {line_number}"
            )

    def require_variable(variable, line_number):

        if variable not in symbol_table:
            raise Exception(
                f"Variable '{variable}' is not declared at line {line_number}"
            )

    def numeric_type(variable, line_number):

        require_variable(variable, line_number)

        if symbol_table[variable] not in ("Integer", "Float"):
            raise Exception(
                f"Variable '{variable}' must be numeric at line {line_number}"
            )

    for line_number, original in enumerate(code.splitlines(), 1):

        line = original.strip()

        if not line or line.startswith("#"):
            continue

        # IF condition
        match = re.fullmatch(CONDITION, line)

        if match:

            variable, value, operator = match.groups()
            numeric_type(variable, line_number)
            continue

        # ELSE / END
        if line in ("warna", "khatam"):
            continue

        # Integer input
        match = re.fullmatch(rf"({IDENTIFIER})\s+lo", line)

        if match:

            variable = match.group(1)
            check_variable(variable, line_number)
            symbol_table[variable] = "Integer"
            continue

        # Old integer declaration
        match = re.fullmatch(
            rf"number\s+lo\s+({IDENTIFIER})",
            line
        )

        if match:

            variable = match.group(1)
            check_variable(variable, line_number)
            symbol_table[variable] = "Integer"
            continue

        # Text input
        match = re.fullmatch(
            rf"text\s+lo\s+({IDENTIFIER})",
            line
        )

        if match:

            variable = match.group(1)
            check_variable(variable, line_number)
            symbol_table[variable] = "String"
            continue

        # Direct string print
        if re.fullmatch(rf"{STRING}\s+dikhao", line):
            continue

        # Multiple variable print
        match = re.fullmatch(
            rf"({IDENTIFIER}(?:\s+aur\s+{IDENTIFIER})+)\s+dikhao",
            line
        )

        if match:

            variables = re.split(r"\s+aur\s+", match.group(1))

            for variable in variables:
                require_variable(variable, line_number)

            continue

        # Addition
        match = re.fullmatch(
            rf"({IDENTIFIER})\s+aur\s+({IDENTIFIER})\s+ko\s+jama\s+karo",
            line
        )

        if match:

            first, second = match.groups()

            numeric_type(first, line_number)
            numeric_type(second, line_number)

            symbol_table["jawab"] = (
                "Float"
                if "Float" in (symbol_table[first], symbol_table[second])
                else "Integer"
            )
            continue

        # Assignment
        match = re.fullmatch(
            rf"({IDENTIFIER})\s*=\s*(.+)",
            line
        )

        if match:

            variable, expression = match.groups()

            if variable in RESERVED:
                raise Exception(
                    f"'{variable}' is a reserved word at line {line_number}"
                )

            if re.fullmatch(r"-?\d+", expression):
                symbol_table[variable] = "Integer"
                continue

            if re.fullmatch(r"-?\d+\.\d+", expression):
                symbol_table[variable] = "Float"
                continue

            if re.fullmatch(STRING, expression):
                symbol_table[variable] = "String"
                continue

            addition = re.fullmatch(
                rf"({IDENTIFIER})\s*\+\s*({IDENTIFIER})",
                expression
            )

            if addition:

                first, second = addition.groups()

                numeric_type(first, line_number)
                numeric_type(second, line_number)

                symbol_table[variable] = (
                    "Float"
                    if "Float" in (symbol_table[first], symbol_table[second])
                    else "Integer"
                )
                continue

            if re.fullmatch(IDENTIFIER, expression):

                require_variable(expression, line_number)
                symbol_table[variable] = symbol_table[expression]
                continue

            raise Exception(
                f"Invalid assignment at line {line_number}: {line}"
            )

        # Single variable print
        match = re.fullmatch(
            rf"({IDENTIFIER})\s+dikhao",
            line
        )

        if match:
            require_variable(match.group(1), line_number)
            continue

        # Old print
        match = re.fullmatch(
            rf"print\s+karo\s+({IDENTIFIER})",
            line
        )

        if match:
            require_variable(match.group(1), line_number)
            continue

        raise Exception(
            f"Invalid semantic statement at line {line_number}: {line}"
        )

    return symbol_table