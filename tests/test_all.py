"""
tests/test_all.py
Comprehensive test suite verifying Module II requirements:
Knowledge Representation, FOPL, WFF to CNF 9-step pipeline, Robinson Unification,
and Resolution Refutation.
"""

import unittest
from logic_engine.ast import (
    Variable, Constant, FunctionTerm, Predicate, Literal, Clause,
    Not, And, Or, Implies, Iff, Forall, Exists
)
from logic_engine.lexer import Lexer, TokenType
from logic_engine.parser import Parser, parse_fopl
from logic_engine.cnf_converter import CNFConverter
from logic_engine.unifier import (
    unify_terms, unify_predicates, unify_complementary_literals,
    occurs_check, format_substitution
)
from logic_engine.resolution import ResolutionProver
from logic_engine.clause_translator import ClauseTranslator
from logic_engine.presets import CONTRACT_PRESETS
from logic_engine.auditor import ContractAuditor


class TestModuleIIEngine(unittest.TestCase):

    def test_lexer_tokens(self):
        text = "forall x, y: (Confidential(x) & Disclose(y, x) -> ~Permitted(y))"
        tokens = Lexer(text).tokenize()
        types = [t.type for t in tokens]
        self.assertIn(TokenType.FORALL, types)
        self.assertIn(TokenType.IDENTIFIER, types)
        self.assertIn(TokenType.AND, types)
        self.assertIn(TokenType.IMPLIES, types)
        self.assertIn(TokenType.NOT, types)

    def test_parser_ast(self):
        formula = parse_fopl("forall r: (Recipient(r) -> exists d: Data(d))")
        self.assertIsInstance(formula, Forall)
        self.assertEqual(formula.var_name, "r")
        self.assertIsInstance(formula.body, Implies)
        self.assertIsInstance(formula.body.right, Exists)

    def test_cnf_conversion_9_steps(self):
        f = parse_fopl("forall x: (Employee(x) -> exists y: (Manager(y) & ReportsTo(x, y)))")
        converter = CNFConverter()
        clauses, steps = converter.convert_with_steps(f)
        self.assertEqual(len(steps), 10) # Step 0 to Step 9
        self.assertEqual(steps[1].name, "Eliminate Biconditionals")
        self.assertEqual(steps[2].name, "Eliminate Implications")
        self.assertEqual(steps[3].name, "Move Negations Inward (NNF)")
        self.assertEqual(steps[4].name, "Standardize Bound Variables")
        self.assertEqual(steps[5].name, "Skolemization")
        self.assertEqual(steps[6].name, "Drop Universal Quantifiers")
        self.assertEqual(steps[7].name, "Distribute Disjunctions over Conjunctions")
        self.assertEqual(steps[8].name, "Extract Clause Set")
        self.assertEqual(steps[9].name, "Standardize Variables Across Clauses")
        self.assertEqual(len(clauses), 2)

    def test_robinson_unification(self):
        # Permitted(x, ApexDev) and ~Permitted(BetaCorp, y)
        l1 = Literal(Predicate("Permitted", [Variable("x"), Constant("ApexDev")]), is_negated=False)
        l2 = Literal(Predicate("Permitted", [Constant("BetaCorp"), Variable("y")]), is_negated=True)
        theta = unify_complementary_literals(l1, l2)
        self.assertIsNotNone(theta)
        self.assertEqual(str(theta["x"]), "BetaCorp")
        self.assertEqual(str(theta["y"]), "ApexDev")

    def test_occurs_check(self):
        x = Variable("x")
        fx = FunctionTerm("f", [x])
        res = unify_terms(x, fx)
        self.assertIsNone(res, "Occurs check must reject recursive unification x = f(x)")

    def test_resolution_refutation_simple(self):
        # KB: A, A -> B, ~B  =>  contradiction []
        conv = CNFConverter()
        c1, _ = conv.convert_with_steps(parse_fopl("A()"), "C1")
        c2, _ = conv.convert_with_steps(parse_fopl("A() -> B()"), "C2")
        c3, _ = conv.convert_with_steps(parse_fopl("~B()"), "C3")
        prover = ResolutionProver()
        res = prover.prove(c1 + c2 + c3)
        self.assertTrue(res.success)
        self.assertIsNotNone(res.empty_clause_id)

    def test_clause_translator_nlp(self):
        translator = ClauseTranslator()
        res = translator.translate("Recipient may disclose confidential information to any contractor who signed an NDA")
        self.assertTrue(res["matched"])
        self.assertIn("PermittedToDisclose", res["fopl"])

    def test_all_contract_presets(self):
        auditor = ContractAuditor()
        for preset in CONTRACT_PRESETS:
            res = auditor.audit_contract_preset(preset)
            self.assertTrue(res["conflict_audit"]["proof"]["success"], f"Conflict proof failed for {preset['title']}")
            self.assertTrue(res["breach_audit"]["proof"]["success"], f"Breach proof failed for {preset['title']}")
            self.assertGreaterEqual(res["risk_score"], 80)


if __name__ == "__main__":
    unittest.main()

