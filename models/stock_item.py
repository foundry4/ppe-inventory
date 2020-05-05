from dataclasses import dataclass


@dataclass
class InventoryItem:
    """Class for keeping track of an item in inventory."""
    item_name: str
    stock_level: int
    daily_usage: int
    stock_levels_note: str
    rag: str
    mutual_aid_received: int
    national_and_other_external_receipts: int
