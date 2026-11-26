from lexer import tokenize
from python_generator import generate_python_code
from parser import syntax_check
from semantic import semantic_check
from code_generator import generate_intermediate_code

code = """
number lo a
number lo b
sum = a + b
print karo sum
"""

print("===== ROMANCODE COMPILER =====")

# Phase 1
tokens = tokenize(code)

print("\n1. LEXICAL ANALYSIS")

for token in tokens:
    print(token)

# Phase 2
print("\n2. SYNTAX ANALYSIS")

print(syntax_check(code))

# Phase 3
print("\n3. SEMANTIC ANALYSIS")

symbol_table = semantic_check(code)

for variable, data_type in symbol_table.items():
    print(variable, ":", data_type)

# Phase 4
print("\n4. INTERMEDIATE CODE GENERATION")

tac = generate_intermediate_code(code)

for instruction in tac:
    print(instruction)
    print("\n5. PYTHON CODE GENERATION")

generated_code = generate_python_code(code)

print(generated_code)

print("\n6. PROGRAM EXECUTION")

print("Running RomanCode Program...\n")

exec(generated_code)