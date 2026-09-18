import re

with open('manuscript_marked.tex', 'r') as f:
    manuscript = f.read()

with open('Response_letter_clean.tex', 'r') as f:
    response = f.read()

print("--- MANUSCRIPT MARKED CHANGES ---")
# Extract all {\color{revcolor}...}
marked_changes = []
# It's tricky to parse nested braces with regex, but we can do a simple search
# A better way is to find \color{revcolor} and then just print the surrounding text
lines = manuscript.split('\n')
for i, line in enumerate(lines):
    if 'color{revcolor}' in line:
        print(f"Line {i+1}: {line.strip()[:150]}...")

print("\n--- RESPONSE LETTER CLAIMS ---")
lines = response.split('\n')
for i, line in enumerate(lines):
    if '\\manuscriptchange' in line:
        print(f"Line {i+1}: {line.strip()}")

