"""
logic_engine/unifier.py
Robinson's First-Order Unification Algorithm with Occurs-Check.
Calculates the Most General Unifier (MGU) for terms, predicates, and complementary literals.
"""

from typing import Dict, Optional, Set, List
import copy

from logic_engine.ast import (
    Term, Variable, Constant, FunctionTerm,
    Predicate, Literal
)


class UnificationError(Exception):
    pass


def occurs_check(var_name: str, term: Term, theta: Dict[str, Term]) -> bool:
    """
    Returns True if variable `var_name` occurs in `term` (directly or via theta bindings).
    Prevents infinite cycles like x = f(x).
    """
    if isinstance(term, Variable):
        if term.name == var_name:
            return True
        if term.name in theta:
            return occurs_check(var_name, theta[term.name], theta)
        return False
    elif isinstance(term, FunctionTerm):
        for arg in term.args:
            if occurs_check(var_name, arg, theta):
                return True
        return False
    return False


def compose_substitutions(theta1: Dict[str, Term], theta2: Dict[str, Term]) -> Dict[str, Term]:
    """
    Composes two substitutions theta1 and theta2: (theta1 o theta2).
    Applies theta2 to every term in theta1, and includes bindings from theta2 not in theta1.
    """
    result: Dict[str, Term] = {}
    for var, term in theta1.items():
        result[var] = term.substitute(theta2)
    for var, term in theta2.items():
        if var not in result:
            result[var] = copy.deepcopy(term)
    return result


def unify_terms(t1: Term, t2: Term, theta: Optional[Dict[str, Term]] = None) -> Optional[Dict[str, Term]]:
    """
    Finds the Most General Unifier (MGU) for two terms t1 and t2 under existing substitution theta.
    Returns the updated substitution dict or None if unification fails.
    """
    if theta is None:
        theta = {}

    # If already identical
    if t1 == t2:
        return theta

    # If t1 is variable
    if isinstance(t1, Variable):
        return unify_var(t1.name, t2, theta)

    # If t2 is variable
    if isinstance(t2, Variable):
        return unify_var(t2.name, t1, theta)

    # If both are Functions
    if isinstance(t1, FunctionTerm) and isinstance(t2, FunctionTerm):
        if t1.name != t2.name or len(t1.args) != len(t2.args):
            return None
        current_theta = dict(theta)
        for a1, a2 in zip(t1.args, t2.args):
            res = unify_terms(a1.substitute(current_theta), a2.substitute(current_theta), current_theta)
            if res is None:
                return None
            current_theta = res
        return current_theta

    # If both are Constants
    if isinstance(t1, Constant) and isinstance(t2, Constant):
        if t1.name == t2.name:
            return theta
        return None

    # Mismatched types
    return None


def unify_var(var_name: str, term: Term, theta: Dict[str, Term]) -> Optional[Dict[str, Term]]:
    """Unifies a variable name with a term under substitution theta."""
    if var_name in theta:
        return unify_terms(theta[var_name], term, theta)

    if isinstance(term, Variable) and term.name in theta:
        return unify_terms(Variable(var_name), theta[term.name], theta)

    # Occurs check: variable cannot occur inside term
    if occurs_check(var_name, term, theta):
        return None

    # Create new binding {var_name: term}
    new_binding = {var_name: term}
    return compose_substitutions(theta, new_binding)


def unify_predicates(p1: Predicate, p2: Predicate, theta: Optional[Dict[str, Term]] = None) -> Optional[Dict[str, Term]]:
    """Unifies two atomic predicates p1 and p2."""
    if theta is None:
        theta = {}

    if p1.name != p2.name or len(p1.args) != len(p2.args):
        return None

    current_theta = dict(theta)
    for a1, a2 in zip(p1.args, p2.args):
        res = unify_terms(a1.substitute(current_theta), a2.substitute(current_theta), current_theta)
        if res is None:
            return None
        current_theta = res
    return current_theta


def unify_complementary_literals(l1: Literal, l2: Literal) -> Optional[Dict[str, Term]]:
    """
    Checks if l1 and l2 are complementary literals (one positive, one negative)
    and if their predicates can be unified.
    Returns MGU theta or None if they cannot resolve.
    """
    if l1.is_negated == l2.is_negated:
        return None  # Same sign cannot resolve against each other

    return unify_predicates(l1.predicate, l2.predicate)


def format_substitution(theta: Optional[Dict[str, Term]]) -> str:
    """Formats a substitution dict into standard mathematical notation: {x/ApexDev, y/Data}."""
    if theta is None:
        return "FAILED"
    if not theta:
        return "{}"
    items = [f"{var} / {term}" for var, term in sorted(theta.items())]
    return "{" + ", ".join(items) + "}"

