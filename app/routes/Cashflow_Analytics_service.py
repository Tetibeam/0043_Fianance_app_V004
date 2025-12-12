from .Cashflow_Analytics_service_detail import read_table_from_db
from app.utils.data_loader import get_latest_date
import pandas as pd


def _build_summary(df_balance):
    latest = get_latest_date()
    one_month_ago_eom = (latest - pd.DateOffset(months=1)) + pd.offsets.MonthEnd(0)
    three_month_ago = (latest - pd.DateOffset(months=3)) + pd.offsets.MonthBegin(-1)
    df = df_balance.copy()

    # Collection
    mask = (
        (df["date"] >= three_month_ago) & (df["date"] <= one_month_ago_eom) &
        (df["収支タイプ"] == "一般収支")
    )
    df_balance_Collection = df[mask].groupby("収支カテゴリー")[["金額","目標"]].sum()
    #print(df_balance_Collection)

    # Fire Progress-3m
    fire_progress_3m = df_balance_Collection["金額"].sum() / df_balance_Collection["目標"].sum()

    # Net Saving-3m
    net_saving_3m = df_balance_Collection["金額"].sum()

    # Saving Rate-3m
    saving_rate_3m = net_saving_3m / df_balance_Collection.loc["収入", "金額"]

    #print(fire_progress_3m, net_saving_3m, saving_rate_3m)

    # Financial Runway
    
    latest_str = latest.strftime("%y/%m/%d")
    return {
        "latest_date": latest_str,
        "Fire Progress-3m": round(fire_progress_3m*100,1),
        "Net Saving-3m": round(net_saving_3m),
        "Saving Rate-3m": round(saving_rate_3m*100,1),
    }

def build_Cashflow_Analytics_payload(include_graphs=False, include_summary=False):
    df_balance, df_item_attribute = read_table_from_db()

    result = {"ok":True, "summary": {}, "graphs": {}}

    if include_summary:
        result["summary"] = _build_summary(df_balance)
        
    if include_graphs:
        result["graphs"] = {
            #"r": _build_asset_tree_map(df_collection,df_item_attribute),
            #"target_deviation": _build_target_deviation(df_collection),
            #"portfolio_efficiency_map": _build_portfolio_efficiency_map(df_collection,df_item_attribute),
            #"liquidity_pyramid": _build_liquidity_pyramid(df_collection,df_item_attribute),
            #"true_risk_exposure_flow": _build_true_risk_exposure_flow(df_collection),
            #"liquidity_horizon": _build_liquidity_horizon(df_collection_latest, df_asset_attribute, df_item_attribute)
        }
    return result

if __name__ == "__main__":
    import os
    base_dir = os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
    )
    # DBマネージャーの初期化
    from app.utils.db_manager import init_db
    init_db(base_dir)

    df_balance, df_item_attribute = read_table_from_db()
    #print(_build_summary(df_balance))
    print(build_Cashflow_Analytics_payload(include_graphs=False, include_summary=True))