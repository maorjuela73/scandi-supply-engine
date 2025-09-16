from flask import current_app
from textblob import TextBlob
import re
from collections import Counter

class ScanService:
    def __init__(self, adapter=None):
        self.adapter = adapter or GDELTAdapter()
        
        # Palabras clave y sus pesos para diferentes categorías de riesgo
        self.risk_keywords = {
            'recall': 30, 'defect': 25, 'failure': 25, 'crash': 35, 
            'stall': 20, 'investigation': 20, 'lawsuit': 30, 'verdict': 25,
            'problem': 20, 'issue': 15, 'concern': 15, 'warn': 15,
            'fire': 40, 'explosion': 40, 'death': 50, 'injuries': 40,
            'controversy': 20, 'protest': 25, 'lawsuit': 30, 'settlement': 20,
            'decline': 15, 'drop': 15, 'fall': 15, 'plummet': 20
        }
        
        # Dominios de medios confiables (aumentan la credibilidad del riesgo)
        self.trusted_domains = {
            'reuters.com', 'bloomberg.com', 'wsj.com', 'ft.com',
            'nytimes.com', 'bbc.co.uk', 'theguardian.com', 'ap.org'
        }
        
        # Países con regulaciones estrictas (aumentan el riesgo percibido)
        self.strict_regulation_countries = {
            'United States', 'Canada', 'Germany', 'United Kingdom',
            'France', 'Japan', 'Australia', 'Sweden'
        }

    def compute_risk_score(self, articles):
        if not articles:
            return 0.0, "No articles found"
            
        total_risk = 0
        risk_explanations = []
        
        for article in articles:
            article_risk = 0
            title = article.get('title', '').lower()
            domain = article.get('domain', '')
            country = article.get('sourcecountry', '')
            
            # Análisis de sentimiento
            sentiment = self._analyze_sentiment(title)
            
            # Detección de palabras clave de riesgo
            keyword_risk, found_keywords = self._check_risk_keywords(title)
            article_risk += keyword_risk
            
            # Factor de dominio confiable
            if domain in self.trusted_domains:
                article_risk *= 1.3
                risk_explanations.append(f"Article from trusted domain {domain}")
            
            # Factor de país con regulaciones estrictas
            if country in self.strict_regulation_countries:
                article_risk *= 1.2
                risk_explanations.append(f"Article from strict regulation country {country}")
            
            # Factor de sentimiento negativo
            if sentiment < 0:
                article_risk *= (1 + abs(sentiment) * 0.5)
                risk_explanations.append("Negative sentiment detected")
            
            # Añadir explicaciones basadas en palabras clave encontradas
            if found_keywords:
                risk_explanations.append(f"Risk keywords found: {', '.join(found_keywords)}")
            
            total_risk += article_risk
        
        # Calcular riesgo promedio y normalizar a escala 0-100
        avg_risk = total_risk / len(articles)
        normalized_risk = min(100, avg_risk)
        
        # Crear explicación consolidada
        explanation = self._generate_explanation(normalized_risk, risk_explanations)
        
        return normalized_risk, explanation

    def _analyze_sentiment(self, text):
        """Analiza el sentimiento del texto usando TextBlob"""
        analysis = TextBlob(text)
        # Convertir polaridad (-1 a 1) a un factor multiplicativo
        return analysis.sentiment.polarity

    def _check_risk_keywords(self, text):
        """Busca palabras clave de riesgo en el texto"""
        risk_score = 0
        found_keywords = []
        
        for keyword, weight in self.risk_keywords.items():
            if re.search(r'\b' + keyword + r'\b', text):
                risk_score += weight
                found_keywords.append(keyword)
        
        return risk_score, found_keywords

    def _generate_explanation(self, risk_score, risk_explanations):
        """Genera una explicación basada en el puntaje de riesgo y las razones"""
        if risk_score < 30:
            base = "Low risk profile. Minimal concerning content found."
        elif risk_score < 60:
            base = "Moderate risk level. Several risk factors detected."
        else:
            base = "High risk level. Significant concerning content identified."
        
        # Añadir las explicaciones específicas si existen
        if risk_explanations:
            unique_explanations = list(set(risk_explanations))
            details = " Key factors: " + "; ".join(unique_explanations[:3])  # Limitar a 3 factores principales
            return base + details
        
        return base

    def risk_level(self, score):
        """Determina el nivel de riesgo basado en el puntaje"""
        if score >= 70:
            return "High"
        elif score >= 40:
            return "Medium"
        else:
            return "Low"

    def summarize(self, company_name, query):
        """Procesa los artículos y genera un resumen de riesgo"""
        data = self.adapter.fetch(query)
        articles = data.get("articles", [])
        
        # Calcular puntaje de riesgo
        risk_score, explanation = self.compute_risk_score(articles)
        risk_level = self.risk_level(risk_score)
        
        return {
            "name": company_name,
            "riskScore": round(risk_score, 2),
            "riskLevel": risk_level,
            "explanation": explanation,
            "category": self.categorize(company_name),
            "news": articles[:3],  # Devolver hasta 3 artículos para contexto
        }

    def categorize(self, company_name: str) -> str:
        """Categorización simple basada en palabras clave"""
        name_lower = company_name.lower()
        if any(word in name_lower for word in ['tech', 'software', 'computer', 'digital']):
            return "Technology"
        elif any(word in name_lower for word in ['bank', 'finance', 'capital', 'investment']):
            return "Finance"
        elif any(word in name_lower for word in ['auto', 'car', 'vehicle', 'motor']):
            return "Automotive"
        elif any(word in name_lower for word in ['oil', 'gas', 'energy', 'power']):
            return "Energy"
        elif any(word in name_lower for word in ['pharma', 'medical', 'health', 'biotech']):
            return "Healthcare"
        else:
            return "General"
