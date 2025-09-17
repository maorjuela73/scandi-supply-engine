import requests
from flask import current_app
import json

class GDELTAdapter:
    def __init__(self, base_url=None, timeout=None):
        self.base_url = base_url or current_app.config["GDELT_BASE"]
        self.timeout = timeout or current_app.config.get("GDELT_TIMEOUT", 10)

    def build_params(self, query, maxrecords=75):
        # Términos específicos de modern slavery para enfocar la búsqueda
        slavery_terms = [
            "slavery", "labor"
        ]
        
        # Combinar la consulta de la empresa con términos de esclavitud moderna
        enhanced_query = f"{query} ({' OR '.join(slavery_terms)})"
        
        return {
            "format": "json",
            "timespan": "FULL",
            "query": enhanced_query,
            "mode": "artlist",
            "maxrecords": maxrecords,
            "sort": "hybridrel"
        }

    def fetch(self, query, maxrecords=75):
        params = self.build_params(query, maxrecords)
        try:
            resp = requests.get(self.base_url, params=params, timeout=self.timeout)
            resp.raise_for_status()
            
            # Verificar que la respuesta no esté vacía
            if not resp.content:
                current_app.logger.warning("GDELT API returned empty response")
                return {"articles": []}
            
            # Verificar el tipo de contenido antes de intentar parsear JSON
            content_type = resp.headers.get('content-type', '')
            if 'application/json' not in content_type:
                current_app.logger.warning(f"GDELT API returned non-JSON content: {content_type}")
                return {"articles": []}
            
            # Parsear JSON con manejo robusto de errores
            try:
                data = resp.json()
            except json.JSONDecodeError as e:
                current_app.logger.error(f"GDELT JSON decode error: {e}. Response content: {resp.text[:200]}")
                return {"articles": []}
                
            return self.normalize(data)
            
        except requests.exceptions.Timeout:
            current_app.logger.error("GDELT API request timed out")
            return {"articles": []}
        except requests.exceptions.ConnectionError:
            current_app.logger.error("GDELT API connection error")
            return {"articles": []}
        except requests.exceptions.HTTPError as e:
            current_app.logger.error(f"GDELT API HTTP error: {e}")
            return {"articles": []}
        except Exception as e:
            current_app.logger.exception(f"GDELT fetch unexpected error: {e}")
            return {"articles": []}

    def normalize(self, raw):
        try:
            # Manejar diferentes formatos de respuesta
            if isinstance(raw, dict):
                articles = raw.get("articles", [])
            elif isinstance(raw, list):
                articles = raw
            else:
                articles = []
                
            normalized = []
            for a in articles:
                # Asegurar que cada artículo sea un diccionario
                if not isinstance(a, dict):
                    continue
                    
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
            
        except Exception as e:
            current_app.logger.exception(f"GDELT normalization error: {e}")
            return {"articles": []}