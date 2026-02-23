import json
from unittest.mock import patch

import pandas as pd
import pytest

from banking_transactions_analytics.views import main_page


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "Дата операции": ["2023-05-01"],
            "Сумма операции": [-100],
            "Номер карты": ["1234567812345678"],
            "Сумма платежа": [100],
            "Категория": ["Test"],
            "Описание": ["Test desc"],
        }
    )


@patch("banking_transactions_analytics.views.get_currency_rates")
@patch("banking_transactions_analytics.views.get_stock_prices")
def test_main_page_basic(mock_stock, mock_currency, sample_df):
    mock_currency.return_value = []
    mock_stock.return_value = []

    result = main_page("2023-05-20 12:00:00", sample_df)
    parsed = json.loads(result)

    assert "greeting" in parsed
    assert "cards" in parsed
    assert "top_transactions" in parsed
    assert "currency_rates" in parsed
    assert "stock_prices" in parsed
    assert "meta" in parsed


@patch("banking_transactions_analytics.views.get_currency_rates")
@patch("banking_transactions_analytics.views.get_stock_prices")
def test_main_page_empty_dataframe(mock_stock, mock_currency):
    mock_currency.return_value = []
    mock_stock.return_value = []

    empty_df = pd.DataFrame(
        columns=[
            "Дата операции",
            "Сумма операции",
            "Номер карты",
            "Сумма платежа",
            "Категория",
            "Описание",
        ]
    )

    result = main_page("2023-05-20 12:00:00", empty_df)
    data = json.loads(result)

    assert data["cards"] == []
    assert data["top_transactions"] == []
    assert "generated_at" in data["meta"]


@patch("banking_transactions_analytics.views.get_currency_rates")
@patch("banking_transactions_analytics.views.get_stock_prices")
def test_main_page_currency_exception(mock_stock, mock_currency, sample_df):
    mock_currency.side_effect = Exception("API fail")
    mock_stock.return_value = []

    result = main_page("2023-05-20 12:00:00", sample_df)
    data = json.loads(result)

    assert data["currency_rates"] == []


@patch("banking_transactions_analytics.views.get_currency_rates")
@patch("banking_transactions_analytics.views.get_stock_prices")
def test_main_page_stock_exception(mock_stock, mock_currency, sample_df):
    mock_currency.return_value = []
    mock_stock.side_effect = Exception("API fail")

    result = main_page("2023-05-20 12:00:00", sample_df)
    data = json.loads(result)

    assert data["stock_prices"] == []
