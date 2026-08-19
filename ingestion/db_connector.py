import os
import pandas as pd
from sqlalchemy import create_engine, text
from config.settings import settings
from config.logging_config import logger

class DatabaseConnector:
    def __init__(self, uri: str = settings.DATABASE_URL):
        db_file = uri.replace("sqlite:///", "")
        if db_file.startswith("./") or db_file.startswith("/"):
            db_dir = os.path.dirname(db_file)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
            
        self.engine = create_engine(uri, connect_args={"check_same_thread": False})
        self._init_sample_financial_tables()

    def _init_sample_financial_tables(self):
        try:
            with self.engine.begin() as conn:
                conn.execute(text('''
                    CREATE TABLE IF NOT EXISTS company_financials (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        company_ticker VARCHAR(10),
                        company_name VARCHAR(100),
                        fiscal_year INT,
                        fiscal_quarter VARCHAR(5),
                        revenue_millions FLOAT,
                        net_income_millions FLOAT,
                        operating_margin FLOAT,
                        sector VARCHAR(50)
                    );
                '''))
                res = conn.execute(text("SELECT COUNT(*) FROM company_financials")).scalar()
                if res == 0:
                    conn.execute(text('''
                        INSERT INTO company_financials 
                        (company_ticker, company_name, fiscal_year, fiscal_quarter, revenue_millions, net_income_millions, operating_margin, sector)
                        VALUES 
                        ('AAPL', 'Apple Inc.', 2025, 'Q3', 85777.0, 21448.0, 0.30, 'Technology'),
                        ('MSFT', 'Microsoft Corp.', 2025, 'Q3', 64727.0, 22036.0, 0.43, 'Technology'),
                        ('GOOGL', 'Alphabet Inc.', 2025, 'Q3', 88268.0, 26301.0, 0.32, 'Technology'),
                        ('JPM', 'JPMorgan Chase & Co.', 2025, 'Q3', 42654.0, 12898.0, 0.38, 'Financial Services'),
                        ('NVDA', 'NVIDIA Corp.', 2025, 'Q3', 30040.0, 16599.0, 0.62, 'Technology'),
                        ('AMZN', 'Amazon.com Inc.', 2025, 'Q3', 158877.0, 15328.0, 0.11, 'Consumer Cyclical');
                    '''))
                    logger.info("Sample financial warehouse records seeded.")
        except Exception as e:
            logger.warning(f"Database setup notice: {e}")

    def execute_raw_sql(self, sql_query: str):
        with self.engine.connect() as conn:
            result = conn.execute(text(sql_query))
            if result.returns_rows:
                return pd.DataFrame(result.fetchall(), columns=result.keys())
            return {"status": "executed"}