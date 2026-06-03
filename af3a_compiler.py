KEYWORDS = {
    "sahih",
    "kasr",
    "kalema",
    "manteq",
    "etha",
    "aw",
    "talama",
    "itba3",
    "da5el",
    "shoghol",
    "lkol",
    "waqef",
    "kammel",
    "raje3",
    "sa7",
    "ghalat"
}


TOKEN_TYPES = {
    "KEYWORD",
    "IDENTIFIER",
    "INTEGER",
    "FLOAT",
    "STRING",
    "OPERATOR",
    "SEMICOLON",
    "COMMA",
    "LPAREN",   # (
    "RPAREN",   # )
    "LBRACE",   # {
    "RBRACE"    # }
}


import re

class Token:
    def __init__(self, token_type, value, line, column):
        self.token_type = token_type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"{self.token_type}('{self.value}') at line {self.line}, column {self.column}"


def lexer(code):
    tokens = []
    errors = []

    token_patterns = [
        ("FLOAT", r"\d+\.\d+"),
        ("INTEGER", r"\d+"),
        ("STRING", r'"[^"]*"'),
        ("OPERATOR", r"==|!=|<=|>=|&&|\|\||[+\-*/%=<>!]"),
        ("SEMICOLON", r";"),
        ("LPAREN", r"\("),
        ("RPAREN", r"\)"),
        ("LBRACE", r"\{"),
        ("RBRACE", r"\}"),
        ("COMMA", r","),
        ("IDENTIFIER", r"[a-zA-Z_][a-zA-Z0-9_]*"),
        ("NEWLINE", r"\n"),
        ("SKIP", r"[ \t]+"),
        ("MISMATCH", r".")
    ]

    combined_regex = "|".join(
        f"(?P<{name}>{pattern})" for name, pattern in token_patterns
    )

    line = 1
    line_start = 0

    for match in re.finditer(combined_regex, code):
        token_type = match.lastgroup
        value = match.group()
        column = match.start() - line_start + 1

        if token_type == "NEWLINE":
            line += 1
            line_start = match.end()

        elif token_type == "SKIP":
            continue

        elif token_type == "MISMATCH":
            errors.append(
                f"Lexical Error at line {line}, column {column}: Invalid character '{value}'"
            )

        else:
            if token_type == "IDENTIFIER"and value in KEYWORDS:
                token_type = "KEYWORD"

            tokens.append(Token(token_type, value, line, column))

    tokens.append(Token("EOF", "EOF", line, 1))

    return tokens, errors