"""
cli.py
Interactive Command-Line Interface for Lex Detective.
Autonomous Legal Conflict & Loophole Engine.
"""

import sys
import argparse
from typing import Optional

from logic_engine.presets import CONTRACT_PRESETS
from logic_engine.auditor import ContractAuditor
from logic_engine.parser import parse_fopl
from logic_engine.cnf_converter import CNFConverter
from logic_engine.resolution import ResolutionProver


def banner():
    print("=" * 80)
    print("  LEX DETECTIVE: Autonomous Legal Conflict & Loophole Engine")
    print("  First-Order Predicate Logic Theorem Proving & Resolution Refutation")
    print("=" * 80)


def list_presets():
    print("\nAvailable Real-World Legal Dispute Cases:")
    for i, p in enumerate(CONTRACT_PRESETS, start=1):
        print(f"  [{i}] {p['title']}")
        print(f"      Category: {p['category']}")
        print(f"      Stakes:   {p.get('stakes', 'High Stakes Dispute')}")
        print(f"      Issue:    {p['badge']}")
        print(f"      Clauses:  {len(p['clauses'])} clauses\n")


def run_audit(preset_index: int = 0):
    if preset_index < 0 or preset_index >= len(CONTRACT_PRESETS):
        print(f"Invalid case index: {preset_index}")
        return

    preset = CONTRACT_PRESETS[preset_index]
    auditor = ContractAuditor()

    print(f"\n[+] Running Autonomous Legal Conflict & Breach Audit for: '{preset['title']}'...")
    print(f"    Stakes: {preset.get('stakes', 'N/A')}")
    res = auditor.audit_contract_preset(preset)

    print(f"\nAudit completed in {res['elapsed_ms']} ms.")
    print(f"Risk Index: {res['risk_score']}/100 [{res['risk_level']}]")
    print(f"Total Base Clauses in Knowledge Base: {res['kb_clauses_total']}")

    # 1. Clauses
    print("\n" + "-" * 80)
    print(" CASE CLAUSES & FIRST-ORDER LOGIC REPRESENTATIONS")
    print("-" * 80)
    for c in res["clause_conversions"]:
        print(f"\n* {c['clause_num']} - {c['title']}")
        print(f"  Plain English: \"{c['natural_text']}\"")
        print(f"  Logic Formula: {c['fopl']}")
        print(f"  Clausal Form:  {[cl['text'] for cl in c['clauses']]}")

    # 2. Conflict Proof
    print("\n" + "-" * 80)
    print(" CONFLICT & LOOPHOLE DETECTION (Cross-Clause Contradiction Prover)")
    print("-" * 80)
    conf = res["conflict_audit"]
    if conf:
        print(f"Scenario:    {conf['title']}")
        print(f"Facts:       {conf['facts']}")
        proof = conf["proof"]
        print(f"Result:      {'FATAL CONTRADICTION FOUND! (Clauses Incompatible)' if proof['success'] else 'Consistent'}")
        print(f"Derivation:  Derived Empty Clause [{proof['empty_clause_id']}] in {len(proof['steps'])} refutation steps.\n")
        print("Proof Trace:")
        for s in proof["steps"]:
            print(f"  [{s['step_id']}] Resolved '{s['literal1']}' ({s['parent1_id']}) with '{s['literal2']}' ({s['parent2_id']})")
            print(f"       MGU:       {s['mgu']}")
            print(f"       Resolvent: {s['resolvent']['text']}")

    # 3. Breach Proof
    print("\n" + "-" * 80)
    print(" INCIDENT COMPLIANCE TRIAL (Breach Verification)")
    print("-" * 80)
    breach = res["breach_audit"]
    if breach:
        print(f"Scenario:    {breach['title']}")
        print(f"Target:      {breach['target_query']}")
        print(f"Incident:    {breach['facts']}")
        proof = breach["proof"]
        print(f"Result:      {'LEGAL BREACH PROVEN BEYOND DOUBT' if proof['success'] else 'No Breach'}")
        print(f"Refutation:  Derived empty clause [{proof['empty_clause_id']}] in {len(proof['steps'])} steps.\n")
        print("Proof Trace:")
        for s in proof["steps"]:
            print(f"  [{s['step_id']}] Resolved '{s['literal1']}' ({s['parent1_id']}) with '{s['literal2']}' ({s['parent2_id']})")
            print(f"       MGU:       {s['mgu']}")
            print(f"       Resolvent: {s['resolvent']['text']}")

    print("\n" + "=" * 80)
    print(" VERDICT REACHED - DEDUCTIVE PROOF COMPLETE")
    print("=" * 80)


def show_cnf_pipeline(formula_str: str):
    print(f"\n[+] Demonstrating 9-Step WFF -> CNF Transformation Pipeline for:\n    {formula_str}\n")
    ast = parse_fopl(formula_str)
    conv = CNFConverter()
    clauses, steps = conv.convert_with_steps(ast, clause_prefix="DEMO")
    for s in steps:
        print(f"Step {s.step_num}: {s.name}")
        print(f"  Description: {s.description}")
        print(f"  Output:      {s.formula_str}\n")


def main():
    banner()
    parser = argparse.ArgumentParser(description="Lex Detective CLI")
    parser.add_argument("--preset", type=int, default=1, help="Case preset index (1-4)")
    parser.add_argument("--list", action="store_true", help="List all dispute cases")
    parser.add_argument("--cnf", type=str, default="", help="Test 9-step CNF conversion on custom logic formula")

    args = parser.parse_args()

    if args.list:
        list_presets()
    elif args.cnf:
        show_cnf_pipeline(args.cnf)
    else:
        run_audit(args.preset - 1)


if __name__ == "__main__":
    main()
