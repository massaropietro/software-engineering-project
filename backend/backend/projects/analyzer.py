import re
import json
import logging
import ast
from pathlib import Path

import z3
import requests
from django.conf import settings

from backend.projects.models import MutationResult

logger = logging.getLogger(__name__)


def parse_and_verify_z3_smt(smt_code: str):
    """
    Esegue il codice SMT-LIB v2.6 in Z3.
    """
    try:
        solver = z3.Solver()
        clean_smt = smt_code.strip()

        logger.info("[Z3] Inizio parsing dello script SMT...")
        parsed_exprs = z3.parse_smt2_string(clean_smt)
        solver.add(parsed_exprs)

        result = solver.check()
        logger.info(f"[Z3] Check completato. Risultato: {result}")

        # UNSAT = Equivalente (Divergenza impossibile)
        return result == z3.unsat
    except Exception as e:
        logger.error(f"[Z3-FAIL] Errore sintattico nello script generato: {e}")
        return None


def get_absolute_file_path(source_path: Path, target_file_rel: str) -> Path | None:
    clean_rel = target_file_rel.lstrip("/")
    target_file_abs = source_path / clean_rel

    if not target_file_abs.exists():
        filename = Path(clean_rel).name
        for p in source_path.rglob(filename):
            if p.as_posix().endswith(clean_rel):
                return p
        return None
    return target_file_abs


def get_function_name_at_line(
    source_path: Path, target_file_rel: str, line_no: int
) -> str:
    """
    Individua il nome della funzione/classe via AST.
    """
    target_file_abs = get_absolute_file_path(source_path, target_file_rel)
    if not target_file_abs:
        return ""

    try:
        source_code = target_file_abs.read_text(encoding="utf-8")
        tree = ast.parse(source_code)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                start = node.lineno
                end = getattr(node, "end_lineno", node.lineno)
                if start <= line_no <= end:
                    return node.name
        return "<modulo_globale>"
    except Exception as e:
        logger.error(f"[AST] Errore parsing: {e}")
    return ""


def get_callers_across_project(source_path: Path, func_name: str) -> list[str]:
    """
    Analisi dei chiamanti per estrarre gli invarianti di contesto.
    """
    if not func_name or func_name == "<modulo_globale>":
        return []

    callers = []
    for py_file in source_path.rglob("*.py"):
        try:
            source_code = py_file.read_text(encoding="utf-8")
            if func_name not in source_code:
                continue
            tree = ast.parse(source_code)
            lines = source_code.splitlines()
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for subnode in ast.walk(node):
                        if isinstance(subnode, ast.Call):
                            name = ""
                            if isinstance(subnode.func, ast.Name):
                                name = subnode.func.id
                            elif isinstance(subnode.func, ast.Attribute):
                                name = subnode.func.attr
                            if name == func_name:
                                start = node.lineno - 1
                                end = getattr(node, "end_lineno", len(lines))
                                callers.append(
                                    f"File: {py_file.name}\n"
                                    + "\n".join(lines[start:end])
                                )
                                break
        except Exception:
            continue
    return callers


def prompt_huggingface_llm(context_data: dict) -> str:
    """
    Genera il prompt e logga integralmente payload e risposta.
    """

    hf_api_key = settings.HF_API_KEY
    hf_endpoint = settings.HF_ENDPOINT_URL

    if not hf_api_key or not hf_endpoint:
        logger.error("[LLM] API Key o Endpoint non configurati.")
        return ""

    role = "Role: You are a formal verification reasoning engine and Python mutation analysis expert. You translate Python code analysis into STRICT SMT-LIB v2.6 code."
    context = f"Context (Sliced Code S):\n{json.dumps(context_data, indent=2)}"
    task = """Task: Prove contextual equivalence between original and mutated code.
We DO NOT know the exact mutation that mutmut applied.
CoT Steps:
1. Examine the original code at exactly 'mutated_line'. Identify one or more likely standard Python mutations (e.g. operators like + to -, < to <=, True to False, continue to break, removing a line, etc.) that could occur at that line.
2. Select the most mathematically relevant/challenging mutation to analyze and explicitly state what you believe the mutated code (I_mut) looks like.
3. Identify callers and guard conditions from the context.
4. Define Global Invariant IG based on these guards.
5. Model original (I_orig) and mutated (I_mut) behavior.

CRITICAL SMT-LIB v2.6 RULES:
- ABSOLUTELY NO custom sorts like 'List', 'Either', 'Tuple', 'Array' or 'Any'. Use ONLY 'Int', 'String', 'Bool', or 'Real'.
- To model Python objects, simplify them into basic Int/Bool/String representations, or use uninterpreted functions.
- Do NOT declare built-in sorts like 'Bool', 'Int', 'Real', 'String'. They are implicitly available.
- Use (declare-fun <name> (<sorts>) <sort>) for your variables and functions.
- Use (declare-const <name> <sort>) for constants.
- String constants must be in double quotes (e.g., "admin").
- Use prefix notation: (= x 10), (not (= a b)), (and p q).
- The final assertion MUST exactly be: (assert (not (= I_orig I_mut))).
- NEVER define duplicate sorts.

Output ONLY the SMT-LIB code block inside ```smt ... ```."""

    payload = {
        "messages": [{"role": "user", "content": f"{role}\n\n{context}\n\n{task}"}]
    }

    logger.info("========== PROMPT SENT TO LLM ==========")
    logger.info(json.dumps(payload, indent=2))
    logger.info("========================================")

    headers = {
        "Authorization": f"Bearer {hf_api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(hf_endpoint, headers=headers, json=payload, timeout=60)

        if response.status_code != 200:
            logger.error(f"[LLM] Errore API {response.status_code}: {response.text}")
            return ""

        res = response.json()
        content = ""
        if "choices" in res:
            content = res["choices"][0]["message"]["content"]
        elif isinstance(res, list):
            content = res[0].get("generated_text", "")
        else:
            content = res.get("generated_text", "")

        # --- LOG DELLA RISPOSTA ---
        logger.info("========== LLM RAW RESPONSE ==========")
        logger.info(content)
        logger.info("======================================")

        return content
    except Exception as e:
        logger.error(f"[LLM] Fallimento chiamata: {e}")
        return ""


def process_equivalent_mutants(analysis, source_path: Path):
    """
    Pipeline principale: match esatto per i file, match 'startswith' per le directory.
    """
    # from backend.projects.services import get_mutant_diff (Removed to avoid diff)

    targets = MutationResult.objects.filter(analysis=analysis, status="survived")

    survived_mutants = list(targets[:20])

    if not survived_mutants:
        logger.info("[PROCESS] Nessun mutante trovato con i criteri specificati.")
        return

    logger.info(f"[PROCESS] Inizio analisi su {len(survived_mutants)} mutanti.")

    for mutant in survived_mutants:
        try:
            logger.info(
                f"--- [ANALISI] Processando file: {mutant.file} (Linea: {mutant.line}) ---"
            )

            func_name = get_function_name_at_line(source_path, mutant.file, mutant.line)
            if not func_name:
                continue

            callers = get_callers_across_project(source_path, func_name)

            # Extract Original Code snippet (around the mutated line)
            original_code = ""
            target_file_abs = get_absolute_file_path(source_path, mutant.file)
            if target_file_abs:
                lines = target_file_abs.read_text(encoding="utf-8").splitlines()
                start_l = max(0, mutant.line - 10)
                end_l = min(len(lines), mutant.line + 10)
                # Attaching line numbers for the LLM
                original_code = "\n".join(
                    f"{i + 1}: {lines[i]}" for i in range(start_l, end_l)
                )

            context_data = {
                "mutated_method": func_name,
                "file": mutant.file,
                "mutated_line": mutant.line,
                "original_code_snippet": original_code,
                "callers": callers,
            }

            llm_reply = prompt_huggingface_llm(context_data)
            if not llm_reply:
                continue

            # Estrazione e verifica SMT
            smt_match = re.search(r"```smt\s*(.*?)\s*```", llm_reply, re.DOTALL)
            smt_block = smt_match.group(1) if smt_match else ""

            if not smt_block and "(declare-const" in llm_reply:
                smt_block = llm_reply[llm_reply.find("(declare-const") :]

            if smt_block:
                is_equiv = parse_and_verify_z3_smt(smt_block)
                mutant.is_equivalent = is_equiv
                if is_equiv is None:
                    mutant.description += f"\n\n--- SMT-LIB Verification ---\n{smt_block}\nErrore: Sintassi Z3 non valida o costrutti non supportati."
                else:
                    mutant.description += f"\n\n--- SMT-LIB Verification ---\n{smt_block}\nEquivalente: {is_equiv}"

            mutant.save(update_fields=["is_equivalent", "description"])

        except Exception as e:
            logger.error(f"[ERROR] Mutante {mutant.id}: {e}")
