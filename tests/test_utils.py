from datetime import datetime
from unittest.mock import patch

import pandas as pd
import requests

from banking_transactions_analytics.utils import (
    calculate_cards_summary,
    filter_transactions_by_period,
    get_greeting,
    get_top_transactions,
)


def test_get_greeting_morning() -> None:
    dt = datetime(2023, 1, 1, 8, 0)
    assert get_greeting(dt) == "Доброе утро"


def test_get_greeting_day() -> None:
    dt = datetime(2023, 1, 1, 14, 0)
    assert get_greeting(dt) == "Добрый день"


def test_get_greeting_evening() -> None:
    dt = datetime(2023, 1, 1, 20, 0)
    assert get_greeting(dt) == "Добрый вечер"


def test_get_greeting_night() -> None:
    dt = datetime(2023, 1, 1, 2, 0)
    assert get_greeting(dt) == "Доброй ночи"


def test_filter_transactions_by_period() -> None:
    data = pd.DataFrame(
        {
            "Дата операции": [
                "2023-05-01",
                "2023-05-10",
                "2023-05-25",
                "2023-04-30",
            ],
            "Сумма операции": [100, 200, 300, 400],
        }
    )

    dt = datetime(2023, 5, 20)

    result = filter_transactions_by_period(data, dt)

    assert len(result) == 2


def test_calculate_cards_summary() -> None:

    data = pd.DataFrame(
        {
            "Номер карты": ["1234567812345814", "1234567812345814", "9876543212347512"],
            "Сумма операции": [-1000, -262, -794],
        }
    )

    result = calculate_cards_summary(data)

    assert len(result) == 2

    card1 = next(item for item in result if item["last_digits"] == "5814")
    assert card1["total_spent"] == 1262
    assert card1["cashback"] == 12.62


def test_get_top_transactions() -> None:
    import pandas as pd

    data = pd.DataFrame(
        {
            "Дата операции": [
                "2023-05-01",
                "2023-05-02",
                "2023-05-03",
                "2023-05-04",
                "2023-05-05",
                "2023-05-06",
            ],
            "Сумма платежа": [100, 500, 200, 700, 300, 400],
            "Категория": ["A", "B", "C", "D", "E", "F"],
            "Описание": ["a", "b", "c", "d", "e", "f"],
        }
    )

    result = get_top_transactions(data)

    assert len(result) == 5
    assert result[0]["amount"] == 700
    assert result[0]["category"] == "D"


def test_load_transactions_from_excel(tmp_path):
    import pandas as pd

    # создаём временный Excel
    test_file = tmp_path / "test.xlsx"
    df_original = pd.DataFrame({"A": [1, 2, 3]})
    df_original.to_excel(test_file, index=False)

    from banking_transactions_analytics.utils import load_transactions_from_excel

    df_loaded = load_transactions_from_excel(str(test_file))

    assert len(df_loaded) == 3
    assert list(df_loaded.columns) == ["A"]


@patch("banking_transactions_analytics.utils.requests.get")
def test_get_currency_rates_api_error(mock_get):
    mock_get.side_effect = requests.exceptions.RequestException()

    from banking_transactions_analytics.utils import get_currency_rates

    result = get_currency_rates(["USD"])
    assert result == []


def test_get_currency_rates_no_api_key(monkeypatch):
    from banking_transactions_analytics import utils

    monkeypatch.setattr(utils, "FMP_API_KEY", None)

    result = utils.get_currency_rates(["USD"])
    assert result == []


@patch("banking_transactions_analytics.utils.requests.get")
def test_get_currency_rates_empty_response(mock_get):
    mock_get.return_value.json.return_value = {}
    mock_get.return_value.raise_for_status.return_value = None

    from banking_transactions_analytics.utils import get_currency_rates

    result = get_currency_rates(["USD"])
    assert result == []


@patch("banking_transactions_analytics.utils.requests.get")
def test_get_stock_prices_api_error(mock_get):
    import requests

    mock_get.side_effect = requests.exceptions.RequestException()

    from banking_transactions_analytics.utils import get_stock_prices

    result = get_stock_prices(["AAPL"])
    assert result == []


@patch("banking_transactions_analytics.utils.requests.get")
def test_get_currency_rates_success(mock_get):
    mock_get.return_value.raise_for_status.return_value = None
    mock_get.return_value.json.return_value = [{"symbol": "USD", "price": 90.5}]

    from banking_transactions_analytics.utils import get_currency_rates

    result = get_currency_rates(["USD"])
    assert result == [{"currency": "USD", "rate": 90.5}]


def test_get_stock_prices_no_api_key(monkeypatch):
    from banking_transactions_analytics import utils

    monkeypatch.setattr(utils, "FMP_API_KEY", None)

    result = utils.get_stock_prices(["AAPL"])
    assert result == []


@patch("banking_transactions_analytics.utils.requests.get")
def test_get_stock_prices_success(mock_get):
    mock_get.return_value.raise_for_status.return_value = None
    mock_get.return_value.json.return_value = [{"symbol": "AAPL", "price": 150.0}]

    from banking_transactions_analytics.utils import get_stock_prices

    result = get_stock_prices(["AAPL"])
    assert result == [{"stock": "AAPL", "price": 150.0}]
