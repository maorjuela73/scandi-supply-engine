import requests
from flask import current_app

class GDELTAdapter:
    def __init__(self, base_url=None, timeout=None):
        self.base_url = base_url or current_app.config["GDELT_BASE"]
        self.timeout = timeout or current_app.config.get("GDELT_TIMEOUT", 10)

    def build_params(self, query, maxrecords=75):
        return {
            "format": "json",
            "timespan": "FULL",
            "query": query,
            "mode": "artlist",
            "maxrecords": maxrecords,
            "sort": "hybridrel"
        }

    def fetch(self, query, maxrecords=75):
        params = self.build_params(query, maxrecords)
        try:
            resp = requests.get(self.base_url, params=params, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            return self.normalize(data)
        except Exception as e:
            current_app.logger.exception("GDELT fetch error: %s", e)
            return {"articles": []}

    def normalize(self, raw):
        articles = raw.get("articles", []) if isinstance(raw, dict) else []
        normalized = []
        for a in articles:
            normalized.append({
                "url": a.get("url"),
                "title": a.get("title"),
                "domain": a.get("domain"),
                "seendate": a.get("seendate"),
                "socialimage": a.get("socialimage"),
                "language": a.get("language"),
                "sourcecountry": a.get("sourcecountry"),
                "raw": a
            })
        return {"articles": normalized}
