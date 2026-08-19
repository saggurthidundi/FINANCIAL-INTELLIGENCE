import os
from config.logging_config import logger

class SECEdgarClient:
    def __init__(self, user_agent: str = "FinVisionAI Research admin@finvision.io"):
        self.headers = {"User-Agent": user_agent}

    def fetch_sample_filing(self, ticker: str, save_path: str = "./data/sample_filing.txt") -> str:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        content = f"""
        UNITED STATES SECURITIES AND EXCHANGE COMMISSION
        FORM 10-K ANNUAL REPORT FOR {ticker.upper()}
        FISCAL YEAR ENDED 2025

        ITEM 1A. RISK FACTORS
        1. Competition in Next-Gen Compute and AI Infrastructure remains elevated across all segments.
        2. Supply chain disruptions regarding high-bandwidth memory (HBM3e) chips could restrict gross margins.
        3. Compliance obligations under generative AI data sovereignty laws create operational overhead.

        ITEM 7. MANAGEMENT'S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION
        Consolidated net revenue increased 18% year-over-year driven by scalable cloud enterprise contracts.
        Operating cash flows expanded to record levels following automated infrastructure cost optimizations.
        """
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(content.strip())
        logger.info(f"Mock 10-K filing generated for {ticker} at {save_path}")
        return save_path