"""
logic_engine/auditor.py
High-level Automated Contract Compliance & Conflict Detection Engine.
Coordinates clause parsing, CNF conversion, resolution refutation,
and generates structured executive audit reports.
"""

from typing import Dict, Any, List, Optional
import time

from logic_engine.parser import parse_fopl
from logic_engine.cnf_converter import CNFConverter
from logic_engine.resolution import ResolutionProver, ProofResult
from logic_engine.ast import Clause, Literal, Predicate, Not


class ContractAuditor:
    """Executes end-to-end logical audit of legal contracts."""

    def __init__(self):
        self.cnf_converter = CNFConverter()
        self.prover = ResolutionProver(max_clauses=2000)

    def audit_contract_preset(self, contract_data: Dict[str, Any]) -> Dict[str, Any]:
        """Runs both internal conflict audit and breach scenario verification for a contract preset."""
        start_time = time.time()

        # 1. Convert clauses and axioms to CNF
        kb_clauses: List[Clause] = []
        clause_conversions: List[Dict[str, Any]] = []

        for c in contract_data.get("clauses", []):
            fopl_ast = parse_fopl(c["fopl"])
            cls, steps = self.cnf_converter.convert_with_steps(
                fopl_ast,
                clause_prefix=c["id"],
                source_text=f"{c.get('clause_num', '')} {c.get('title', '')}: {c.get('natural_text', '')}"
            )
            kb_clauses.extend(cls)
            clause_conversions.append({
                "clause_id": c["id"],
                "clause_num": c.get("clause_num", ""),
                "title": c.get("title", ""),
                "natural_text": c.get("natural_text", ""),
                "fopl": c["fopl"],
                "clauses": [cl.to_dict() for cl in cls],
                "steps": [s.to_dict() for s in steps]
            })

        for ax in contract_data.get("domain_axioms", []):
            fopl_ast = parse_fopl(ax["fopl"])
            cls, steps = self.cnf_converter.convert_with_steps(
                fopl_ast,
                clause_prefix=ax["id"],
                source_text=f"Axiom: {ax.get('natural_text', '')}"
            )
            kb_clauses.extend(cls)

        # 2. Audit Internal Conflict Demo
        conflict_demo = contract_data.get("conflict_demo", {})
        conflict_result = None
        if conflict_demo and conflict_demo.get("facts"):
            conflict_clauses = [cl for cl in kb_clauses]
            for i, f_str in enumerate(conflict_demo["facts"], start=1):
                f_ast = parse_fopl(f_str)
                f_cls, _ = self.cnf_converter.convert_with_steps(f_ast, clause_prefix=f"FACT_{i}", source_text=f"Conflict Fact: {f_str}")
                conflict_clauses.extend(f_cls)

            # Target query if any
            if conflict_demo.get("target_query"):
                q_ast = parse_fopl(conflict_demo["target_query"])
                neg_q = Not(q_ast)
                q_cls, _ = self.cnf_converter.convert_with_steps(neg_q, clause_prefix="QUERY", source_text=f"Negated Goal: ~({conflict_demo['target_query']})")
                conflict_clauses.extend(q_cls)

            conflict_proof: ProofResult = self.prover.prove(conflict_clauses)
            conflict_result = {
                "title": conflict_demo.get("title"),
                "description": conflict_demo.get("description"),
                "facts": conflict_demo.get("facts"),
                "proof": conflict_proof.to_dict()
            }

        # 3. Audit Scenario Breach Demo
        breach_demo = contract_data.get("breach_demo", {})
        breach_result = None
        if breach_demo and breach_demo.get("target_query"):
            breach_clauses = [cl for cl in kb_clauses]
            for i, f_str in enumerate(breach_demo.get("facts", []), start=1):
                f_ast = parse_fopl(f_str)
                f_cls, _ = self.cnf_converter.convert_with_steps(f_ast, clause_prefix=f"AUDIT_FACT_{i}", source_text=f"Incident Fact: {f_str}")
                breach_clauses.extend(f_cls)

            # Negate target query to prove it via refutation
            q_ast = parse_fopl(breach_demo["target_query"])
            neg_q = Not(q_ast)
            q_cls, _ = self.cnf_converter.convert_with_steps(neg_q, clause_prefix="NEG_QUERY", source_text=f"Negated Query: ~({breach_demo['target_query']})")
            breach_clauses.extend(q_cls)

            breach_proof: ProofResult = self.prover.prove(breach_clauses)
            breach_result = {
                "title": breach_demo.get("title"),
                "description": breach_demo.get("description"),
                "facts": breach_demo.get("facts"),
                "target_query": breach_demo.get("target_query"),
                "proof": breach_proof.to_dict()
            }

        elapsed = round((time.time() - start_time) * 1000, 2)

        # Risk Score Calculation
        risk_score = 0
        if conflict_result and conflict_result["proof"]["success"]:
            risk_score += 60  # Latent contradiction is high risk
        if breach_result and breach_result["proof"]["success"]:
            risk_score += 40  # Proven liability breach

        return {
            "contract_id": contract_data.get("id"),
            "title": contract_data.get("title"),
            "category": contract_data.get("category"),
            "stakes": contract_data.get("stakes", "$5M Legal Exposure"),
            "elapsed_ms": elapsed,
            "risk_score": risk_score,
            "risk_level": "CRITICAL" if risk_score >= 80 else ("HIGH" if risk_score >= 50 else "LOW"),
            "clauses_count": len(contract_data.get("clauses", [])),
            "kb_clauses_total": len(kb_clauses),
            "clause_conversions": clause_conversions,
            "conflict_audit": conflict_result,
            "breach_audit": breach_result,
            "markdown_report": self._build_markdown_report(contract_data, conflict_result, breach_result, risk_score)
        }

    def verify_custom_query(self, clauses_fopl: List[str], facts_fopl: List[str], query_fopl: Optional[str] = None) -> Dict[str, Any]:
        """Verifies a custom set of clauses, facts, and optional query."""
        all_clauses: List[Clause] = []

        for i, f_str in enumerate(clauses_fopl, start=1):
            ast = parse_fopl(f_str)
            cls, _ = self.cnf_converter.convert_with_steps(ast, clause_prefix=f"C{i}", source_text=f"Clause {i}: {f_str}")
            all_clauses.extend(cls)

        for i, f_str in enumerate(facts_fopl, start=1):
            ast = parse_fopl(f_str)
            cls, _ = self.cnf_converter.convert_with_steps(ast, clause_prefix=f"F{i}", source_text=f"Fact {i}: {f_str}")
            all_clauses.extend(cls)

        if query_fopl and query_fopl.strip():
            ast = parse_fopl(query_fopl)
            neg_ast = Not(ast)
            cls, _ = self.cnf_converter.convert_with_steps(neg_ast, clause_prefix="QUERY", source_text=f"Negated Goal: ~({query_fopl})")
            all_clauses.extend(cls)

        proof = self.prover.prove(all_clauses)
        return proof.to_dict()

    def _build_markdown_report(
        self,
        contract_data: Dict[str, Any],
        conflict_res: Optional[Dict[str, Any]],
        breach_res: Optional[Dict[str, Any]],
        risk_score: int
    ) -> str:
        lines = [
            f"# Lex Detective: Legal Conflict & Settlement Audit Report",
            f"**Case:** {contract_data.get('title')} ({contract_data.get('category')})  ",
            f"**Stakes:** {contract_data.get('stakes', 'High Stakes Dispute')}  ",
            f"**Risk Index:** {risk_score}/100 ({'CRITICAL' if risk_score >= 80 else ('HIGH' if risk_score >= 50 else 'LOW')})  \n",
            "---",
            "## 1. Executive Summary & Verdict",
            f"The Autonomous Reasoning Agent executed a First-Order Logic deduction over the {len(contract_data.get('clauses', []))} clauses and dispute evidence.",
            ""
        ]

        if conflict_res and conflict_res["proof"]["success"]:
            lines.extend([
                "### 🚨 Fatal Contract Contradiction & Loophole Detected",
                f"- **Dispute:** {conflict_res.get('title')}",
                f"- **Verdict:** Mutually exclusive obligations proved in {len(conflict_res['proof']['steps'])} resolution steps.",
                f"- **Empty Clause Derivation:** `{conflict_res['proof']['empty_clause_id']}`",
                "- **Legal Impact:** The contract contains an irreconcilable conflict. Under dispute rules, conflicting terms cannot be simultaneously enforced, creating an actionable loophole.",
                ""
            ])
        else:
            lines.append("### ✅ No Internal Contradictions Found in Base Knowledge Base\n")

        if breach_res and breach_res["proof"]["success"]:
            lines.extend([
                "### ⚖️ Legal Breach Formally Proven Beyond Doubt",
                f"- **Claim:** {breach_res.get('title')}",
                f"- **Proven Target:** `{breach_res.get('target_query')}`",
                f"- **Proof Path Length:** {len(breach_res['proof']['steps'])} steps leading to refutation []",
                "- **Liability Assessment:** The facts of the incident log deductively entail legal liability under first-order predicate semantics.",
                ""
            ])

        lines.extend([
            "---",
            "## 2. Clause Inventory & Formal Representations",
            ""
        ])

        for c in contract_data.get("clauses", []):
            lines.append(f"### {c.get('clause_num', '')}: {c.get('title', '')} [{c.get('modality', '')}]")
            lines.append(f"> \"{c.get('natural_text', '')}\"")
            lines.append(f"```logic\n{c.get('fopl', '')}\n```\n")

        lines.extend([
            "---",
            "## 3. Step-by-Step Mathematical Refutation Proof",
            ""
        ])

        if conflict_res and conflict_res["proof"]["steps"]:
            lines.append("#### Contradiction Derivation Steps:")
            for s in conflict_res["proof"]["steps"]:
                lines.append(f"- **Step {s['step_id']}**: Resolved `{s['literal1']}` from `{s['parent1_id']}` with `{s['literal2']}` from `{s['parent2_id']}` via MGU `{s['mgu']}` $\\to$ **Resolvent:** `{s['resolvent']['text']}`")
            lines.append("")

        if breach_res and breach_res["proof"]["steps"]:
            lines.append("#### Breach Proof Steps:")
            for s in breach_res["proof"]["steps"]:
                lines.append(f"- **Step {s['step_id']}**: Resolved `{s['literal1']}` from `{s['parent1_id']}` with `{s['literal2']}` from `{s['parent2_id']}` via MGU `{s['mgu']}` $\\to$ **Resolvent:** `{s['resolvent']['text']}`")
            lines.append("")

        lines.extend([
            "---",
            "## 4. Strategic Settlement Guidance",
            "1. **Dispute Settlement**: If a cross-clause contradiction is proved, the affected party can move to dismiss enforcement or demand contract renegotiation.",
            "2. **Harmonization**: Add explicit precedence carve-outs (e.g. 'Notwithstanding Section X...').",
            "3. **Proactive Protection**: Deploy automated logic verification prior to executing multi-million dollar agreements."
        ])

        return "\n".join(lines)
