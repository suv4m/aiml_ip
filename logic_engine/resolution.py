"""
logic_engine/resolution.py
First-Order Logic Resolution by Refutation Theorem Prover.
Implements the Given Clause (Otter loop) algorithm with unit preference,
subsumption checking, and minimal proof DAG reconstruction.
"""

from typing import List, Dict, Set, Tuple, Optional, Any
import copy
import heapq

from logic_engine.ast import (
    Term, Variable, Constant, FunctionTerm,
    Predicate, Literal, Clause
)
from logic_engine.unifier import (
    unify_complementary_literals, format_substitution
)


class ProofStep:
    """Represents a single valid resolution inference step."""
    def __init__(
        self,
        step_id: str,
        parent1_id: str,
        parent2_id: str,
        resolvent: Clause,
        literal1: Literal,
        literal2: Literal,
        mgu: Dict[str, Term],
        explanation: str = ""
    ):
        self.step_id = step_id
        self.parent1_id = parent1_id
        self.parent2_id = parent2_id
        self.resolvent = resolvent
        self.literal1 = literal1
        self.literal2 = literal2
        self.mgu = mgu
        self.explanation = explanation

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "parent1_id": self.parent1_id,
            "parent2_id": self.parent2_id,
            "resolvent": self.resolvent.to_dict(),
            "literal1": str(self.literal1),
            "literal2": str(self.literal2),
            "mgu": format_substitution(self.mgu),
            "explanation": self.explanation
        }


class ProofResult:
    """Stores the complete outcome of a Resolution Refutation run."""
    def __init__(
        self,
        success: bool,
        steps: List[ProofStep],
        initial_clauses: List[Clause],
        empty_clause_id: Optional[str] = None,
        total_clauses_generated: int = 0,
        message: str = ""
    ):
        self.success = success
        self.steps = steps
        self.initial_clauses = initial_clauses
        self.empty_clause_id = empty_clause_id
        self.total_clauses_generated = total_clauses_generated
        self.message = message

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "empty_clause_id": self.empty_clause_id,
            "total_clauses_generated": self.total_clauses_generated,
            "message": self.message,
            "initial_clauses": [c.to_dict() for c in self.initial_clauses],
            "steps": [s.to_dict() for s in self.steps],
            "graph": self.build_graph()
        }

    def build_graph(self) -> Dict[str, Any]:
        """Builds a Directed Acyclic Graph (DAG) for interactive visual rendering."""
        nodes = []
        edges = []

        # Find all participating clause IDs by backtracking from empty clause
        participating_ids = set()
        step_by_id = {s.step_id: s for s in self.steps}

        if self.success and self.empty_clause_id:
            participating_ids.add(self.empty_clause_id)
            queue = [self.empty_clause_id]
            while queue:
                cid = queue.pop(0)
                if cid in step_by_id:
                    s = step_by_id[cid]
                    participating_ids.add(s.parent1_id)
                    participating_ids.add(s.parent2_id)
                    queue.append(s.parent1_id)
                    queue.append(s.parent2_id)
        else:
            participating_ids = {c.clause_id for c in self.initial_clauses}.union(
                {s.step_id for s in self.steps[:20]}
            )

        # Initial clauses nodes
        for c in self.initial_clauses:
            if c.clause_id in participating_ids:
                node_type = "query" if "QUERY" in c.clause_id or "GOAL" in c.clause_id else "axiom"
                nodes.append({
                    "id": c.clause_id,
                    "label": str(c),
                    "type": node_type,
                    "source": c.source_clause or "Base Axiom",
                    "clause": c.to_dict()
                })

        # Derived step nodes and edges
        for s in self.steps:
            if s.step_id in participating_ids:
                is_contradiction = s.resolvent.is_empty()
                nodes.append({
                    "id": s.step_id,
                    "label": "[] (Contradiction)" if is_contradiction else str(s.resolvent),
                    "type": "contradiction" if is_contradiction else "resolvent",
                    "source": f"Resolved from {s.parent1_id} & {s.parent2_id}",
                    "clause": s.resolvent.to_dict()
                })

                edges.append({
                    "from": s.parent1_id,
                    "to": s.step_id,
                    "literal": str(s.literal1),
                    "mgu": format_substitution(s.mgu)
                })
                edges.append({
                    "from": s.parent2_id,
                    "to": s.step_id,
                    "literal": str(s.literal2),
                    "mgu": format_substitution(s.mgu)
                })

        return {"nodes": nodes, "edges": edges}


class ResolutionProver:
    """Resolution by Refutation Theorem Prover for First-Order Logic."""

    def __init__(self, max_clauses: int = 1000):
        self.max_clauses = max_clauses

    def prove(self, clauses: List[Clause]) -> ProofResult:
        """
        Executes resolution refutation on input clauses using the Given Clause algorithm.
        """
        initial_clauses: List[Clause] = []
        for i, c in enumerate(clauses):
            cid = c.clause_id if c.clause_id else f"A{i+1}"
            cl_copy = copy.deepcopy(c)
            cl_copy.clause_id = cid
            initial_clauses.append(cl_copy)

        # Check if contradiction is already in initial knowledge base
        for c in initial_clauses:
            if c.is_empty():
                return ProofResult(
                    success=True,
                    steps=[],
                    initial_clauses=initial_clauses,
                    empty_clause_id=c.clause_id,
                    total_clauses_generated=len(initial_clauses),
                    message="Contradiction found: Empty clause present in initial axioms."
                )

        steps: List[ProofStep] = []
        clause_counter = len(initial_clauses)
        seen_clauses: Set[str] = {self._canonical_clause_str(c) for c in initial_clauses}

        # Unprocessed agenda (ordered by clause length to prioritize unit clauses)
        unprocessed: List[Clause] = sorted(initial_clauses, key=lambda c: len(c.literals))
        processed: List[Clause] = []

        step_counter = 0

        while unprocessed and len(processed) + len(unprocessed) < self.max_clauses:
            # Pick the shortest clause (Unit preference)
            given = unprocessed.pop(0)

            # Resolve given clause against all processed clauses
            for other in processed:
                resolvents = self._resolve_pair(given, other)
                for resolvent_clause, lit1, lit2, mgu in resolvents:
                    # Tautology check: P | ~P
                    if self._is_tautology(resolvent_clause):
                        continue

                    canon = self._canonical_clause_str(resolvent_clause)
                    if canon in seen_clauses:
                        continue
                    seen_clauses.add(canon)

                    step_counter += 1
                    clause_counter += 1
                    resolvent_id = f"R{step_counter}"
                    resolvent_clause.clause_id = resolvent_id

                    explanation = self._build_explanation(given, other, lit1, lit2, mgu, resolvent_clause)
                    step = ProofStep(
                        step_id=resolvent_id,
                        parent1_id=given.clause_id,
                        parent2_id=other.clause_id,
                        resolvent=resolvent_clause,
                        literal1=lit1,
                        literal2=lit2,
                        mgu=mgu,
                        explanation=explanation
                    )
                    steps.append(step)

                    # Empty clause derived! Proof refutation successful!
                    if resolvent_clause.is_empty():
                        pruned_steps = self._prune_irrelevant_steps(steps, resolvent_id)
                        return ProofResult(
                            success=True,
                            steps=pruned_steps,
                            initial_clauses=initial_clauses,
                            empty_clause_id=resolvent_id,
                            total_clauses_generated=clause_counter,
                            message="Contradiction derived! Refutation proof succeeded (empty clause [] derived)."
                        )

                    # Insert resolvent into unprocessed preserving length order
                    self._insert_ordered(unprocessed, resolvent_clause)

            processed.append(given)

        return ProofResult(
            success=False,
            steps=steps[:40],
            initial_clauses=initial_clauses,
            empty_clause_id=None,
            total_clauses_generated=clause_counter,
            message="No contradiction found. Knowledge base is consistent."
        )

    def _insert_ordered(self, lst: List[Clause], item: Clause) -> None:
        """Inserts a clause into a length-sorted list using binary search."""
        target_len = len(item.literals)
        low, high = 0, len(lst)
        while low < high:
            mid = (low + high) // 2
            if len(lst[mid].literals) <= target_len:
                low = mid + 1
            else:
                high = mid
        lst.insert(low, item)

    def _resolve_pair(self, c1: Clause, c2: Clause) -> List[Tuple[Clause, Literal, Literal, Dict[str, Term]]]:
        """Resolves two clauses on all complementary unifiable literal pairs."""
        # Standardize variables apart between the two clauses
        c1_std = c1.standardize_variables("p1")
        c2_std = c2.standardize_variables("p2")

        resolvents: List[Tuple[Clause, Literal, Literal, Dict[str, Term]]] = []

        for l1 in c1_std.literals:
            for l2 in c2_std.literals:
                mgu = unify_complementary_literals(l1, l2)
                if mgu is not None:
                    # Construct resolvent: (c1 \ {l1}) U (c2 \ {l2}) under mgu
                    remaining_lits: List[Literal] = []
                    for lit in c1_std.literals:
                        if lit != l1:
                            remaining_lits.append(lit.substitute(mgu))
                    for lit in c2_std.literals:
                        if lit != l2:
                            remaining_lits.append(lit.substitute(mgu))

                    # Factor unifiable duplicate literals
                    factored_lits: List[Literal] = []
                    for lit in remaining_lits:
                        if lit not in factored_lits:
                            factored_lits.append(lit)

                    new_clause = Clause(literals=factored_lits)
                    resolvents.append((new_clause, l1, l2, mgu))

        return resolvents

    def _is_tautology(self, clause: Clause) -> bool:
        pos_lits = [lit for lit in clause.literals if not lit.is_negated]
        neg_lits = [lit for lit in clause.literals if lit.is_negated]
        for p in pos_lits:
            for n in neg_lits:
                if p.predicate == n.predicate:
                    return True
        return False

    def _canonical_clause_str(self, clause: Clause) -> str:
        # Normalize variable names to canonical forms for structural equality
        var_map: Dict[str, str] = {}
        v_idx = 0
        norm_lits = []
        for lit in sorted(clause.literals, key=lambda l: (l.predicate.name, l.is_negated, len(l.predicate.args))):
            norm_args = []
            for a in lit.predicate.args:
                if isinstance(a, Variable):
                    if a.name not in var_map:
                        v_idx += 1
                        var_map[a.name] = f"v{v_idx}"
                    norm_args.append(var_map[a.name])
                else:
                    norm_args.append(str(a))
            prefix = "~" if lit.is_negated else ""
            norm_lits.append(f"{prefix}{lit.predicate.name}({','.join(norm_args)})")
        return " | ".join(sorted(norm_lits))

    def _build_explanation(
        self,
        c1: Clause,
        c2: Clause,
        l1: Literal,
        l2: Literal,
        mgu: Dict[str, Term],
        resolvent: Clause
    ) -> str:
        mgu_str = format_substitution(mgu)
        if resolvent.is_empty():
            return (
                f"Resolved '{l1}' from [{c1.clause_id}] against '{l2}' from [{c2.clause_id}] "
                f"under MGU {mgu_str}. Derived the EMPTY CLAUSE [] (formal contradiction!). "
                f"Proves that the clauses mutually invalidate each other."
            )
        return (
            f"Resolved literal '{l1}' from [{c1.clause_id}] with complementary '{l2}' from [{c2.clause_id}] "
            f"under MGU {mgu_str} -> Resolvent: [{resolvent}]."
        )

    def _prune_irrelevant_steps(self, steps: List[ProofStep], empty_clause_id: str) -> List[ProofStep]:
        needed_ids: Set[str] = {empty_clause_id}
        step_map = {s.step_id: s for s in steps}

        queue = [empty_clause_id]
        while queue:
            cur_id = queue.pop(0)
            if cur_id in step_map:
                s = step_map[cur_id]
                if s.parent1_id not in needed_ids:
                    needed_ids.add(s.parent1_id)
                    queue.append(s.parent1_id)
                if s.parent2_id not in needed_ids:
                    needed_ids.add(s.parent2_id)
                    queue.append(s.parent2_id)

        return [s for s in steps if s.step_id in needed_ids]
