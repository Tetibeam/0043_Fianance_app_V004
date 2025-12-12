from flask import Blueprint, jsonify
from werkzeug.exceptions import InternalServerError
import os
from .routes_helper import apply_etag
from .Cashflow_Analytics_service import build_Cashflow_Analytics_payload

Cashflow_Analytics_bp = Blueprint("Cashflow_Analytics", __name__, url_prefix="/api/Cashflow_Analytics")

# API 用ルート
@Cashflow_Analytics_bp.route("/", methods=["GET"])
def index():
    """
    API root: 簡単なメタ情報を返す
    """
    payload = {
        "service": "Portfolio_Command_Center",
        "version": "1.0",
        "endpoints": {
            "graphs": "/api/Cashflow_Analytics/graphs",
            "summary": "/api/Cashflow_Analytics/summary"
        }
    }
    return jsonify(payload)

@Cashflow_Analytics_bp.route("/graphs", methods=["GET"])
def graphs():
    """
    グラフ用データを返すエンドポイント。
    フロントはここから時系列データ・メタ情報を受け取り描画する。
    """
    try:
        payload = build_Cashflow_Analytics_payload(include_graphs=True, include_summary=False)
        return apply_etag(payload)
    except Exception as e:
        import traceback
        traceback.print_exc()
        # ログはアプリ側で出している想定
        raise InternalServerError(description=str(e))


@Cashflow_Analytics_bp.route("/summary", methods=["GET"])
def summary():
    """
    サマリ（軽量）だけほしいフロントのための簡易エンドポイント。
    """
    try:
        payload = build_Cashflow_Analytics_payload(include_graphs=False, include_summary=True)
        return apply_etag(payload)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise InternalServerError(description=str(e))