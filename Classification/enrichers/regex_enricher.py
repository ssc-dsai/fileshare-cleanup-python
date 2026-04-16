"""
Classification/enrichers/regex_enricher.py

Deterministic RegEx enrichment layer.
Applies rules from RegEx-db.csv (singles + AND/OR groups).
Runs first and overrides other enrichers when matched.
"""
import logging
from pathlib import Path
from typing import Dict, Any

from project_config import REGEX_DB_PATH
from ..data_loaders import load_regex_db

logger = logging.getLogger(__name__)


def apply_regex_rules(text: str, original_path: str | None = None) -> Dict[str, Any]:
    """
    Apply all active rules from RegEx-db.csv.
    Returns dict of overrides to merge into metadata.

    Enhanced logging for visibility during development:
    - INFO level for every major step
    - Text preview
    - Rule-by-rule testing + result
    - Summary of hits and overrides
    """
    filename = Path(original_path).name if original_path else "unknown_document"

    logger.info("RegEx layer started | document: %s", filename)

    regex_data = load_regex_db(REGEX_DB_PATH)
    if not regex_data['singles'] and not regex_data['groups']:
        logger.info("No active regex rules found in RegEx-db.csv")
        return {}

    logger.info("Loaded %d single rules + %d grouped rule sets",
                len(regex_data['singles']), len(regex_data['groups']))

    # Show what the regex actually sees (very helpful for OCR artifacts)
    preview = text[:500].replace('\n', '\\n').replace('\r', '\\r')
    logger.info("RegEx input preview (first 500 chars): %s", preview)

    overrides: Dict[str, Any] = {}
    fired_singles = []
    fired_groups = []

    # Single rules – detailed per-rule logging
    for rule in regex_data['singles']:
        rule_name = rule.get('rule_name', 'unnamed_rule')
        target_field = rule.get('target_field', 'unknown_field')
        target_value = rule.get('target_value', 'unknown_value')

        logger.info("Testing rule '%s' → targets %s = %s",
                    rule_name, target_field, target_value)

        match = rule['pattern'].search(text)
        if match:
            # Handle group capture if requested
            value = target_value
            if '{group' in target_value and match.groups():
                try:
                    group_num = int(target_value.split('group')[1].split('}')[0])
                    value = match.group(group_num)
                except Exception as e:
                    logger.warning("Group capture failed for %s: %s", rule_name, e)

            overrides[target_field] = value
            fired_singles.append(f"{rule_name} → {target_field} = {value!r}")
            logger.info("MATCH SUCCESS: %s → %s = %s", rule_name, target_field, value)
        else:
            logger.info("No match for rule: %s", rule_name)

    # Grouped rules
    for group_id, group in regex_data['groups'].items():
        logic = group['logic']
        rules = group['rules']
        match_count = sum(1 for r in rules if r['pattern'].search(text))

        triggered = (logic == 'AND' and match_count == len(rules)) or \
                    (logic == 'OR' and match_count >= 1)

        if triggered:
            logger.info("GROUP TRIGGERED: %s (%s) – %d/%d rules matched",
                        group_id, logic, match_count, len(rules))
            for rule in rules:
                overrides[rule['target_field']] = rule['target_value']
            fired_groups.append(f"Group {group_id} ({logic}) – {match_count} matches")

    # Final summary – always logged at INFO
    if fired_singles or fired_groups:
        logger.info("═" * 60)
        logger.info("REGEX LAYER SUMMARY for %s", filename)
        if fired_singles:
            logger.info("Single rules matched (%d):", len(fired_singles))
            for msg in fired_singles:
                logger.info("  • %s", msg)
        if fired_groups:
            logger.info("Groups triggered (%d):", len(fired_groups))
            for msg in fired_groups:
                logger.info("  • %s", msg)
        logger.info("Final overrides applied: %s", overrides)
        logger.info("═" * 60)
    else:
        logger.info("RegEx layer finished – no matches / no overrides for %s", filename)

    return overrides