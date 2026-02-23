import json
import pandas as pd

from banking_transactions_analytics.views import main_page


def test_main_page_basic() -> None:
    data = pd.DataFrame(
        {
            "Дата операции": ["2023-05-01", "2023-05-02"],
            "Сумма операции": [-1000, -500],
            "Сумма платежа": [1000, 500],
            "Номер карты": ["1234567812345814", "1234567812345814"],
            "Категория": ["A", "B"],
            "Описание": ["a", "b"],
        }
    )

    result = main_page("2023-05-20 12:00:00", data)
    parsed = json.loads(result)

    assert "greeting" in parsed
    assert "cards" in parsed
    assert "top_transactions" in parsed
