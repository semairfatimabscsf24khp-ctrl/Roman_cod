
import re

IDENTIFIER = r"[A-Za-z_]\w*"


def generate_intermediate_code(code):

    result = []
    temp_count = 1

    def new_temp():
        nonlocal temp_count
        temp = f"t{temp_count}"
        temp_count += 1
        return temp

    for original in code.splitlines():

        line = original.strip()

        if not line or line.startswith("#"):
            continue

        # IF condition
        match = re.fullmatch(
            rf"agar\s+({IDENTIFIER})\s+(-?\d+(?:\.\d+)?)\s+se\s+(bara|chota|barabar)\s+ho",
            line
        )

        if match:
            variable, value, operator = match.groups()

            operators = {
                "bara": ">",
                "chota": "<",
                "barabar": "=="
            }

            result.append(
                f"IF {variable} {operators[operator]} {value} GOTO"
            )
            continue

        if line == "warna":
            result.append("ELSE:")
            continue

        if line == "khatam":
            result.append("ENDIF")
            continue

        # Addition
        match = re.fullmatch(
            rf"({IDENTIFIER})\s+aur\s+({IDENTIFIER})\s+ko\s+jama\s+karo",
            line
        )

        if match:
            first, second = match.groups()
            temp = new_temp()
            result.append(f"{temp} = {first} + {second}")
            result.append(f"jawab = {temp}")
            continue

        # Assignment
        match = re.fullmatch(
            rf"({IDENTIFIER})\s*=\s*(.+)",
            line
        )

        if match:
            variable, expression = match.groups()
            result.append(f"{variable} = {expression}")
            continue

        # Input
        match = re.fullmatch(
            rf"(?:number|text)\s+lo\s+({IDENTIFIER})|({IDENTIFIER})\s+lo",
            line
        )

        if match:
            variable = match.group(1) or match.group(2)
            result.append(f"READ {variable}")
            continue

        # Print
        match = re.fullmatch(
            rf"({IDENTIFIER})\s+dikhao",
            line
        )

        if match:
            result.append(f"PRINT {match.group(1)}")
            continue

        # String print
        match = re.fullmatch(
            r"""("[^"]*"|'[^']*')\s+dikhao""",
            line
        )

        if match:
            result.append(f"PRINT {match.group(1)}")
            continue

    return result
