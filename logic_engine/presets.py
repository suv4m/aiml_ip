"""
logic_engine/presets.py
Curated high-stakes legal dispute cases with plain-English clauses,
formal First-Order Logic translations, interactive scenario facts,
and verified resolution refutation proofs.
"""

from typing import List, Dict, Any


CONTRACT_PRESETS: List[Dict[str, Any]] = [
    {
        "id": "ai-charter-clash",
        "title": "Case 1: The AI Lab Charter Clash",
        "category": "Frontier AI & Open Source Governance",
        "badge": "Public Charter vs Exclusive Commercial License",
        "stakes": "$10B Commercial Exclusivity Dispute",
        "description": "A frontier AI lab pledges in its Founding Charter to keep all model weights permanently open-source. Two years later, leadership signs an exclusive commercial licensing deal with an enterprise cloud conglomerate. Does the contract contain a fatal legal loophole?",
        "clauses": [
            {
                "id": "C1",
                "clause_num": "Charter Art. 1",
                "title": "Mandatory Public Open-Source Pledge",
                "natural_text": "All artificial general intelligence weights, architectures, and models developed by Organization must remain open-source for public benefit.",
                "fopl": "forall m: (CreatedBy(Organization, m) & FrontierModel(m) -> OpenSourcePublic(m))",
                "modality": "Founding Mandate"
            },
            {
                "id": "C2",
                "clause_num": "License Sec. 3.1",
                "title": "Enterprise Commercial Exclusivity",
                "natural_text": "Enterprise Partner holds exclusive proprietary commercial rights over all frontier models created by Organization, and no public open-source release is permitted.",
                "fopl": "forall m: (CreatedBy(Organization, m) & FrontierModel(m) -> ~OpenSourcePublic(m))",
                "modality": "Commercial Restriction"
            },
            {
                "id": "C3",
                "clause_num": "Charter Art. 4",
                "title": "Precedence & Anti-Circumvention Rule",
                "natural_text": "Any commercial agreement that impairs the public open-source mandate is deemed an ultra vires Charter Violation.",
                "fopl": "forall m: (CreatedBy(Organization, m) & ~OpenSourcePublic(m) -> CharterViolation(Organization, m))",
                "modality": "Enforcement"
            }
        ],
        "domain_axioms": [],
        "conflict_demo": {
            "title": "Fatal Loophole Audit: Public Pledge vs Private Exclusivity",
            "description": "Proves that Charter Art. 1 and License Sec. 3.1 are mathematically irreconcilable when evaluating frontier model GPT_Omni.",
            "facts": [
                "CreatedBy(Organization, GPT_Omni)",
                "FrontierModel(GPT_Omni)"
            ],
            "target_query": None,
            "query_description": "Proves contradiction: Charter forces OpenSourcePublic while Commercial License forces ~OpenSourcePublic."
        },
        "breach_demo": {
            "title": "Charter Breach Trial: Commercial Lockup of Model",
            "description": "Proves whether Organization committed an actionable Charter Violation by locking down GPT_Omni under commercial license terms.",
            "facts": [
                "CreatedBy(Organization, GPT_Omni)",
                "FrontierModel(GPT_Omni)",
                "~OpenSourcePublic(GPT_Omni)"
            ],
            "target_query": "CharterViolation(Organization, GPT_Omni)",
            "query_description": "Prove CharterViolation(Organization, GPT_Omni)."
        }
    },
    {
        "id": "multiverse-ip-war",
        "title": "Case 2: The Multiverse IP Rights War",
        "category": "Hollywood Studio Copyright & Franchise Rights",
        "badge": "Standalone Character Rights vs Multiverse Crossover Rights",
        "stakes": "$2.5B Blockbuster Box Office Dispute",
        "description": "Studio A holds perpetual film rights to Spider-Hero. Studio B signs an agreement for exclusive cinematic Multiverse crossover distribution. When the crossover blockbuster 'SecretWars' releases, both studios claim exclusive distribution rights.",
        "clauses": [
            {
                "id": "C1",
                "clause_num": "Agreement A Sec. 2",
                "title": "Standalone Character Franchise Exclusivity",
                "natural_text": "Studio A is the sole exclusive distributor of any theatrical film featuring the character Spider-Hero.",
                "fopl": "forall f: (FeaturesCharacter(f, SpiderHero) -> ExclusiveDistributor(StudioA, f))",
                "modality": "Exclusive Grant"
            },
            {
                "id": "C2",
                "clause_num": "Agreement B Sec. 4",
                "title": "Multiverse Crossover Universe Exclusivity",
                "natural_text": "Studio B is the sole exclusive distributor of any theatrical film depicting Multiverse crossover events.",
                "fopl": "forall f: (MultiverseCrossover(f) -> ExclusiveDistributor(StudioB, f))",
                "modality": "Exclusive Grant"
            },
            {
                "id": "C3",
                "clause_num": "Legal Axiom 1.1",
                "title": "Exclusivity Singularity Axiom",
                "natural_text": "A film cannot have two distinct competing exclusive distributors; granting exclusivity to Studio A prohibits exclusivity to Studio B.",
                "fopl": "forall f: (ExclusiveDistributor(StudioA, f) -> ~ExclusiveDistributor(StudioB, f))",
                "modality": "Legal Axiom"
            }
        ],
        "domain_axioms": [],
        "conflict_demo": {
            "title": "IP Deadlock: Simultaneous Exclusive Distribution Claims",
            "description": "Audits the copyright deadlock when blockbuster SecretWars features both Spider-Hero and Multiverse crossover events.",
            "facts": [
                "FeaturesCharacter(SecretWars, SpiderHero)",
                "MultiverseCrossover(SecretWars)"
            ],
            "target_query": None,
            "query_description": "Proves direct collision: Agreement A entails ExclusiveDistributor(StudioA) which entails ~ExclusiveDistributor(StudioB), contradicting Agreement B."
        },
        "breach_demo": {
            "title": "Injunction Proof: Studio B Breach of Exclusive Covenant",
            "description": "Studio A sues to enjoin Studio B from distributing SecretWars.",
            "facts": [
                "FeaturesCharacter(SecretWars, SpiderHero)",
                "MultiverseCrossover(SecretWars)"
            ],
            "target_query": "ExclusiveDistributor(StudioA, SecretWars)",
            "query_description": "Prove Studio A retains exclusive distribution rights."
        }
    },
    {
        "id": "silicon-whistleblower",
        "title": "Case 3: The Silicon Valley Whistleblower",
        "category": "Corporate Trade Secrets vs Federal Whistleblower Protection",
        "badge": "Strict Corporate NDA vs Federal Disclosure Shield",
        "stakes": "$15M Trade Secret Damages Claim",
        "description": "Engineer Alice discovers secret illegal user surveillance algorithms and delivers encrypted logs to federal law enforcement (FBI). The tech company sues Alice for $15M for violating her strict non-disclosure agreement.",
        "clauses": [
            {
                "id": "C1",
                "clause_num": "NDA Sec. 2.1",
                "title": "Absolute Trade Secret Non-Disclosure",
                "natural_text": "Employee shall not disclose any technical data to any outside party; unauthorized disclosure constitutes a Liability Breach.",
                "fopl": "forall e, d, p: (Employee(e) & TechnicalData(d) & DisclosedTo(e, p, d) & ~Authorized(e, d) -> LiabilityBreach(e, d))",
                "modality": "Prohibition"
            },
            {
                "id": "C2",
                "clause_num": "Whistleblower Sec. 5",
                "title": "Statutory Law Enforcement Protection",
                "natural_text": "Any disclosure of data to a recognized federal agency reporting illegal conduct is legally authorized by law.",
                "fopl": "forall e, d, p: (DisclosedTo(e, p, d) & FederalAgency(p) & IllegalConduct(d) -> Authorized(e, d))",
                "modality": "Statutory Permission"
            },
            {
                "id": "C3",
                "clause_num": "Legal Shield Sec. 9",
                "title": "Statutory Authorization Shield",
                "natural_text": "Any disclosure that is legally authorized under federal statute strictly cannot constitute a Liability Breach.",
                "fopl": "forall e, d: (Authorized(e, d) -> ~LiabilityBreach(e, d))",
                "modality": "Legal Immunity"
            },
            {
                "id": "C4",
                "clause_num": "Remedy Sec. 8.2",
                "title": "Damage Award Trigger",
                "natural_text": "If employee commits a Liability Breach, Company is entitled to liquidated damages.",
                "fopl": "forall e, d: (LiabilityBreach(e, d) -> AwardDamages(Company, e))",
                "modality": "Remedy"
            }
        ],
        "domain_axioms": [],
        "conflict_demo": {
            "title": "Statutory Defense Audit: Does the Whistleblower Shield Prevail?",
            "description": "Tests whether Alice's report to the FBI is shielded from the company's breach claim.",
            "facts": [
                "Employee(Alice)",
                "TechnicalData(SurveillanceLog)",
                "DisclosedTo(Alice, FBI, SurveillanceLog)",
                "FederalAgency(FBI)",
                "IllegalConduct(SurveillanceLog)",
                "LiabilityBreach(Alice, SurveillanceLog)"
            ],
            "target_query": None,
            "query_description": "Proves contradiction: Alice's disclosure is Authorized by statute, refuting the claim of unauthorized LiabilityBreach."
        },
        "breach_demo": {
            "title": "Whistleblower Immunity Proof",
            "description": "Verifies that Alice's report to the FBI is legally authorized under statutory protection.",
            "facts": [
                "Employee(Alice)",
                "TechnicalData(SurveillanceLog)",
                "DisclosedTo(Alice, FBI, SurveillanceLog)",
                "FederalAgency(FBI)",
                "IllegalConduct(SurveillanceLog)"
            ],
            "target_query": "Authorized(Alice, SurveillanceLog)",
            "query_description": "Prove Authorized(Alice, SurveillanceLog)."
        }
    },
    {
        "id": "autonomous-drone-meltdown",
        "title": "Case 4: The Autonomous Drone Crash & Cargo Meltdown",
        "category": "Autonomous Robotics & Cloud Delivery SLA",
        "badge": "99.9% Uptime Guarantee vs Force Majeure Storm Shield",
        "stakes": "$200K Pharmaceutical Cargo Destruction",
        "description": "An autonomous delivery drone crashes during a microburst storm, destroying urgent pharmaceutical inventory. Retailer QuickMeds demands compensation under the 99.9% Delivery Guarantee. DroneCarrier claims zero liability under the Force Majeure weather clause, but an active weather warning was ignored.",
        "clauses": [
            {
                "id": "C1",
                "clause_num": "SLA Sec. 3.2",
                "title": "Guaranteed Delivery & Damage Liability",
                "natural_text": "If carrier fails to deliver cargo and is not exempt from liability, Carrier is legally liable for full replacement damages.",
                "fopl": "forall c, d: (Carrier(c) & Cargo(d) & FailedDelivery(c, d) & ~ExemptFromLiability(c, d) -> LiableForDamages(c, d))",
                "modality": "Guarantee"
            },
            {
                "id": "C2",
                "clause_num": "Force Majeure Sec. 7",
                "title": "Severe Weather Exemption",
                "natural_text": "Carrier is exempt from liability if delivery failure was caused by severe weather events.",
                "fopl": "forall c, d: (Carrier(c) & Cargo(d) & SevereWeatherEvent(d) -> ExemptFromLiability(c, d))",
                "modality": "Exemption"
            },
            {
                "id": "C3",
                "clause_num": "Safety Policy Sec. 2.1",
                "title": "Reckless Dispatch Override",
                "natural_text": "Carrier is strictly not exempt from liability if drone was dispatched despite an active severe gale warning.",
                "fopl": "forall c, d: (Carrier(c) & Cargo(d) & ActiveGaleWarning(d) & DispatchedAnyway(c, d) -> ~ExemptFromLiability(c, d))",
                "modality": "Override"
            }
        ],
        "domain_axioms": [],
        "conflict_demo": {
            "title": "Weather Shield vs Reckless Dispatch Paradox",
            "description": "Audits the clash between the Force Majeure storm shield and the safety dispatch override.",
            "facts": [
                "Carrier(AeroLogistics)",
                "Cargo(PharmaBatch)",
                "FailedDelivery(AeroLogistics, PharmaBatch)",
                "SevereWeatherEvent(PharmaBatch)",
                "ActiveGaleWarning(PharmaBatch)",
                "DispatchedAnyway(AeroLogistics, PharmaBatch)"
            ],
            "target_query": None,
            "query_description": "Proves contradiction: Force Majeure grants ExemptFromLiability while Dispatch Override forces ~ExemptFromLiability."
        },
        "breach_demo": {
            "title": "Liability Proof: Reckless Dispatch Breach",
            "description": "Formally proves AeroLogistics is liable for cargo damages due to ignoring the active gale warning.",
            "facts": [
                "Carrier(AeroLogistics)",
                "Cargo(PharmaBatch)",
                "FailedDelivery(AeroLogistics, PharmaBatch)",
                "ActiveGaleWarning(PharmaBatch)",
                "DispatchedAnyway(AeroLogistics, PharmaBatch)"
            ],
            "target_query": "LiableForDamages(AeroLogistics, PharmaBatch)",
            "query_description": "Prove LiableForDamages(AeroLogistics, PharmaBatch)."
        }
    }
]
