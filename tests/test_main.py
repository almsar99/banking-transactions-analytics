import runpy
from unittest.mock import patch

from banking_transactions_analytics.main import main


def test_main_runs():
    with (
        patch("banking_transactions_analytics.main.load_transactions_from_excel") as mock_load,
        patch("banking_transactions_analytics.main.main_page") as mock_page,
        patch("builtins.print") as mock_print,
    ):

        mock_load.return_value = "fake_df"
        mock_page.return_value = "{}"

        main()

        mock_load.assert_called_once()
        mock_page.assert_called_once()
        mock_print.assert_called_once()


def test_main_as_script():
    runpy.run_module("banking_transactions_analytics.main", run_name="__main__")
