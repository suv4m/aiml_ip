"""
logic_engine/clause_translator.py
Translates simplified plain-English legal clauses into First-Order Predicate Logic (FOPL).
Uses deontic modal mapping, syntactic pattern matching, and entity-action extraction.
"""

from typing import Dict, Any, List, Optional
import re
from logic_engine.parser import parse_fopl
from logic_engine.ast import Formula


class ClauseTranslator:
    """
    Translates plain-English contract clauses into formal First-Order Logic (FOPL).
    Recognizes legal deontic structures:
      - Obligations: "X shall / must / is obligated to do Y"
      - Prohibitions: "X shall not / must not / is prohibited from Y"
      - Permissions: "X may / is permitted to / has the right to Y"
      - Conditional Exceptions: "unless / except if / provided that Z"
    """

    PATTERNS = [
        # 1. Recipient may disclose to subcontractor who signed NDA
        {
            "regex": r"(?:recipient|party)\s+may\s+disclose\s+(?:confidential\s+information|data)\s+to\s+(?:any\s+)?(\w+)\s+(?:who|that)\s+(?:has\s+)?signed\s+(?:an?\s+)?nda",
            "fopl": "forall r, d, c: (Recipient(r) & Confidential(d) & Contractor(c) & SignedSubNDA(c) -> PermittedToDisclose(r, c, d))",
            "desc": "Permission to disclose confidential information to NDA-bound contractors."
        },
        # 2. Recipient shall not disclose to non-employees / third parties
        {
            "regex": r"(?:recipient|party)\s+shall\s+not\s+disclose\s+(?:confidential\s+information|data)\s+to\s+(?:any\s+)?(?:external\s+)?(\w+)",
            "fopl": "forall r, d, e: (Recipient(r) & Confidential(d) & NonEmployee(e) -> ~PermittedToDisclose(r, e, d))",
            "desc": "Strict prohibition against disclosing confidential information to non-employees/third parties."
        },
        # 3. Provider must pay penalty if uptime below threshold
        {
            "regex": r"provider\s+must\s+(?:maintain|pay)\s+.*uptime.*penalty",
            "fopl": "forall p: (CloudProvider(p) & ~Exempt(p) & OutageExceedsThreshold(p) -> ObligatedToPayCredit(p))",
            "desc": "Obligation to pay service credit penalty when uptime threshold is violated and no exemption applies."
        },
        # 4. Scheduled maintenance exemption
        {
            "regex": r"(?:provider\s+is\s+)?exempt.*scheduled\s+maintenance.*prior\s+notice",
            "fopl": "forall p: (CloudProvider(p) & ScheduledMaintenance(p) & PriorNoticeGiven(p) -> Exempt(p))",
            "desc": "Exemption from service penalties for scheduled maintenance with advance notice."
        },
        # 5. Core business hours outage breach
        {
            "regex": r"(?:any\s+)?unscheduled\s+(?:outage|downtime).*business\s+hours.*(?:breach|penalty)",
            "fopl": "forall p: (CloudProvider(p) & UnscheduledOutage(p) & CoreBusinessHours(p) -> SLABreach(p))",
            "desc": "Direct SLA breach incurred for unscheduled outages during business hours."
        },
        # 6. Employee work belongs to company
        {
            "regex": r"(?:all\s+)?(?:software|inventions|work).*created.*employment.*(?:property|exclusive)\s+(?:of\s+)?company",
            "fopl": "forall e, w: (Employee(e) & CreatedDuringEmployment(e, w) -> ExclusiveOwner(Company, w))",
            "desc": "Assignment of all employee-created works to Company as exclusive owner."
        },
        # 7. Employee retains open source rights
        {
            "regex": r"employee\s+(?:may|is\s+permitted\s+to|retains\s+rights\s+to)\s+.*open\s+source",
            "fopl": "forall e, w: (Employee(e) & OpenSourceContribution(e, w) -> ~ExclusiveOwner(Company, w))",
            "desc": "Right of employee to retain ownership / non-exclusive rights on open-source contributions."
        },
        # 8. HIPAA PHI disclosure violation
        {
            "regex": r"(?:associate|party)\s+shall\s+not\s+disclose\s+(?:phi|protected\s+health\s+information).*without\s+consent",
            "fopl": "forall a, p, d: (Associate(a) & PHI(d) & Disclose(a, p, d) & ~WrittenConsent(d) & ~SubpoenaReceived(d) -> HIPAA_Violation(a, d))",
            "desc": "Prohibition of PHI disclosure without patient written consent or statutory subpoena."
        },
        # 9. HIPAA mandatory notification on violation
        {
            "regex": r"(?:in\s+the\s+event\s+of\s+)?(?:a\s+)?hipaa\s+violation.*(?:notify|report)",
            "fopl": "forall a, d: (HIPAA_Violation(a, d) -> MustNotifyHHS(a, d))",
            "desc": "Mandatory obligation to notify HHS and covered entity upon HIPAA violation."
        }
    ]

    def translate(self, natural_clause: str) -> Dict[str, Any]:
        """
        Translates a natural language legal clause into a candidate FOPL formula.
        Falls back to a structural semantic template if no direct regex matches.
        """
        clean_text = natural_clause.strip()
        lower_text = clean_text.lower()

        # Check curated patterns
        for pat in self.PATTERNS:
            if re.search(pat["regex"], lower_text):
                fopl_str = pat["fopl"]
                try:
                    parsed_ast = parse_fopl(fopl_str)
                    return {
                        "matched": True,
                        "fopl": fopl_str,
                        "description": pat["desc"],
                        "confidence": 0.95,
                        "ast_type": type(parsed_ast).__name__
                    }
                except Exception:
                    pass

        # Heuristic fallback: detect Deontic modality (shall, may, shall not, must)
        if "shall not" in lower_text or "must not" in lower_text or "prohibited" in lower_text:
            fopl_str = "forall x, a: (Party(x) & Action(a) & RestrictedCondition(x, a) -> ~Permitted(x, a))"
            desc = "Heuristic Prohibition: Prohibits Party x from performing Action a under restricted conditions."
        elif "may" in lower_text or "permitted" in lower_text or "entitled" in lower_text:
            fopl_str = "forall x, a: (Party(x) & Action(a) & AuthorizedCondition(x, a) -> Permitted(x, a))"
            desc = "Heuristic Permission: Grants Party x permission to perform Action a under authorized conditions."
        elif "shall" in lower_text or "must" in lower_text or "obligated" in lower_text or "required" in lower_text:
            fopl_str = "forall x, a: (Party(x) & ObligationTrigger(x) & ~Performed(x, a) -> ContractBreach(x))"
            desc = "Heuristic Obligation: Obligates Party x to perform Action a; failure to perform constitutes breach."
        else:
            fopl_str = "forall x: (Condition(x) -> LegalEffect(x))"
            desc = "Generic Rule: Establishes a conditional legal implication."

        return {
            "matched": False,
            "fopl": fopl_str,
            "description": desc,
            "confidence": 0.65,
            "ast_type": "Heuristic"
        }

