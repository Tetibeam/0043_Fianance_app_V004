from .Cashflow_Analytics_service_detail import read_table_from_db

def _build_summary(df_collection):
    pass


def build_Cashflow_Analytics_payload(include_graphs=False, include_summary=False):
    pass

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

    read_table_from_db()