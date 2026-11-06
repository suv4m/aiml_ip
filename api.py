"""
api.py
FastAPI application serving the Logic-Based Contract Compliance Engine.
Provides REST endpoints for contract presets, clause translation,
WFF to CNF conversion, and Robinson Resolution Refutation.
"""

import os
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from logic_engine.presets import CONTRACT_PRESETS
from logic_engine.auditor import ContractAuditor
from logic_engine.parser import parse_fopl
from logic_engine.cnf_converter import CNFConverter
from logic_engine.clause_translator import ClauseTranslator
from logic_engine.resolution import ResolutionProver

app = FastAPI(
    title="Lex Detective",
    description="Autonomous legal contract compliance and conflict detection via First-Order Predicate Logic & Resolution Refutation.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

auditor = ContractAuditor()
cnf_converter = CNFConverter()
clause_translator = ClauseTranslator()


# --- Request/Response Models ---

class ParseClauseRequest(BaseModel):
    natural_text: str


class CNFConvertRequest(BaseModel):
    formula: str
    clause_prefix: Optional[str] = "C"


class ResolveRequest(BaseModel):
    clauses: List[str]
    facts: Optional[List[str]] = []
    query: Optional[str] = None


class AuditCustomRequest(BaseModel):
    contract_data: Dict[str, Any]


# --- API Routes ---

@app.get("/api/presets")
def get_presets():
    """Returns all available contract presets."""
    return CONTRACT_PRESETS


@app.get("/api/preset/{preset_id}")
def get_preset(preset_id: str):
    """Returns a single contract preset by ID."""
    for p in CONTRACT_PRESETS:
        if p["id"] == preset_id:
            return p
    raise HTTPException(status_code=404, detail="Preset not found")


@app.post("/api/audit-preset/{preset_id}")
def audit_preset(preset_id: str):
    """Runs a complete audit on a preset contract."""
    for p in CONTRACT_PRESETS:
        if p["id"] == preset_id:
            return auditor.audit_contract_preset(p)
    raise HTTPException(status_code=404, detail="Preset not found")


@app.post("/api/audit-custom")
def audit_custom(req: AuditCustomRequest):
    """Runs an audit on a custom user-defined contract."""
    try:
        return auditor.audit_contract_preset(req.contract_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/parse-clause")
def parse_clause(req: ParseClauseRequest):
    """Translates a natural language clause to FOPL."""
    return clause_translator.translate(req.natural_text)


@app.post("/api/cnf-convert")
def convert_cnf(req: CNFConvertRequest):
    """Executes the 9-step WFF to CNF conversion pipeline."""
    try:
        ast = parse_fopl(req.formula)
        clauses, steps = cnf_converter.convert_with_steps(ast, clause_prefix=req.clause_prefix or "C")
        return {
            "formula": req.formula,
            "clauses": [c.to_dict() for c in clauses],
            "steps": [s.to_dict() for s in steps]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Conversion error: {str(e)}")


@app.post("/api/resolve")
def resolve_query(req: ResolveRequest):
    """Executes Robinson Resolution Refutation."""
    try:
        return auditor.verify_custom_query(
            clauses_fopl=req.clauses,
            facts_fopl=req.facts or [],
            query_fopl=req.query
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Resolution error: {str(e)}")


# Serve static web frontend if static directory exists
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/")
    def serve_index():
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))

