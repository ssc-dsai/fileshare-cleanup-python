# all prompt templates (easy to tune)
# Classification/prompts.py
def get_stage1_prompt(candidates: list, text_sample: str) -> str:
    return f"""Classify into ONE top-level Function.
Possible: {', '.join(candidates[:40])} ... (total {len(candidates)})

Text (first 2000 chars): {text_sample}

Respond ONLY with valid JSON:
{{"function_en": "Exact match from list", "function_fr": "", "function_conf": 0.XX}}"""

def get_stage2_prompt(function_en: str, candidates: list, text_sample: str) -> str:
    return f"""Given Function: {function_en}
Classify into ONE Sub-Function.
Possible: {', '.join(candidates)}

Text: {text_sample}

Respond ONLY JSON: {{"sub_function_en": "...", "sub_function_fr": "...", "sub_function_conf": 0.XX}}"""

def get_stage3_prompt(sub_function_en: str, candidates: list, text_sample: str) -> str:
    return f"""Given Sub-Function: {sub_function_en}
Classify into ONE Business Process.
Possible: {', '.join(candidates)}

Text: {text_sample}

Respond ONLY JSON:
{{"business_process_en": "...", "business_process_fr": "...", "business_process_conf": 0.XX}}"""

# Add similar functions for stage2 and stage3...