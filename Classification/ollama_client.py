# Classification/ollama_client.py
#set OLLAMA_MAX_LOADED_MODELS=2
#set OLLAMA_KEEP_ALIVE=-2
#ollama serve
#qwen2.5:7b
#qwen2.5vl:7b
#http://localhost:11434
"""
Ollama client wrapper for text classification, title generation, and vision tasks.
Handles multimodal input (text + image path) and robust JSON response parsing.
"""

import json
import logging
import re
from pathlib import Path

import ollama
from json_repair import repair_json

logger = logging.getLogger(__name__)


def classify(
    question: str,
    image_path: str | None = None,
    temperature: float = 0.15,
    max_tokens: int = 512,
    model: str = "qwen2.5:7b",
    force_json_mode: bool = True,
) -> dict:
    """
    Call Ollama (text-only or multimodal) and return parsed JSON.

    Returns dict with:
        'parsed': dict (successful parse) or {}
        'raw': raw response string
        'error': error message or None
    """
    if not model:
        raise ValueError("Model name required (e.g. 'qwen2.5:7b' or 'qwen2.5vl:7b')")

    logger.debug(
        f"Ollama classify | model={model} | temp={temperature} | "
        f"tokens={max_tokens} | image={bool(image_path)}"
    )

    # Enforce JSON output in prompt
    json_instruction = """
Respond **EXCLUSIVELY** with valid JSON — nothing else.
No text, no markdown, no code blocks, no explanations.
Use lowercase key names (e.g. "title", "visual_summary").
Example: {"title": "Your value here"}
"""
    full_prompt = question.strip() + "\n\n" + json_instruction

    try:
        # Prepare options
        options = {
            "temperature": temperature,
            "num_predict": max_tokens,
        }

        # Add format="json" if supported and requested
        if force_json_mode:
            options["format"] = "json"

        if image_path:
            # Vision mode
            response = ollama.generate(
                model=model,
                prompt=full_prompt,
                images=[str(Path(image_path).resolve())],
                options=options
            )
            raw = response.get("response", "").strip()
        else:
            # Text-only mode
            response = ollama.chat(
                model=model,
                messages=[{"role": "user", "content": full_prompt}],
                options=options
            )
            raw = response["message"]["content"].strip()

        if not raw:
            return {"parsed": {}, "raw": "", "error": "Empty response from Ollama"}

        # ── Aggressive cleaning for common Ollama response issues ───────────────────────
        cleaned = raw

        # Remove markdown fences
        cleaned = re.sub(r'^```json\s*', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\s*```$', '', cleaned, flags=re.IGNORECASE)

        # Remove any leading/trailing junk before/after JSON
        cleaned = re.sub(r'^.*?\{', '{', cleaned, flags=re.DOTALL)
        cleaned = re.sub(r'\}.*?$', '}', cleaned, flags=re.DOTALL)

        cleaned = cleaned.strip()

        # Step 1: Try direct parse
        try:
            parsed = json.loads(cleaned)
            return {"parsed": parsed, "raw": raw, "error": None}
        except json.JSONDecodeError:
            pass

        # Step 2: Repair
        try:
            repaired = repair_json(cleaned)
            if isinstance(repaired, dict):
                logger.debug("JSON repaired successfully")
                return {"parsed": repaired, "raw": raw, "error": None}
        except Exception as repair_err:
            logger.debug(f"JSON repair failed: {repair_err}")

        return {"parsed": {}, "raw": raw, "error": "Failed to parse response as JSON"}

    except ollama.ResponseError as re_err:
        err_msg = f"Ollama ResponseError: {re_err.error} (status {re_err.status_code})"
        logger.error(err_msg)
        return {"parsed": {}, "raw": "", "error": err_msg}

    except Exception as e:
        err_msg = f"Ollama call failed: {type(e).__name__} - {str(e)}"
        logger.exception(err_msg)
        return {"parsed": {}, "raw": "", "error": err_msg}