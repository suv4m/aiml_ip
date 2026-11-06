"""
logic_engine/ast.py
Abstract Syntax Tree (AST) representations for First-Order Predicate Logic (FOPL)
and Clausal Form (CNF).
"""

from typing import List, Set, Dict, Any, Optional
import copy


class Term:
    """Base class for terms in First-Order Logic (Constants, Variables, Functions)."""
    def is_variable(self) -> bool:
        return False
    
    def is_constant(self) -> bool:
        return False

    def is_function(self) -> bool:
        return False

    def get_variables(self) -> Set[str]:
        return set()

    def substitute(self, theta: Dict[str, 'Term']) -> 'Term':
        raise NotImplementedError


class Variable(Term):
    """Represents a logical variable (e.g., x, y, recipient)."""
    def __init__(self, name: str):
        self.name = name

    def is_variable(self) -> bool:
        return True

    def get_variables(self) -> Set[str]:
        return {self.name}

    def substitute(self, theta: Dict[str, Term]) -> Term:
        if self.name in theta:
            # Recursively apply substitution if needed
            return copy.deepcopy(theta[self.name])
        return Variable(self.name)

    def __repr__(self) -> str:
        return self.name

    def __eq__(self, other) -> bool:
        return isinstance(other, Variable) and self.name == other.name

    def __hash__(self) -> int:
        return hash(("var", self.name))


class Constant(Term):
    """Represents a domain constant (e.g., AcmeCorp, Alice, Data101)."""
    def __init__(self, name: str):
        self.name = name

    def is_constant(self) -> bool:
        return True

    def get_variables(self) -> Set[str]:
        return set()

    def substitute(self, theta: Dict[str, Term]) -> Term:
        return Constant(self.name)

    def __repr__(self) -> str:
        return self.name

    def __eq__(self, other) -> bool:
        return isinstance(other, Constant) and self.name == other.name

    def __hash__(self) -> int:
        return hash(("const", self.name))


class FunctionTerm(Term):
    """Represents a function or Skolem function term (e.g., skolem_f1(x), f(a, y))."""
    def __init__(self, name: str, args: List[Term]):
        self.name = name
        self.args = args

    def is_function(self) -> bool:
        return True

    def get_variables(self) -> Set[str]:
        res = set()
        for a in self.args:
            res.update(a.get_variables())
        return res

    def substitute(self, theta: Dict[str, Term]) -> Term:
        return FunctionTerm(self.name, [a.substitute(theta) for a in self.args])

    def __repr__(self) -> str:
        if not self.args:
            return f"{self.name}()"
        return f"{self.name}({', '.join(str(a) for a in self.args)})"

    def __eq__(self, other) -> bool:
        return (isinstance(other, FunctionTerm) and 
                self.name == other.name and 
                self.args == other.args)

    def __hash__(self) -> int:
        return hash(("func", self.name, tuple(self.args)))


# --- Formulas (WFF) ---

class Formula:
    """Base class for First-Order Logic Formulas (WFF)."""
    def to_pretty(self) -> str:
        return str(self)

    def get_free_variables(self) -> Set[str]:
        raise NotImplementedError

    def get_all_variables(self) -> Set[str]:
        raise NotImplementedError

    def substitute_terms(self, theta: Dict[str, Term]) -> 'Formula':
        raise NotImplementedError

    def to_dict(self) -> Dict[str, Any]:
        raise NotImplementedError


class Predicate(Formula):
    """Atomic formula P(t1, t2, ..., tn)."""
    def __init__(self, name: str, args: Optional[List[Term]] = None):
        self.name = name
        self.args = args or []

    def get_free_variables(self) -> Set[str]:
        res = set()
        for a in self.args:
            res.update(a.get_variables())
        return res

    def get_all_variables(self) -> Set[str]:
        return self.get_free_variables()

    def substitute_terms(self, theta: Dict[str, Term]) -> 'Predicate':
        return Predicate(self.name, [a.substitute(theta) for a in self.args])

    def __repr__(self) -> str:
        if not self.args:
            return self.name
        return f"{self.name}({', '.join(str(a) for a in self.args)})"

    def __eq__(self, other) -> bool:
        return (isinstance(other, Predicate) and 
                self.name == other.name and 
                self.args == other.args)

    def __hash__(self) -> int:
        return hash(("pred", self.name, tuple(self.args)))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Predicate",
            "name": self.name,
            "args": [str(a) for a in self.args]
        }


class Not(Formula):
    """Negation: ~A or ¬A."""
    def __init__(self, operand: Formula):
        self.operand = operand

    def get_free_variables(self) -> Set[str]:
        return self.operand.get_free_variables()

    def get_all_variables(self) -> Set[str]:
        return self.operand.get_all_variables()

    def substitute_terms(self, theta: Dict[str, Term]) -> 'Not':
        return Not(self.operand.substitute_terms(theta))

    def __repr__(self) -> str:
        if isinstance(self.operand, (Predicate, Not)):
            return f"~{self.operand}"
        return f"~({self.operand})"

    def __eq__(self, other) -> bool:
        return isinstance(other, Not) and self.operand == other.operand

    def __hash__(self) -> int:
        return hash(("not", self.operand))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Not",
            "operand": self.operand.to_dict()
        }


class And(Formula):
    """Conjunction: A & B or A ∧ B."""
    def __init__(self, left: Formula, right: Formula):
        self.left = left
        self.right = right

    def get_free_variables(self) -> Set[str]:
        return self.left.get_free_variables().union(self.right.get_free_variables())

    def get_all_variables(self) -> Set[str]:
        return self.left.get_all_variables().union(self.right.get_all_variables())

    def substitute_terms(self, theta: Dict[str, Term]) -> 'And':
        return And(self.left.substitute_terms(theta), self.right.substitute_terms(theta))

    def __repr__(self) -> str:
        return f"({self.left} & {self.right})"

    def __eq__(self, other) -> bool:
        return isinstance(other, And) and self.left == other.left and self.right == other.right

    def __hash__(self) -> int:
        return hash(("and", self.left, self.right))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "And",
            "left": self.left.to_dict(),
            "right": self.right.to_dict()
        }


class Or(Formula):
    """Disjunction: A | B or A ∨ B."""
    def __init__(self, left: Formula, right: Formula):
        self.left = left
        self.right = right

    def get_free_variables(self) -> Set[str]:
        return self.left.get_free_variables().union(self.right.get_free_variables())

    def get_all_variables(self) -> Set[str]:
        return self.left.get_all_variables().union(self.right.get_all_variables())

    def substitute_terms(self, theta: Dict[str, Term]) -> 'Or':
        return Or(self.left.substitute_terms(theta), self.right.substitute_terms(theta))

    def __repr__(self) -> str:
        return f"({self.left} | {self.right})"

    def __eq__(self, other) -> bool:
        return isinstance(other, Or) and self.left == other.left and self.right == other.right

    def __hash__(self) -> int:
        return hash(("or", self.left, self.right))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Or",
            "left": self.left.to_dict(),
            "right": self.right.to_dict()
        }


class Implies(Formula):
    """Implication: A -> B or A ⇒ B."""
    def __init__(self, left: Formula, right: Formula):
        self.left = left
        self.right = right

    def get_free_variables(self) -> Set[str]:
        return self.left.get_free_variables().union(self.right.get_free_variables())

    def get_all_variables(self) -> Set[str]:
        return self.left.get_all_variables().union(self.right.get_all_variables())

    def substitute_terms(self, theta: Dict[str, Term]) -> 'Implies':
        return Implies(self.left.substitute_terms(theta), self.right.substitute_terms(theta))

    def __repr__(self) -> str:
        return f"({self.left} -> {self.right})"

    def __eq__(self, other) -> bool:
        return isinstance(other, Implies) and self.left == other.left and self.right == other.right

    def __hash__(self) -> int:
        return hash(("implies", self.left, self.right))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Implies",
            "left": self.left.to_dict(),
            "right": self.right.to_dict()
        }


class Iff(Formula):
    """Biconditional: A <-> B or A ⇔ B."""
    def __init__(self, left: Formula, right: Formula):
        self.left = left
        self.right = right

    def get_free_variables(self) -> Set[str]:
        return self.left.get_free_variables().union(self.right.get_free_variables())

    def get_all_variables(self) -> Set[str]:
        return self.left.get_all_variables().union(self.right.get_all_variables())

    def substitute_terms(self, theta: Dict[str, Term]) -> 'Iff':
        return Iff(self.left.substitute_terms(theta), self.right.substitute_terms(theta))

    def __repr__(self) -> str:
        return f"({self.left} <-> {self.right})"

    def __eq__(self, other) -> bool:
        return isinstance(other, Iff) and self.left == other.left and self.right == other.right

    def __hash__(self) -> int:
        return hash(("iff", self.left, self.right))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Iff",
            "left": self.left.to_dict(),
            "right": self.right.to_dict()
        }


class Forall(Formula):
    """Universal Quantifier: forall x: P(x) or ∀x P(x)."""
    def __init__(self, var_name: str, body: Formula):
        self.var_name = var_name
        self.body = body

    def get_free_variables(self) -> Set[str]:
        res = self.body.get_free_variables()
        res.discard(self.var_name)
        return res

    def get_all_variables(self) -> Set[str]:
        res = self.body.get_all_variables()
        res.add(self.var_name)
        return res

    def substitute_terms(self, theta: Dict[str, Term]) -> 'Forall':
        sub_theta = {k: v for k, v in theta.items() if k != self.var_name}
        return Forall(self.var_name, self.body.substitute_terms(sub_theta))

    def __repr__(self) -> str:
        return f"forall {self.var_name}: {self.body}"

    def __eq__(self, other) -> bool:
        return isinstance(other, Forall) and self.var_name == other.var_name and self.body == other.body

    def __hash__(self) -> int:
        return hash(("forall", self.var_name, self.body))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Forall",
            "var": self.var_name,
            "body": self.body.to_dict()
        }


class Exists(Formula):
    """Existential Quantifier: exists x: P(x) or ∃x P(x)."""
    def __init__(self, var_name: str, body: Formula):
        self.var_name = var_name
        self.body = body

    def get_free_variables(self) -> Set[str]:
        res = self.body.get_free_variables()
        res.discard(self.var_name)
        return res

    def get_all_variables(self) -> Set[str]:
        res = self.body.get_all_variables()
        res.add(self.var_name)
        return res

    def substitute_terms(self, theta: Dict[str, Term]) -> 'Exists':
        sub_theta = {k: v for k, v in theta.items() if k != self.var_name}
        return Exists(self.var_name, self.body.substitute_terms(sub_theta))

    def __repr__(self) -> str:
        return f"exists {self.var_name}: {self.body}"

    def __eq__(self, other) -> bool:
        return isinstance(other, Exists) and self.var_name == other.var_name and self.body == other.body

    def __hash__(self) -> int:
        return hash(("exists", self.var_name, self.body))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Exists",
            "var": self.var_name,
            "body": self.body.to_dict()
        }


# --- Clausal Form Representation ---

class Literal:
    """A positive or negative atomic predicate in a clause."""
    def __init__(self, predicate: Predicate, is_negated: bool = False):
        self.predicate = predicate
        self.is_negated = is_negated

    def negate(self) -> 'Literal':
        return Literal(copy.deepcopy(self.predicate), not self.is_negated)

    def substitute(self, theta: Dict[str, Term]) -> 'Literal':
        return Literal(self.predicate.substitute_terms(theta), self.is_negated)

    def get_variables(self) -> Set[str]:
        return self.predicate.get_free_variables()

    def __repr__(self) -> str:
        prefix = "~" if self.is_negated else ""
        return f"{prefix}{self.predicate}"

    def __eq__(self, other) -> bool:
        return (isinstance(other, Literal) and 
                self.is_negated == other.is_negated and 
                self.predicate == other.predicate)

    def __hash__(self) -> int:
        return hash(("lit", self.is_negated, self.predicate))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.predicate.name,
            "args": [str(a) for a in self.predicate.args],
            "is_negated": self.is_negated,
            "text": str(self)
        }


class Clause:
    """A disjunction of literals: L1 | L2 | ... | Lk."""
    def __init__(self, literals: Optional[List[Literal]] = None, clause_id: Optional[str] = None, source_clause: Optional[str] = None):
        # Store as ordered list with deduplication
        self.literals: List[Literal] = []
        if literals:
            for lit in literals:
                if lit not in self.literals:
                    self.literals.append(lit)
        self.clause_id = clause_id or ""
        self.source_clause = source_clause or ""

    def is_empty(self) -> bool:
        return len(self.literals) == 0

    def substitute(self, theta: Dict[str, Term]) -> 'Clause':
        new_lits = [lit.substitute(theta) for lit in self.literals]
        return Clause(new_lits, self.clause_id, self.source_clause)

    def get_variables(self) -> Set[str]:
        res = set()
        for lit in self.literals:
            res.update(lit.get_variables())
        return res

    def standardize_variables(self, suffix: str) -> 'Clause':
        vars_in_clause = self.get_variables()
        theta = {v: Variable(f"{v}_{suffix}") for v in vars_in_clause}
        return self.substitute(theta)

    def __repr__(self) -> str:
        if self.is_empty():
            return "[]"  # Empty clause (Contradiction / False / Box)
        return " | ".join(str(lit) for lit in self.literals)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Clause):
            return False
        return set(self.literals) == set(other.literals)

    def __hash__(self) -> int:
        return hash(frozenset(self.literals))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "clause_id": self.clause_id,
            "source_clause": self.source_clause,
            "text": str(self),
            "is_empty": self.is_empty(),
            "literals": [lit.to_dict() for lit in self.literals]
        }

