import logging
from datetime import datetime

import pandas as pd

logger = logging.getLogger(__name__)


def get_greeting(dt: datetime) -> str:
    """
    Returns greeting based on time of day.
    """

    hour = dt.hour

    if 5 <= hour < 12:
        return "Доброе утро"
    if 12 <= hour < 18:
        return "Добрый день"
    if 18 <= hour < 23:
        return "Добрый вечер"
    return "Доброй ночи"


def filter_transactions_by_period(
    df: pd.DataFrame,
    dt: datetime,
) -> pd.DataFrame:
    """
    Filters transactions from start of month to given datetime.
    """

    logger.info("Filtering transactions for main page period")

    df = df.copy()
    df["Дата операции"] = pd.to_datetime(df["Дата операции"])

    start_of_month = dt.replace(day=1)

    return df[
        (df["Дата операции"] >= start_of_month)
        & (df["Дата операции"] <= dt)
    ]


def calculate_cards_summary(df: pd.DataFrame) -> list[dict[str, float | str]]:
    """
    Calculates spending and cashback per card.
    """

    logger.info("Calculating cards summary")

    df = df[df["Сумма операции"] < 0]

    grouped = (
        df.groupby("Номер карты")["Сумма операции"]
        .sum()
        .abs()
        .reset_index()
    )

    result: list[dict[str, float | str]] = []

    for _, row in grouped.iterrows():
        last_digits = str(row["Номер карты"])[-4:]
        total_spent = float(row["Сумма операции"])
        cashback = round(total_spent / 100, 2)

        result.append(
            {
                "last_digits": last_digits,
                "total_spent": round(total_spent, 2),
                "cashback": cashback,
            }
        )

    return result


def get_top_transactions(df: pd.DataFrame) -> list[dict[str, str | float]]:
    """
    Returns top 5 transactions by payment amount.
    """

    logger.info("Calculating top transactions")

    df = df.copy()
    df["Дата операции"] = pd.to_datetime(
        df["Дата операции"],
        dayfirst=True,
    )

    top = df.sort_values(by="Сумма платежа", ascending=False).head(5)

    result: list[dict[str, str | float]] = []

    for _, row in top.iterrows():
        result.append(
            {
                "date": row["Дата операции"].strftime("%d.%m.%Y"),
                "amount": float(row["Сумма платежа"]),
                "category": row["Категория"],
                "description": row["Описание"],
            }
        )

    return result


logger = logging.getLogger(__name__)


def load_transactions_from_excel(path: str) -> pd.DataFrame:
    """
    Loads transactions from Excel file.
    """

    logger.info("Loading transactions from Excel: %s", path)

    df = pd.read_excel(path)

    return df

