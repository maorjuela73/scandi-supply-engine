from flask import current_app
from ..adapters.gdelt_adapter import GDELTAdapter

class ScanService:
    def __init__(self, adapter: GDELTAdapter = None):
        self.adapter = adapter or GDELTAdapter()

    def compute_risk_score(self, articles):
        if not articles:
            return 0.0
        count = len(articles)
        base = min(count / 10.0, 8.0)  # simple heuristic
        serious = {"nytimes.com", "reuters.com", "guardian.co.uk", "bbc.co.uk"}
        bump = sum(1 for a in articles if a.get("domain") in serious)
        score = base + min(bump, 2.0)
        score = round(min(score, 10.0), 2)
        return score

    def risk_level(self, score):
        if score >= 7.5:
            return "High"
        if score >= 4.0:
            return "Medium"
        return "Low"

    def categorize(self, company_name: str) -> str:
        """Naive categorization by keywords; can later be replaced with ML model."""
        mapping = {
            "Nike": "Apparel",
            "Adidas": "Apparel",
            "iPhone": "Electronics",
            "Apple": "Electronics",
            "Tesla": "Automotive",
        }
        return mapping.get(company_name, "General")

    def summarize(self, company_name, query):
        data = self.adapter.fetch(query)
        articles = data.get("articles", [])
        score = self.compute_risk_score(articles)
        level = self.risk_level(score)

        explanation = (
            "Limited public evidence of high-severity issues."
            if score < 4
            else "Improved transparency but ongoing concerns in operations."
            if score < 7.5
            else "Complex supply chain with rare earth mining concerns in conflict regions."
        )

        return {
            "name": company_name,
            "riskScore": score,
            "riskLevel": level,
            "explanation": explanation,
            "category": self.categorize(company_name),
        }
