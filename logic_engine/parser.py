"""
logic_engine/parser.py
Recursive descent parser for First-Order Predicate Logic (FOPL) Formulas.
Grammar:
  formula        := quantified | iff_expr
  quantified     := ('forall' | 'exists') IDENTIFIER (',' IDENTIFIER)* ':' formula
  iff_expr       := implies_expr ('<->' implies_expr)*
  implies_expr   := or_expr ('->' implies_expr)?
  or_expr        := and_expr ('|' and_expr)*
  and_expr       := unary_expr ('&' unary_expr)*
  unary_expr     := ('~') unary_expr | primary_expr
  primary_expr   := '(' formula ')' | predicate
  predicate      := IDENTIFIER ('(' (term (',' term)*)? ')')?
  term           := IDENTIFIER ('(' (term (',' term)*)? ')')?
"""

from typing import List, Set, Optional
from logic_engine.lexer import Lexer, Token, TokenType
from logic_engine.ast import (
    Formula, Predicate, Not, And, Or, Implies, Iff, Forall, Exists,
    Term, Variable, Constant, FunctionTerm
)


class ParseError(Exception):
    def __init__(self, message: str, position: int = 0):
        super().__init__(f"Parse Error at pos {position}: {message}")
        self.position = position


class Parser:
    """Parses a sequence of tokens into a Formula AST."""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.bound_vars: Set[str] = set()

    def current(self) -> Token:
        return self.tokens[self.pos]

    def peek(self) -> Token:
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1]
        return self.tokens[-1]

    def advance(self) -> Token:
        tok = self.current()
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return tok

    def match(self, expected_type: str) -> bool:
        if self.current().type == expected_type:
            self.advance()
            return True
        return False

    def expect(self, expected_type: str, err_msg: Optional[str] = None) -> Token:
        cur = self.current()
        if cur.type != expected_type:
            msg = err_msg or f"Expected token {expected_type}, but found {cur.type} ('{cur.value}')"
            raise ParseError(msg, cur.position)
        return self.advance()

    def parse(self) -> Formula:
        expr = self.parse_formula()
        if self.current().type != TokenType.EOF:
            raise ParseError(f"Unexpected trailing tokens starting with '{self.current().value}'", self.current().position)
        return expr

    def parse_formula(self) -> Formula:
        cur = self.current()
        if cur.type in (TokenType.FORALL, TokenType.EXISTS):
            return self.parse_quantified()
        return self.parse_iff()

    def parse_quantified(self) -> Formula:
        q_tok = self.advance()
        is_forall = (q_tok.type == TokenType.FORALL)

        var_names: List[str] = []
        first_var = self.expect(TokenType.IDENTIFIER, "Expected variable name after quantifier").value
        var_names.append(first_var)

        while self.match(TokenType.COMMA):
            v = self.expect(TokenType.IDENTIFIER, "Expected variable name after comma in quantifier").value
            var_names.append(v)

        # Optional colon or dot: forall x: or forall x.
        if self.current().type == TokenType.COLON:
            self.advance()

        # Add to bound variables context for term parsing
        for v in var_names:
            self.bound_vars.add(v)

        body = self.parse_formula()

        # Wrap multiple quantified variables right-to-left:
        # forall x, y: P(x, y) => forall x: (forall y: P(x, y))
        res = body
        for v in reversed(var_names):
            if is_forall:
                res = Forall(v, res)
            else:
                res = Exists(v, res)

        return res

    def parse_iff(self) -> Formula:
        expr = self.parse_implies()
        while self.match(TokenType.IFF):
            right = self.parse_implies()
            expr = Iff(expr, right)
        return expr

    def parse_implies(self) -> Formula:
        expr = self.parse_or()
        if self.match(TokenType.IMPLIES):
            # Implication is right-associative: A -> B -> C is A -> (B -> C)
            right = self.parse_implies()
            return Implies(expr, right)
        return expr

    def parse_or(self) -> Formula:
        expr = self.parse_and()
        while self.match(TokenType.OR):
            right = self.parse_and()
            expr = Or(expr, right)
        return expr

    def parse_and(self) -> Formula:
        expr = self.parse_unary()
        while self.match(TokenType.AND):
            right = self.parse_unary()
            expr = And(expr, right)
        return expr

    def parse_unary(self) -> Formula:
        if self.match(TokenType.NOT):
            operand = self.parse_unary()
            return Not(operand)
        return self.parse_primary()

    def parse_primary(self) -> Formula:
        cur = self.current()
        if self.match(TokenType.LPAREN):
            expr = self.parse_formula()
            self.expect(TokenType.RPAREN, "Expected closing parenthesis ')'")
            return expr

        if cur.type in (TokenType.FORALL, TokenType.EXISTS):
            return self.parse_quantified()

        if cur.type == TokenType.IDENTIFIER:
            return self.parse_predicate()

        raise ParseError(f"Unexpected token in formula: {cur.type} ('{cur.value}')", cur.position)

    def parse_predicate(self) -> Predicate:
        name_tok = self.expect(TokenType.IDENTIFIER)
        pred_name = name_tok.value
        args: List[Term] = []

        if self.match(TokenType.LPAREN):
            if self.current().type != TokenType.RPAREN:
                args.append(self.parse_term())
                while self.match(TokenType.COMMA):
                    args.append(self.parse_term())
            self.expect(TokenType.RPAREN, f"Expected ')' closing arguments of predicate '{pred_name}'")

        return Predicate(pred_name, args)

    def parse_term(self) -> Term:
        name_tok = self.expect(TokenType.IDENTIFIER, "Expected term (variable, constant, or function)")
        name = name_tok.value

        # Check if function call
        if self.match(TokenType.LPAREN):
            f_args: List[Term] = []
            if self.current().type != TokenType.RPAREN:
                f_args.append(self.parse_term())
                while self.match(TokenType.COMMA):
                    f_args.append(self.parse_term())
            self.expect(TokenType.RPAREN, f"Expected ')' closing function '{name}'")
            return FunctionTerm(name, f_args)

        # Variable vs Constant classification:
        # 1. If in bound_vars, it is definitely a variable.
        # 2. If starts with lowercase letter or underscore, treat as variable (standard FOL).
        # 3. If starts with uppercase or digit, treat as constant.
        if name in self.bound_vars or (name[0].islower() or name[0] == '_'):
            return Variable(name)
        else:
            return Constant(name)


def parse_fopl(formula_str: str) -> Formula:
    """Convenience helper to lex and parse a FOPL string into an AST Formula."""
    tokens = Lexer(formula_str).tokenize()
    return Parser(tokens).parse()

