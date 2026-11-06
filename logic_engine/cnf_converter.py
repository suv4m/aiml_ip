"""
logic_engine/cnf_converter.py
Complete 9-Step WFF to Clausal Form (CNF) Conversion Pipeline.
Implements the formal algorithm from Module II (Knowledge Representation & Logic).
Captures detailed audit logs and explanations for every transformation step.
"""

from typing import List, Dict, Set, Tuple, Any, Optional
import copy

from logic_engine.ast import (
    Formula, Predicate, Not, And, Or, Implies, Iff, Forall, Exists,
    Term, Variable, Constant, FunctionTerm,
    Literal, Clause
)


class ConversionStep:
    """Records the state of the formula at each stage of clausal conversion."""
    def __init__(self, step_num: int, name: str, description: str, formula_str: str, formula: Optional[Formula] = None, clauses: Optional[List[Clause]] = None):
        self.step_num = step_num
        self.name = name
        self.description = description
        self.formula_str = formula_str
        self.formula = formula
        self.clauses = clauses or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_num": self.step_num,
            "name": self.name,
            "description": self.description,
            "formula_str": self.formula_str,
            "clauses": [c.to_dict() for c in self.clauses] if self.clauses else []
        }


class CNFConverter:
    """Converts First-Order Logic Formulas (WFF) into Clausal Form (CNF)."""

    def __init__(self):
        self.skolem_const_counter = 0
        self.skolem_func_counter = 0
        self.var_counter = 0

    def convert_with_steps(self, formula: Formula, clause_prefix: str = "C", source_text: str = "") -> Tuple[List[Clause], List[ConversionStep]]:
        """
        Executes the 9-step conversion pipeline and returns:
          1. The resulting list of Clause objects (standardized apart)
          2. The list of ConversionStep objects recording each step.
        """
        steps: List[ConversionStep] = []

        # Step 0: Initial WFF
        f0 = copy.deepcopy(formula)
        steps.append(ConversionStep(
            0,
            "Initial Well-Formed Formula (WFF)",
            "The original input first-order logic statement.",
            str(f0),
            f0
        ))

        # Step 1: Eliminate Biconditionals (<->)
        f1 = self.eliminate_iff(f0)
        steps.append(ConversionStep(
            1,
            "Eliminate Biconditionals",
            "Replace (P <-> Q) with ((P -> Q) & (Q -> P)).",
            str(f1),
            f1
        ))

        # Step 2: Eliminate Implications (->)
        f2 = self.eliminate_implies(f1)
        steps.append(ConversionStep(
            2,
            "Eliminate Implications",
            "Replace (P -> Q) with (~P | Q).",
            str(f2),
            f2
        ))

        # Step 3: Move Negation Inwards (NNF via De Morgan & Quantifier Duality)
        f3 = self.push_negation(f2)
        steps.append(ConversionStep(
            3,
            "Move Negations Inward (NNF)",
            "Apply De Morgan's laws (~(P&Q) => ~P|~Q, ~(P|Q) => ~P&~Q), double negation (~~P => P), and quantifier negation (~forall x: P => exists x: ~P, ~exists x: P => forall x: ~P).",
            str(f3),
            f3
        ))

        # Step 4: Standardize Bound Variables Apart
        f4 = self.standardize_variables(f3)
        steps.append(ConversionStep(
            4,
            "Standardize Bound Variables",
            "Rename bound variables so each quantifier binds a unique identifier across the formula.",
            str(f4),
            f4
        ))

        # Step 5: Skolemization (Eliminate Existential Quantifiers)
        f5 = self.skolemize(f4, universal_vars=[])
        steps.append(ConversionStep(
            5,
            "Skolemization",
            "Eliminate existential quantifiers (exists x). If enclosed in forall u1..un, replace with Skolem function f(u1..un); if outside any forall, replace with Skolem constant c.",
            str(f5),
            f5
        ))

        # Step 6: Drop Universal Quantifiers
        f6 = self.drop_universal(f5)
        steps.append(ConversionStep(
            6,
            "Drop Universal Quantifiers",
            "Remove all universal quantifier prefixes (forall x:). All free variables are now implicitly universally quantified.",
            str(f6),
            f6
        ))

        # Step 7: Distribute OR over AND (CNF)
        f7 = self.distribute_or_over_and(f6)
        steps.append(ConversionStep(
            7,
            "Distribute Disjunctions over Conjunctions",
            "Apply the distributive law: A | (B & C) => (A | B) & (A | C) to convert into pure Conjunctive Normal Form (CNF).",
            str(f7),
            f7
        ))

        # Step 8: Extract Clauses
        extracted_clauses = self.extract_clauses(f7, source_text=source_text)
        steps.append(ConversionStep(
            8,
            "Extract Clause Set",
            "Split the top-level conjunctions into a set of distinct clauses, each consisting of a disjunction of literals.",
            " { " + ", ".join(f"[{str(c)}]" for c in extracted_clauses) + " }",
            clauses=extracted_clauses
        ))

        # Step 9: Standardize Variables Apart per Clause
        final_clauses = self.standardize_clauses_apart(extracted_clauses, prefix=clause_prefix)
        steps.append(ConversionStep(
            9,
            "Standardize Variables Across Clauses",
            "Rename variables in each clause independently (e.g. x -> x_1, y -> y_1) to prevent unwanted variable coupling during unification.",
            " { " + ", ".join(f"{c.clause_id}: [{str(c)}]" for c in final_clauses) + " }",
            clauses=final_clauses
        ))

        return final_clauses, steps

    # --- Step 1: Eliminate Biconditionals ---
    def eliminate_iff(self, formula: Formula) -> Formula:
        if isinstance(formula, Iff):
            left = self.eliminate_iff(formula.left)
            right = self.eliminate_iff(formula.right)
            return And(Implies(left, right), Implies(right, left))
        elif isinstance(formula, Implies):
            return Implies(self.eliminate_iff(formula.left), self.eliminate_iff(formula.right))
        elif isinstance(formula, And):
            return And(self.eliminate_iff(formula.left), self.eliminate_iff(formula.right))
        elif isinstance(formula, Or):
            return Or(self.eliminate_iff(formula.left), self.eliminate_iff(formula.right))
        elif isinstance(formula, Not):
            return Not(self.eliminate_iff(formula.operand))
        elif isinstance(formula, Forall):
            return Forall(formula.var_name, self.eliminate_iff(formula.body))
        elif isinstance(formula, Exists):
            return Exists(formula.var_name, self.eliminate_iff(formula.body))
        else:
            return copy.deepcopy(formula)

    # --- Step 2: Eliminate Implications ---
    def eliminate_implies(self, formula: Formula) -> Formula:
        if isinstance(formula, Implies):
            left = self.eliminate_implies(formula.left)
            right = self.eliminate_implies(formula.right)
            return Or(Not(left), right)
        elif isinstance(formula, And):
            return And(self.eliminate_implies(formula.left), self.eliminate_implies(formula.right))
        elif isinstance(formula, Or):
            return Or(self.eliminate_implies(formula.left), self.eliminate_implies(formula.right))
        elif isinstance(formula, Not):
            return Not(self.eliminate_implies(formula.operand))
        elif isinstance(formula, Forall):
            return Forall(formula.var_name, self.eliminate_implies(formula.body))
        elif isinstance(formula, Exists):
            return Exists(formula.var_name, self.eliminate_implies(formula.body))
        else:
            return copy.deepcopy(formula)

    # --- Step 3: Move Negation Inwards (NNF) ---
    def push_negation(self, formula: Formula) -> Formula:
        if isinstance(formula, Not):
            op = formula.operand
            if isinstance(op, Not):
                # ~~P => P
                return self.push_negation(op.operand)
            elif isinstance(op, And):
                # ~(P & Q) => ~P | ~Q
                return Or(self.push_negation(Not(op.left)), self.push_negation(Not(op.right)))
            elif isinstance(op, Or):
                # ~(P | Q) => ~P & ~Q
                return And(self.push_negation(Not(op.left)), self.push_negation(Not(op.right)))
            elif isinstance(op, Forall):
                # ~forall x: P => exists x: ~P
                return Exists(op.var_name, self.push_negation(Not(op.body)))
            elif isinstance(op, Exists):
                # ~exists x: P => forall x: ~P
                return Forall(op.var_name, self.push_negation(Not(op.body)))
            else:
                return Not(self.push_negation(op))
        elif isinstance(formula, And):
            return And(self.push_negation(formula.left), self.push_negation(formula.right))
        elif isinstance(formula, Or):
            return Or(self.push_negation(formula.left), self.push_negation(formula.right))
        elif isinstance(formula, Forall):
            return Forall(formula.var_name, self.push_negation(formula.body))
        elif isinstance(formula, Exists):
            return Exists(formula.var_name, self.push_negation(formula.body))
        else:
            return copy.deepcopy(formula)

    # --- Step 4: Standardize Bound Variables ---
    def standardize_variables(self, formula: Formula, env: Optional[Dict[str, str]] = None) -> Formula:
        if env is None:
            env = {}

        if isinstance(formula, Predicate):
            new_args = []
            for a in formula.args:
                if isinstance(a, Variable) and a.name in env:
                    new_args.append(Variable(env[a.name]))
                elif isinstance(a, FunctionTerm):
                    new_args.append(self._subst_term_vars(a, env))
                else:
                    new_args.append(copy.deepcopy(a))
            return Predicate(formula.name, new_args)

        elif isinstance(formula, Not):
            return Not(self.standardize_variables(formula.operand, env))
        elif isinstance(formula, And):
            return And(self.standardize_variables(formula.left, env), self.standardize_variables(formula.right, env))
        elif isinstance(formula, Or):
            return Or(self.standardize_variables(formula.left, env), self.standardize_variables(formula.right, env))
        elif isinstance(formula, Forall):
            self.var_counter += 1
            new_var = f"{formula.var_name}_{self.var_counter}"
            new_env = dict(env)
            new_env[formula.var_name] = new_var
            return Forall(new_var, self.standardize_variables(formula.body, new_env))
        elif isinstance(formula, Exists):
            self.var_counter += 1
            new_var = f"{formula.var_name}_{self.var_counter}"
            new_env = dict(env)
            new_env[formula.var_name] = new_var
            return Exists(new_var, self.standardize_variables(formula.body, new_env))
        else:
            return copy.deepcopy(formula)

    def _subst_term_vars(self, term: Term, env: Dict[str, str]) -> Term:
        if isinstance(term, Variable):
            return Variable(env.get(term.name, term.name))
        elif isinstance(term, FunctionTerm):
            return FunctionTerm(term.name, [self._subst_term_vars(a, env) for a in term.args])
        return copy.deepcopy(term)

    # --- Step 5: Skolemization ---
    def skolemize(self, formula: Formula, universal_vars: List[str]) -> Formula:
        if isinstance(formula, Forall):
            return Forall(formula.var_name, self.skolemize(formula.body, universal_vars + [formula.var_name]))
        elif isinstance(formula, Exists):
            var_to_replace = formula.var_name
            if not universal_vars:
                # Independent existential: replace with Skolem Constant
                self.skolem_const_counter += 1
                skolem_term = Constant(f"skolem_c{self.skolem_const_counter}")
            else:
                # Dependent existential: replace with Skolem Function of universal vars in scope
                self.skolem_func_counter += 1
                sk_args = [Variable(u) for u in universal_vars]
                skolem_term = FunctionTerm(f"skolem_f{self.skolem_func_counter}", sk_args)

            # Substitute var_to_replace with skolem_term inside body
            subbed_body = formula.body.substitute_terms({var_to_replace: skolem_term})
            return self.skolemize(subbed_body, universal_vars)
        elif isinstance(formula, And):
            return And(self.skolemize(formula.left, universal_vars), self.skolemize(formula.right, universal_vars))
        elif isinstance(formula, Or):
            return Or(self.skolemize(formula.left, universal_vars), self.skolemize(formula.right, universal_vars))
        elif isinstance(formula, Not):
            return Not(self.skolemize(formula.operand, universal_vars))
        else:
            return copy.deepcopy(formula)

    # --- Step 6: Drop Universal Quantifiers ---
    def drop_universal(self, formula: Formula) -> Formula:
        if isinstance(formula, Forall):
            return self.drop_universal(formula.body)
        elif isinstance(formula, And):
            return And(self.drop_universal(formula.left), self.drop_universal(formula.right))
        elif isinstance(formula, Or):
            return Or(self.drop_universal(formula.left), self.drop_universal(formula.right))
        elif isinstance(formula, Not):
            return Not(self.drop_universal(formula.operand))
        else:
            return copy.deepcopy(formula)

    # --- Step 7: Distribute OR over AND (CNF) ---
    def distribute_or_over_and(self, formula: Formula) -> Formula:
        if isinstance(formula, And):
            return And(self.distribute_or_over_and(formula.left), self.distribute_or_over_and(formula.right))
        elif isinstance(formula, Or):
            left = self.distribute_or_over_and(formula.left)
            right = self.distribute_or_over_and(formula.right)

            # (A & B) | C => (A | C) & (B | C)
            if isinstance(left, And):
                return And(
                    self.distribute_or_over_and(Or(left.left, right)),
                    self.distribute_or_over_and(Or(left.right, right))
                )
            # A | (B & C) => (A | B) & (A | C)
            if isinstance(right, And):
                return And(
                    self.distribute_or_over_and(Or(left, right.left)),
                    self.distribute_or_over_and(Or(left, right.right))
                )
            return Or(left, right)
        elif isinstance(formula, Not):
            return Not(self.distribute_or_over_and(formula.operand))
        else:
            return copy.deepcopy(formula)

    # --- Step 8: Extract Clauses ---
    def extract_clauses(self, formula: Formula, source_text: str = "") -> List[Clause]:
        raw_clauses = self._collect_conjunctions(formula)
        result: List[Clause] = []
        for i, c_form in enumerate(raw_clauses, start=1):
            literals = self._collect_disjunctions(c_form)
            result.append(Clause(literals=literals, source_clause=source_text))
        return result

    def _collect_conjunctions(self, formula: Formula) -> List[Formula]:
        if isinstance(formula, And):
            return self._collect_conjunctions(formula.left) + self._collect_conjunctions(formula.right)
        return [formula]

    def _collect_disjunctions(self, formula: Formula) -> List[Literal]:
        if isinstance(formula, Or):
            return self._collect_disjunctions(formula.left) + self._collect_disjunctions(formula.right)
        elif isinstance(formula, Not):
            if isinstance(formula.operand, Predicate):
                return [Literal(predicate=formula.operand, is_negated=True)]
            else:
                raise ValueError(f"Expected atomic predicate under Not, got: {formula.operand}")
        elif isinstance(formula, Predicate):
            return [Literal(predicate=formula, is_negated=False)]
        else:
            raise ValueError(f"Unexpected formula type in clause extraction: {type(formula)}")

    # --- Step 9: Standardize Variables Apart Across Clauses ---
    def standardize_clauses_apart(self, clauses: List[Clause], prefix: str = "C") -> List[Clause]:
        final_list: List[Clause] = []
        for i, cl in enumerate(clauses, start=1):
            clause_id = f"{prefix}{i}"
            vars_found = cl.get_variables()
            theta: Dict[str, Term] = {v: Variable(f"{v}_{clause_id}") for v in vars_found}
            std_clause = cl.substitute(theta)
            std_clause.clause_id = clause_id
            std_clause.source_clause = cl.source_clause
            final_list.append(std_clause)
        return final_list

