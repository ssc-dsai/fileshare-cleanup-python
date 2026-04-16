# Classification/utils/metadata_enrichers.py
def enrich_static_fields(row: dict) -> dict:
    """
    Add static / fixed metadata fields to the row.
    """
    row["Technical Environment | Environnement technique"] = "Microsoft's Distributed File System (DFS)"
    row["Disposition Authorization / Autorisation de disposition"] = "2021/005"

    # Add more static fields here later (Retention Period, etc.)

    return row