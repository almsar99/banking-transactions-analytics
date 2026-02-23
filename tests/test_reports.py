import pandas as pd

from banking_transactions_analytics.reports import spending_by_category, save_report
from unittest.mock import patch


def test_spending_by_category_basic() -> None:
    data = pd.DataFrame(
        {
            "Дата операции": [
                "2023-01-10",
                "2023-02-15",
                "2023-03-20",
                "2023-04-01",
            ],
            "Категория": [
                "Супермаркеты",
                "Супермаркеты",
                "Супермаркеты",
                "Развлечения",
            ],
            "Сумма операции": [-1000, -2000, -1500, -500],
        }
    )

    result = spending_by_category(data, "Супермаркеты", date="2023-04-01")

    # должны попасть 3 месяца назад от 1 апреля → январь включительно
    assert not result.empty
    assert result["Сумма операции"].sum() == 4500


def test_spending_by_category_without_date() -> None:
    data = pd.DataFrame(
        {
            "Дата операции": ["2023-01-10"],
            "Категория": ["Супермаркеты"],
            "Сумма операции": [-1000],
        }
    )

    result = spending_by_category(data, "Супермаркеты")

    assert isinstance(result, pd.DataFrame)


def test_save_report_with_dict(tmp_path) -> None:
    file_path = tmp_path / "test_report.json"

    @save_report(str(file_path))
    def dummy():
        return {"key": "value"}

    result = dummy()

    assert result == {"key": "value"}
    assert file_path.exists()


def test_save_report_os_error(tmp_path) -> None:
    @save_report(str(tmp_path / "fail.json"))
    def dummy():
        return {"key": "value"}

    with patch("builtins.open", side_effect=OSError):
        result = dummy()

    assert result == {"key": "value"}
