import json
import logging
from datetime import datetime

import pandas as pd

from banking_transactions_analytics.utils import (
    calculate_cards_summary,
    filter_transactions_by_period,
    get_currency_rates,
    get_greeting,
    get_stock_prices,
    get_top_transactions,
    load_user_settings,
)

logger = logging.getLogger(__name__)


def main_page(date_str: str, df: pd.DataFrame) -> str:
    """
    Generates JSON response for the Main page.
    """

    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

    filtered = filter_transactions_by_period(df, dt)

    settings = load_user_settings()

    try:
        currency_rates = get_currency_rates(settings.get("user_currencies", []))
    except Exception as e:
        logger.warning("Currency API failed: %s", e)
        currency_rates = []

    try:
        stock_prices = get_stock_prices(settings.get("user_stocks", []))
    except Exception as e:
        logger.warning("Stock API failed: %s", e)
        stock_prices = []

    result = {
        "greeting": get_greeting(dt),
        "cards": calculate_cards_summary(filtered),
        "top_transactions": get_top_transactions(filtered),
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
        "meta": {"generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
    }

    return json.dumps(result, ensure_ascii=False, indent=4)
