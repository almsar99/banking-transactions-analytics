import json

import pytest

from banking_transactions_analytics.services import (
    investment_bank,
    search_by_phone,
    search_transfers_to_individuals,
    simple_search,
)


@pytest.fixture
def sample_transactions() -> list[dict[str, object]]:
    return [
        {"Дата операции": "2023-01-15", "Сумма операции": 1712.0},
        {"Дата операции": "2023-01-20", "Сумма операции": 305.0},
        {"Дата операции": "2023-02-10", "Сумма операции": 1000.0},
        {"Дата операции": "2023-01-25", "Сумма операции": -500.0},  # доход — игнорируется
    ]


def test_investment_bank_basic(sample_transactions: list[dict[str, object]]) -> None:
    result = investment_bank("2023-01", sample_transactions, 50)

    # 1712 -> 1750 (38)
    # 305 -> 350 (45)
    # -500 игнорируется
    assert result == 83.0


def test_investment_bank_other_month(sample_transactions: list[dict[str, object]]) -> None:
    result = investment_bank("2023-02", sample_transactions, 50)

    # 1000 уже кратно 50
    assert result == 0.0


@pytest.mark.parametrize(
    "month",
    ["2023/01", "2023-1", "January-2023"],
)
def test_invalid_month_format(month: str, sample_transactions: list[dict[str, object]]) -> None:
    with pytest.raises(ValueError):
        investment_bank(month, sample_transactions, 50)


def test_invalid_limit(sample_transactions: list[dict[str, object]]) -> None:
    with pytest.raises(ValueError):
        investment_bank("2023-01", sample_transactions, 0)


def test_missing_fields() -> None:
    transactions = [{"date": "2023-01-01", "amount": 1000}]

    with pytest.raises(KeyError):
        investment_bank("2023-01", transactions, 50)


@pytest.fixture
def search_transactions() -> list[dict[str, str]]:
    return [
        {"Описание": "Покупка в Ленте", "Категория": "Супермаркеты"},
        {"Описание": "Перевод Сергею", "Категория": "Переводы"},
        {"Описание": "Оплата МТС", "Категория": "Связь"},
    ]


def test_simple_search_by_description(search_transactions: list[dict[str, str]]) -> None:
    result = simple_search("лента", search_transactions)
    data = json.loads(result)

    assert len(data) == 1
    assert data[0]["Категория"] == "Супермаркеты"


def test_simple_search_by_category(search_transactions: list[dict[str, str]]) -> None:
    result = simple_search("переводы", search_transactions)
    data = json.loads(result)

    assert len(data) == 1
    assert data[0]["Описание"] == "Перевод Сергею"


def test_simple_search_no_results(search_transactions: list[dict[str, str]]) -> None:
    result = simple_search("кино", search_transactions)
    data = json.loads(result)

    assert len(data) == 0


def test_simple_search_empty_query(search_transactions: list[dict[str, str]]) -> None:
    with pytest.raises(ValueError):
        simple_search("", search_transactions)


def test_search_by_phone() -> None:
    transactions = [
        {"Описание": "Я МТС +7 921 11-22-33"},
        {"Описание": "Покупка в магазине"},
        {"Описание": "Тинькофф Мобайл +7 995 555-55-55"},
    ]

    result = search_by_phone(transactions)
    data = json.loads(result)

    assert len(data) == 2


def test_search_transfers_to_individuals() -> None:
    transactions = [
        {"Категория": "Переводы", "Описание": "Перевод Валерий А."},
        {"Категория": "Переводы", "Описание": "Перевод Сергей З."},
        {"Категория": "Переводы", "Описание": "Перевод компании ООО"},
        {"Категория": "Супермаркеты", "Описание": "Лента"},
    ]

    result = search_transfers_to_individuals(transactions)
    data = json.loads(result)

    assert len(data) == 2
