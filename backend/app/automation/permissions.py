from enum import StrEnum

class Risk(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

ACTION_RISK = {
    "open_app": Risk.LOW,
    "open_url": Risk.LOW,
    "open_folder": Risk.LOW,
    "search_files": Risk.LOW,
    "create_folder": Risk.LOW,
    "create_file": Risk.MEDIUM,
    "rename_file": Risk.MEDIUM,
    "copy_file": Risk.MEDIUM,
    "move_file": Risk.MEDIUM,
    "delete_file": Risk.HIGH,
}

def risk_for(action: str) -> Risk:
    if action not in ACTION_RISK:
        raise ValueError(f"Unsupported automation action: {action}")
    return ACTION_RISK[action]

def requires_confirmation(action: str) -> bool:
    return risk_for(action) != Risk.LOW
