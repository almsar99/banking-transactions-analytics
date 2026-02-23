import json
import logging
import re
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


def investment_bank(month: str, transactions: list[dict[str, Any]], limit: int) -> float:
    """
    Calculate the amount that could be saved to the investment bank
    by rounding transactions up to the specified limit.

    :param month: Month in format 'YYYY-MM'
    :param transactions: List of transaction dictionaries
    :param limit: Rounding limit (10, 50, 100)
    :return: Total amount saved
    """

    # Strict validation of month format YYYY-MM
    if not re.fullmatch(r"\d{4}-\d{2}", month):
        logger.error("Invalid month format: %s", month)
        raise ValueError("Month must be in 'YYYY-MM' format")

    target_month = datetime.strptime(month, "%Y-%m")

    if limit <= 0:
        raise ValueError("Limit must be a positive integer")

    total_saved: float = 0.0

    for transaction in transactions:
        try:
            operation_date_str = transaction["Дата операции"]
            amount = float(transaction["Сумма операции"])
        except KeyError as exc:
            logger.error("Missing required transaction fields")
            raise KeyError("Transaction must contain required fields") from exc

        operation_date = datetime.strptime(operation_date_str, "%Y-%m-%d")

        # Filter by year and month and only positive expenses
        if operation_date.year == target_month.year and operation_date.month == target_month.month and amount > 0:
            remainder = amount % limit
            if remainder != 0:
                rounded_amount = amount + (limit - remainder)
                total_saved += rounded_amount - amount

    return round(total_saved, 2)


def simple_search(query: str, transactions: list[dict[str, Any]]) -> str:
    """
    Search transactions by query in 'Описание' or 'Категория'.
    """

    if not query:
        raise ValueError("Query must not be empty")

    query = query.strip()

    root = query[:-1] if len(query) > 3 else query
    pattern = re.compile(re.escape(root), re.IGNORECASE)

    matched: list[dict[str, Any]] = []

    for transaction in transactions:
        description = str(transaction.get("Описание", ""))
        category = str(transaction.get("Категория", ""))

        if pattern.search(description) or pattern.search(category):
            matched.append(transaction)

    logger.info(
        "Found %d matching transactions for query '%s'",
        len(matched),
        query,
    )

    return json.dumps(matched, ensure_ascii=False)


def search_by_phone(transactions: list[dict[str, Any]]) -> str:
    """
    Search transactions containing mobile phone numbers in description.
    """

    pattern = re.compile(r"\+7\s\d{3}\s\d{2,3}-\d{2}-\d{2}")
    matched: list[dict[str, Any]] = []

    for transaction in transactions:
        description = str(transaction.get("Описание", ""))

        if pattern.search(description):
            matched.append(transaction)

    logger.info("Found %d transactions with phone numbers", len(matched))

    return json.dumps(matched, ensure_ascii=False)


def search_transfers_to_individuals(transactions: list[dict[str, Any]]) -> str:
    """
    Search transactions that are transfers to individuals.
    Category must be 'Переводы' and description must contain
    a name in format 'Имя Б.'.
    """

    pattern = re.compile(r"[А-ЯЁ][а-яё]+\s[А-ЯЁ]\.")
    matched: list[dict[str, Any]] = []

    for transaction in transactions:
        category = str(transaction.get("Категория", ""))
        description = str(transaction.get("Описание", ""))

        if category == "Переводы" and pattern.search(description):
            matched.append(transaction)

    logger.info(
        "Found %d transfer transactions to individuals",
        len(matched),
    )

    return json.dumps(matched, ensure_ascii=False)
