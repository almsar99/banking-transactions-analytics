import json
import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Callable, Optional, TypeVar, Any

import pandas as pd

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def save_report(filename: Optional[str] = None) -> Callable[[F], F]:
    """
    Decorator for saving report results to a file.
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)

            report_filename = (
                filename if filename else f"report_{func.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )

            try:
                with open(report_filename, "w", encoding="utf-8") as file:
                    if hasattr(result, "to_dict"):
                        json.dump(result.to_dict(), file, ensure_ascii=False, indent=4)
                    else:
                        json.dump(result, file, ensure_ascii=False, indent=4)

                logger.info("Report saved to %s", report_filename)

            except OSError as error:
                logger.error("Failed to save report: %s", error)

            return result

        return wrapper  # type: ignore

    return decorator


@save_report()
def spending_by_category(
    transactions: pd.DataFrame,
    category: str,
    date: str | None = None,
) -> pd.DataFrame:
    """
    Returns spending by category for the last 3 months from given date.
    """

    logger.info("Generating spending_by_category report")

    if date:
        end_date = datetime.strptime(date, "%Y-%m-%d")
    else:
        end_date = datetime.now()

    start_date = end_date - timedelta(days=90)

    df = transactions.copy()

    df["Дата операции"] = pd.to_datetime(df["Дата операции"])

    filtered = df[
        (df["Дата операции"] >= start_date)
        & (df["Дата операции"] <= end_date)
        & (df["Категория"] == category)
        & (df["Сумма операции"] < 0)
    ]

    result = filtered.groupby(filtered["Дата операции"].dt.to_period("M"))["Сумма операции"].sum().abs().reset_index()

    result["Дата операции"] = result["Дата операции"].astype(str)

    logger.info("Report generated successfully")

    return result
