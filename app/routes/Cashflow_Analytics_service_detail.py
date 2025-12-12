from app.utils.data_loader import (
    get_latest_date,
    query_table_date_filter,
    get_raw_table
)
import pandas as pd

def read_table_from_db():

    # 12か月前の月初を計算
    latest_date = get_latest_date()
    start_date = max(
        (latest_date - pd.DateOffset(months=12)).replace(day=1),
        pd.to_datetime("2024-10-01")
    )
    df_balance = query_table_date_filter("balance_detail", start_date, latest_date)
    #print(df_balance)

    df_item_attribute = get_raw_table("item_attribute")

    return df_balance, df_item_attribute