"""
logic_engine/lexer.py
Tokenizer for First-Order Predicate Logic (FOPL) Well-Formed Formulas.
"""

from typing import List, NamedTuple
import re


class TokenType:
    FORALL = "FORALL"          # forall, ∀
    EXISTS = "EXISTS"          # exists, ∃
    NOT = "NOT"                # ~, not, !, ¬
    AND = "AND"                # &, and, ∧
    OR = "OR"                  # |, or, ∨
    IMPLIES = "IMPLIES"        # ->, =>, →, implies
    IFF = "IFF"                # <->, <=>, ↔, iff
    LPAREN = "LPAREN"          # (
    RPAREN = "RPAREN"          # )
    COMMA = "COMMA"            # ,
    COLON = "COLON"            # :
    IDENTIFIER = "IDENTIFIER"  # Name of predicate, constant, variable, or function
    EOF = "EOF"


class Token(NamedTuple):
    type: str
    value: str
    position: int


class Lexer:
    """Tokenizes FOPL strings into a stream of tokens."""
    
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.length = len(text)

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []

        while self.pos < self.length:
            ch = self.text[self.pos]

            # Skip whitespace
            if ch.isspace():
                self.pos += 1
                continue

            start_pos = self.pos

            # Multicharacter symbols first
            if self.text.startswith("<->", self.pos) or self.text.startswith("<=>", self.pos):
                tokens.append(Token(TokenType.IFF, "<->", start_pos))
                self.pos += 3
                continue

            if self.text.startswith("->", self.pos) or self.text.startswith("=>", self.pos):
                tokens.append(Token(TokenType.IMPLIES, "->", start_pos))
                self.pos += 2
                continue

            # Unicode single-char logic symbols
            if ch == '∀':
                tokens.append(Token(TokenType.FORALL, "forall", start_pos))
                self.pos += 1
                continue

            if ch == '∃':
                tokens.append(Token(TokenType.EXISTS, "exists", start_pos))
                self.pos += 1
                continue

            if ch in ('¬', '~', '!'):
                tokens.append(Token(TokenType.NOT, "~", start_pos))
                self.pos += 1
                continue

            if ch in ('∧', '&'):
                tokens.append(Token(TokenType.AND, "&", start_pos))
                self.pos += 1
                continue

            if ch in ('∨', '|'):
                tokens.append(Token(TokenType.OR, "|", start_pos))
                self.pos += 1
                continue

            if ch == '→':
                tokens.append(Token(TokenType.IMPLIES, "->", start_pos))
                self.pos += 1
                continue

            if ch == '↔':
                tokens.append(Token(TokenType.IFF, "<->", start_pos))
                self.pos += 1
                continue

            if ch == '(':
                tokens.append(Token(TokenType.LPAREN, "(", start_pos))
                self.pos += 1
                continue

            if ch == ')':
                tokens.append(Token(TokenType.RPAREN, ")", start_pos))
                self.pos += 1
                continue

            if ch == ',':
                tokens.append(Token(TokenType.COMMA, ",", start_pos))
                self.pos += 1
                continue

            if ch == ':':
                tokens.append(Token(TokenType.COLON, ":", start_pos))
                self.pos += 1
                continue

            # Words / Identifiers / Keywords
            if ch.isalnum() or ch == '_':
                ident_match = re.match(r'[A-Za-z0-9_]+', self.text[self.pos:])
                if ident_match:
                    ident = ident_match.group(0)
                    self.pos += len(ident)
                    lower_ident = ident.lower()

                    if lower_ident == "forall":
                        tokens.append(Token(TokenType.FORALL, "forall", start_pos))
                    elif lower_ident == "exists":
                        tokens.append(Token(TokenType.EXISTS, "exists", start_pos))
                    elif lower_ident in ("not",):
                        tokens.append(Token(TokenType.NOT, "~", start_pos))
                    elif lower_ident in ("and",):
                        tokens.append(Token(TokenType.AND, "&", start_pos))
                    elif lower_ident in ("or",):
                        tokens.append(Token(TokenType.OR, "|", start_pos))
                    elif lower_ident in ("implies",):
                        tokens.append(Token(TokenType.IMPLIES, "->", start_pos))
                    elif lower_ident in ("iff",):
                        tokens.append(Token(TokenType.IFF, "<->", start_pos))
                    else:
                        tokens.append(Token(TokenType.IDENTIFIER, ident, start_pos))
                    continue

            # Unrecognized character
            raise ValueError(f"Unexpected character '{ch}' at position {self.pos} in '{self.text}'")

        tokens.append(Token(TokenType.EOF, "", self.pos))
        return tokens

