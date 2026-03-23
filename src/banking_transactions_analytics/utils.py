import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import TypedDict, cast

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

FMP_API_KEY = os.getenv("FMP_API_KEY")


# =========================
# TypedDict definitions
# =========================


class CurrencyRate(TypedDict):
    currency: str
    rate: float


class StockPrice(TypedDict):
    stock: str
    price: float


# =========================
# Core helpers
# =========================


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

    df["Дата операции"] = pd.to_datetime(
        df["Дата операции"],
        format="mixed",
        errors="coerce",
    )

    start_of_month = dt.replace(day=1)

    return df[(df["Дата операции"] >= start_of_month) & (df["Дата операции"] <= dt)]


def calculate_cards_summary(df: pd.DataFrame) -> list[dict[str, float | str]]:
    """
    Calculates spending and cashback per card.
    """

    logger.info("Calculating cards summary")

    df = df[df["Сумма операции"] < 0]

    grouped = df.groupby("Номер карты")["Сумма операции"].sum().abs().reset_index()

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
        format="mixed",
        errors="coerce",
    )

    top = df.sort_values(by="Сумма платежа", ascending=False).head(5)

    result: list[dict[str, str | float]] = []

    for _, row in top.iterrows():
        result.append(
            {
                "date": row["Дата операции"].strftime("%d.%m.%Y"),
                "amount": float(row["Сумма платежа"]),
                "category": str(row["Категория"]),
                "description": str(row["Описание"]),
            }
        )

    return result


# =========================
# Data loading
# =========================


def load_transactions_from_excel(path: str) -> pd.DataFrame:
    """
    Loads transactions from Excel file.
    """

    logger.info("Loading transactions from Excel: %s", path)
    return pd.read_excel(path)


def load_user_settings(path: str = "user_settings.json") -> dict[str, list[str]]:
    """
    Loads user settings from JSON file.
    """

    with open(Path(path), encoding="utf-8") as file:
        data = json.load(file)

    return cast(dict[str, list[str]], data)


# =========================
# API integration (FMP)
# =========================


def get_currency_rates(currencies: list[str]) -> list[CurrencyRate]:
    """
    Fetches currency rates from Financial Modeling Prep API.
    """

    if not FMP_API_KEY:
        logger.warning("FMP_API_KEY not found")
        return []

    result: list[CurrencyRate] = []

    try:
        url = f"https://financialmodelingprep.com/api/v3/quote/" f"{','.join(currencies)}?apikey={FMP_API_KEY}"

        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        for item in data:
            result.append(
                {
                    "currency": str(item["symbol"]),
                    "rate": round(float(item["price"]), 2),
                }
            )

    except requests.RequestException as error:
        logger.error("Currency fetch error: %s", error)

    return result


def get_stock_prices(stocks: list[str]) -> list[StockPrice]:
    """
    Fetches stock prices from Financial Modeling Prep API.
    """

    if not FMP_API_KEY:
        logger.warning("FMP_API_KEY not found")
        return []

    result: list[StockPrice] = []

    try:
        url = f"https://financialmodelingprep.com/api/v3/quote/" f"{','.join(stocks)}?apikey={FMP_API_KEY}"

        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        for item in data:
            result.append(
                {
                    "stock": str(item["symbol"]),
                    "price": float(item["price"]),
                }
            )

    except requests.RequestException as error:
        logger.error("Stock fetch error: %s", error)

    return result
