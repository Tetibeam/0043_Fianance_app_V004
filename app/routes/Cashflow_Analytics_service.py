from .Cashflow_Analytics_service_detail import read_table_from_db
from app.utils.data_loader import get_latest_date
from app.utils.dashboard_utility import make_vector, graph_individual_setting

import pandas as pd
import plotly.graph_objects as go
import json


def _build_summary(df_balance, df_emergency_buffer):
    latest = get_latest_date()
    latest_beginning_of_month = latest.replace(day=1) 
    three_month_ago = (latest - pd.DateOffset(months=3)) + pd.offsets.MonthBegin(-1)
    six_month_ago = (latest - pd.DateOffset(months=6)) + pd.offsets.MonthBegin(-1)

    #print(latest, latest_beginning_of_month, three_month_ago)

    df = df_balance.copy()

    # Collection
    df_current = (
        df[
            (df["date"] >= three_month_ago) & (df["date"] < latest_beginning_of_month) &
            (df["収支タイプ"] == "一般収支")
        ].groupby("収支カテゴリー")[["金額","目標"]].sum()
    )
    df_past = (
        df[
            (df["date"] >= six_month_ago) & (df["date"] < three_month_ago) &
            (df["収支タイプ"] == "一般収支")
        ].groupby("収支カテゴリー")[["金額","目標"]].sum()
    )

    # Fire Progress-3m
    fire_progress_current = df_current["金額"].sum() / df_current["目標"].sum()
    fire_progress_past = df_past["金額"].sum() / df_past["目標"].sum()

    # Net Saving-3m
    net_saving_current = df_current["金額"].sum()
    net_saving_past = df_past["金額"].sum()

    # Saving Rate-3m
    saving_rate_current = net_saving_current / df_current.loc["収入", "金額"]
    saving_rate_past = net_saving_past / df_past.loc["収入", "金額"]

    # Financial Runway
    emergency_buffer_current = df_emergency_buffer[
        df_emergency_buffer["date"] == latest_beginning_of_month
    ]["資産額"].iloc[0]
    emergency_buffer_past = df_emergency_buffer[
        df_emergency_buffer["date"] == three_month_ago
    ]["資産額"].iloc[0]

    financial_runway_current = emergency_buffer_current / (abs(df_current.loc["支出", "金額"]) / 3)
    financial_runway_past = emergency_buffer_past / (abs(df_past.loc["支出", "金額"]) / 3)

    #print(fire_progress_current, net_saving_current, saving_rate_current, financial_runway_current)
    #print(fire_progress_past, net_saving_past, saving_rate_past, financial_runway_past)

    latest_str = latest.strftime("%y/%m/%d")
    return {
        "latest_date": latest_str,
        "fire_progress_3m": round(fire_progress_current*100,1),
        "fire_progress_3m_vector": make_vector(fire_progress_current, fire_progress_past),
        "net_saving_3m": round(net_saving_current),
        "net_saving_3m_vector": make_vector(net_saving_current, net_saving_past),
        "saving_rate_3m": round(saving_rate_current*100,1),
        "saving_rate_3m_vector": make_vector(saving_rate_current, saving_rate_past),
        "financial_runway": str(round(financial_runway_current)) + " months",
        "financial_runway_vector": make_vector(financial_runway_current, financial_runway_past),
    }

def _build_target_trajectory(df_balance):
    # 日付設定
    latest = get_latest_date()
    latest_month = latest.replace(day=1)
    three_month_later = latest_month + pd.DateOffset(months=3)
    nine_month_ago = latest_month - pd.DateOffset(months=9)

    #print(latest_month, three_month_later, nine_month_ago)
    #　データ生成
    mask = (
        (df_balance["date"] >= nine_month_ago) & (df_balance["date"] < three_month_later)&
        (df_balance["収支タイプ"] == "一般収支")
    )
    df_sub = df_balance[mask].groupby(["date","収支カテゴリー"])[["金額","目標"]].sum().reset_index()

    #グラフ
    x_values = (
        df_sub[df_sub["収支カテゴリー"]=="収入"].set_index("date")
        .resample("MS").sum().index.strftime("%y-%m").tolist()
    )
    y1_values = (
        df_sub[df_sub["収支カテゴリー"]=="収入"].set_index("date")
        .resample("MS").sum()["金額"].astype(int).tolist()
    )
    y2_values = (
        df_sub[df_sub["収支カテゴリー"]=="収入"].set_index("date")
        .resample("MS").sum()["目標"].astype(int).tolist()
    )
    y3_values = (
        df_sub[df_sub["収支カテゴリー"]=="支出"].set_index("date")
        .resample("MS").sum()["金額"].astype(int).tolist()
    )
    y4_values = (
        df_sub[df_sub["収支カテゴリー"]=="支出"].set_index("date")
        .resample("MS").sum()["目標"].astype(int).tolist()
    )
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=x_values, y=y1_values, name="Actual Income",
        hovertemplate = '<i>x</i>: %{x}<br><i>y</i>: ¥%{y:,}<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=x_values, y=y2_values, mode="lines+markers", name="Target Income",
        hovertemplate = '<i>x</i>: %{x}<br><i>y</i>: ¥%{y:,}<extra></extra>'
    ))
    fig.add_trace(go.Bar(
        x=x_values, y=y3_values, name="Actual Expense",
        hovertemplate = '<i>x</i>: %{x}<br><i>y</i>: ¥%{y:,}<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=x_values, y=y4_values, mode="lines+markers", name="Target Expense",
        hovertemplate = '<i>x</i>: %{x}<br><i>y</i>: ¥%{y:,}<extra></extra>'
    ))

    fig = graph_individual_setting(fig, "date", "%y-%m", "Income and Expense", "¥", "")
    # metaでID付与
    fig.update_layout(meta={"id": "target_trajectory"})

    #fig.show()

    fig_dict = fig.to_dict()
    json_str = json.dumps(fig_dict)

    return json_str

def build_Cashflow_Analytics_payload(include_graphs=False, include_summary=False):
    df_balance, df_item_attribute, df_emergency_buffer = read_table_from_db()

    result = {"ok":True, "summary": {}, "graphs": {}}

    if include_summary:
        result["summary"] = _build_summary(df_balance,df_emergency_buffer)
        
    if include_graphs:
        result["graphs"] = {
            "target_trajectory": _build_target_trajectory(df_balance),
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

    df_balance, df_item_attribute, df_emergency_buffer = read_table_from_db()
    #print(_build_summary(df_balance,df_emergency_buffer))
    _build_target_trajectory(df_balance)
    #print(build_Cashflow_Analytics_payload(include_graphs=False, include_summary=True))