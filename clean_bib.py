import re

def clean_bib(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replacements
    replacements = {
        '₃': '$_3$',
        '₂': '$_2$',
        '₁': '$_1$',
        '₄': '$_4$',
        '₅': '$_5$',
        '₆': '$_6$',
        '₇': '$_7$',
        '₈': '$_8$',
        '₉': '$_9$',
        '₀': '$_0$',
        'µ': r'$\mu$',
        'Å': r'\AA{}',
        'é': r"\'{e}",
        'á': r"\'{a}",
        'í': r"\'{i}",
        'ó': r"\'{o}",
        'ú': r"\'{u}",
        'ñ': r'\~{n}',
        '—': '--', # Em-dash
        '–': '-',  # En-dash
        '“': "``",
        '”': "''",
        '’': "'",
        '‘': "`",
        '\u2062': '', # Invisible times
    }

    for k, v in replacements.items():
        content = content.replace(k, v)

    # Remove non-ASCII remaining characters if any (or replace them with space)
    # Actually, let's just do a blanket ASCII conversion for safety
    # But keep the common ones we fixed.

    with open(filename, 'w', encoding='ascii', errors='replace') as f:
        f.write(content)

if __name__ == '__main__':
    clean_bib('CMS_Final_Submission/references.bib')
