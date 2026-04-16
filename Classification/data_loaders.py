# load hierarchy CSV, RegEx CSV
import logging
import re
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

def load_hierarchy(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        logger.warning(f"Hierarchy CSV missing: {csv_path}")
        return pd.DataFrame()
    df = pd.read_csv(csv_path, encoding="utf-8")
    logger.info(f"Loaded {len(df)} hierarchy rows")
    return df


def load_regex_db(csv_path: Path) -> dict:
    """
    Load RegEx database with support for groups (AND/OR).
    Returns:
        {
            'singles': [list of single rules],
            'groups': {group_id: {'logic': 'AND'|'OR', 'rules': [list]}}
        }
    """
    if not csv_path.exists() or csv_path.stat().st_size == 0:
        logger.info("RegEx DB empty/missing – skipping")
        return {'singles': [], 'groups': {}}

    df = pd.read_csv(csv_path)
    df = df[df['status'] == 'Activate'].copy()

    singles = []
    groups = {}

    for _, row in df.iterrows():
        rule = row.to_dict()
        # Pre-compile regex once for massive speed
        try:
            rule['pattern'] = re.compile(rule['pattern'], re.IGNORECASE)
        except re.error as e:
            logger.warning(f"Invalid regex skipped: {rule.get('rule_name')} - {e}")
            continue

        gid = rule.get('group_id')
        logic = rule.get('group_logic', 'SINGLE')

        if pd.isna(gid) or str(gid).strip() == '' or logic == 'SINGLE':
            singles.append(rule)
        else:
            gid = str(gid)
            if gid not in groups:
                groups[gid] = {'logic': logic, 'rules': []}
            groups[gid]['rules'].append(rule)

    logger.info(f"Loaded {len(singles)} single rules + {len(groups)} grouped rule sets from RegEx-db.csv")
    return {'singles': singles, 'groups': groups}