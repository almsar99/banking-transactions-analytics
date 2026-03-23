from banking_transactions_analytics.utils import load_transactions_from_excel
from banking_transactions_analytics.views import main_page


def main() -> None:
    df = load_transactions_from_excel("data/operations.xlsx")
    result = main_page("2021-12-31 23:59:59", df)
    print(result)


if __name__ == "__main__":
    main()
