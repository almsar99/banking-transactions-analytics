import json
import logging
from datetime import datetime

import pandas as pd

from banking_transactions_analytics.utils import (
    calculate_cards_summary,
    filter_transactions_by_period,
    get_greeting,
    get_top_transactions,
)

logger = logging.getLogger(__name__)


def main_page(date_str: str, df: pd.DataFrame) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

    filtered = filter_transactions_by_period(df, dt)

    result = {
        "greeting": get_greeting(dt),
        "cards": calculate_cards_summary(filtered),
        "top_transactions": get_top_transactions(filtered),
    }

    return json.dumps(result, ensure_ascii=False, indent=4)
