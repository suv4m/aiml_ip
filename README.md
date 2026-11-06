# Lex Detective
> **Autonomous Legal Conflict & Loophole Engine**  
> *Deductive Legal Reasoning Agent via First-Order Predicate Logic (FOPL) & Resolution Refutation*

---

## 🏛️ Executive Overview

Modern multi-million-dollar agreements (commercial exclusivity deals, franchise copyright grants, whistleblower agreements, and autonomous service level guarantees) frequently conceal **fatal cross-clause contradictions** and **unintended liability loopholes**. Traditional keyword search and probabilistic LLMs often hallucinate or fail to guarantee formal consistency.

**Lex Detective** solves this with rigorous automated theorem proving:
1. Translates plain-English legal terms into formal **First-Order Predicate Logic (FOPL)**.
2. Normalizes formulas through a **9-step Well-Formed Formula (WFF) to Clausal Normal Form (CNF)** transformation pipeline.
3. Applies **Robinson's First-Order Resolution by Refutation** to prove whether:
   - **Intra-Contract Inconsistency Exists**: Two or more clauses are mutually incompatible under specific factual conditions (proving a contract loophole).
   - **Liability / Breach Occurred**: Observed incident logs deductively entail a breach of contractual covenants (proving legal liability).

---

## 🎬 Iconic Real-World Dispute Cases

Lex Detective includes 4 pre-configured, high-stakes dispute cases:

| Case | Dispute Context | Stakes | Logical Clash & Refutation Proof |
| :--- | :--- | :--- | :--- |
| 🤖 **Case 1: The AI Lab Charter Clash** | A frontier AI lab pledges in its Founding Charter that all model weights will remain public open-source. Two years later, leadership signs an exclusive commercial enterprise agreement locking down all frontier models. | **$10B Commercial Exclusivity** | The Charter forces `OpenSourcePublic(m)` while the License forces `~OpenSourcePublic(m)`. Resolution refutation derives the empty contradiction clause $\Box$ in 5 steps! |
| 🎬 **Case 2: The Multiverse IP Rights War** | Studio A owns perpetual film rights to Spider-Hero. Studio B holds exclusive distribution rights to all Multiverse crossover crossovers. When a crossover blockbuster is released, both claim exclusive distribution. | **$2.5B Blockbuster Box Office** | Competing exclusive claims resolve against the legal singularity axiom, mathematically proving an irreconcilable copyright deadlock. |
| 🕵️‍♂️ **Case 3: The Silicon Valley Whistleblower** | An engineer discovers secret illegal surveillance algorithms and reports encrypted logs to the FBI. The company sues for $15M for violating a strict trade secret NDA. | **$15M Trade Secret Claim** | The statutory whistleblower shield entails `Authorized(Alice, Log)`, neutralizing the company's breach claim via deductive refutation. |
| ⚡ **Case 4: The Autonomous Drone Crash** | An autonomous delivery drone crashes during a microburst storm, destroying urgent pharmaceutical cargo. The carrier claims Force Majeure weather immunity, but the safety dispatch override was triggered. | **$200K Pharmaceutical Cargo** | The safety override negates the weather exemption, mathematically proving the carrier is liable for replacement damages. |

---

## 📐 The Formal Logic Pipeline

```
                              LEGAL KNOWLEDGE BASE (KB)
                                         │
[Plain-English Legal Clauses] ──► [Clause Parser] ──► [FOPL AST (∀, ∃, ¬, ∧, ∨, →, ↔)]
                                                            │
                                                            ▼
                                          [9-Step WFF → CNF Transformation]
                                          1. Eliminate Biconditionals (↔)
                                          2. Eliminate Implications (→)
                                          3. Negation Normal Form (De Morgan)
                                          4. Standardize Bound Variables
                                          5. Skolemization (∃ ⟹ c_k or f_k(u))
                                          6. Drop Universal Quantifiers (∀)
                                          7. Distribute ∨ over ∧
                                          8. Extract Clause Set
                                          9. Standardize Clauses Apart
                                                            │
                                                            ▼
[Incident Evidence Facts] ───────────────────────► [Clause Pool] ◄── [Negated Goal ¬Q]
                                                            │
                                                            ▼
                                          [Robinson's Unification Algorithm]
                                          - Occurs-Check: prevents x = f(x)
                                          - Most General Unifier (MGU θ)
                                                            │
                                                            ▼
                                          [Resolution Refutation Theorem Prover]
                                          - Given Clause (Otter Loop)
                                          - Unit Preference & Factoring
                                          - Minimal Proof Backtracking
                                                            │
                                                            ▼
                                           [Empty Clause □ / Contradiction]
                                                            │
                                                            ▼
                                   [Interactive Courtroom Proof Tree & Report]
```

### 1. Robinson's Unification Algorithm with Occurs-Check
Given two atomic literals $L_1 = P(t_1, \dots, t_n)$ and $L_2 = \neg P(s_1, \dots, s_n)$, the unifier computes the Most General Unifier (MGU) $\theta$:
$$\text{MGU}(L_1, \neg L_2) = \theta \quad \text{such that} \quad L_1\theta = (\neg L_2)\theta$$
- **Occurs-Check**: Prevents recursive circular substitutions (e.g. $x = f(x)$) ensuring sound first-order semantics.

### 2. Resolution Inference Rule
Given two standardized parent clauses:
$$C_1 = L_1 \lor \alpha \quad \text{and} \quad C_2 = M_1 \lor \beta$$
If $\text{unify}(L_1, \text{complement}(M_1)) = \theta$, the resolvent clause is:
$$R = (\alpha \lor \beta)\theta$$
When $R = \emptyset = \Box$ (the empty clause), a formal **contradiction** is derived, completing the proof by refutation!

---

## 🖥️ Minimalist, Fresh User Interface

- **Case Dossier & Live Evidence Board**: View plain-English terms, formal logic translations, and interactive incident facts.
- **Courtroom Trial & Visual Proof Tree**:
  - Interactive responsive **SVG DAG Graph** with pan, zoom, parent-lineage tracing, and illuminated empty clause $\Box$ leaf.
  - Switch between **Loophole & Conflict Hunt** and **Breach Liability Trial** with one click.
- **9-Step Transformation Pipeline**: Interactive accordion revealing every algebraic stage of clausal conversion.
- **Settlement & Audit Report**: Executive risk gauge (0–100%), dispute summary, clause citations, and one-click copy Markdown / PDF print export.
- **Dark / Light Theme**: High-contrast modern typography.

---

## 🚀 Quickstart Guide

### 1. Run the Test Suite
```bash
python -m unittest tests/test_all.py
```
*(Runs 8 unit test suites in ~0.1s)*

### 2. Interactive Command-Line Tool (CLI)
```bash
# Audit Case 1: AI Lab Charter Clash ($10B Dispute)
python cli.py --preset 1

# Audit Case 2: Multiverse IP Rights War ($2.5B Dispute)
python cli.py --preset 2

# List all dispute cases
python cli.py --list

# Inspect 9-step CNF conversion for custom formula
python cli.py --cnf "forall x: (Employee(x) -> exists y: (Manager(y) & ReportsTo(x, y)))"
```

### 3. Launch the Web Application
```bash
python main.py --port 8000
```
Open your browser at: **`http://127.0.0.1:8000`**

---

## 📁 Repository Structure

```
aiml_ip/
├── logic_engine/
│   ├── __init__.py
│   ├── ast.py               # FOPL & Clausal Form AST nodes
│   ├── lexer.py             # Tokenizer for logic symbols & quantifiers
│   ├── parser.py            # Recursive descent parser for WFF
│   ├── cnf_converter.py     # 9-step WFF to CNF transformation engine
│   ├── unifier.py           # Robinson's First-Order Unification with occurs-check
│   ├── resolution.py        # Resolution Refutation Theorem Prover & DAG builder
│   ├── clause_translator.py # Deontic NLP-to-logic semantic translator
│   ├── presets.py           # 4 high-stakes legal dispute cases
│   └── auditor.py           # Conflict & Compliance Auditor
├── static/
│   ├── index.html           # Minimalist web interface
│   ├── styles.css           # Clean CSS design system & typography
│   └── app.js               # Reactive frontend controller & SVG DAG renderer
├── tests/
│   ├── __init__.py
│   └── test_all.py          # Complete unit test suite
├── api.py                   # FastAPI REST service
├── cli.py                   # Command-line demonstration tool
├── main.py                  # Web application launcher
└── README.md                # Full technical reference & case guide
```
