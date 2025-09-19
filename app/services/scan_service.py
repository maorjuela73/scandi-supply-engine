from flask import current_app
from textblob import TextBlob
import re
from collections import Counter

class ScanService:
    def __init__(self, adapter=None):
        self.adapter = adapter or GDELTAdapter()
        
        # Palabras clave específicas de modern slavery con pesos
        self.slavery_keywords = {
            'forced labor': 40, 'human trafficking': 45, 'child labor': 50,
            'debt bondage': 35, 'exploitation': 30, 'sweatshop': 25,
            'forced overtime': 20, 'labor camp': 45, 'coercion': 25,
            'involuntary servitude': 40, 'wage theft': 20, 'recruitment fraud': 25
        }
        
        # Industrias de alto riesgo para modern slavery
        self.high_risk_industries = {
            'textile', 'garment', 'agriculture', 'mining',
            'construction', 'fishing', 'manufacturing', 'electronics'
        }
        
        # Regiones de alto riesgo para modern slavery
        self.high_risk_regions = {
            'China', 'India', 'Bangladesh', 'Pakistan',
            'Vietnam', 'Cambodia', 'Myanmar', 'Thailand'
        }
        
        # Dominios de medios confiables
        self.trusted_domains = {
            'reuters.com', 'bloomberg.com', 'wsj.com', 'ft.com',
            'nytimes.com', 'bbc.co.uk', 'theguardian.com', 'ap.org'
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
            
            # Análisis de sentimiento con TextBlob
            sentiment = self._analyze_sentiment(title)
            
            # Detección de palabras clave de modern slavery
            keyword_risk, found_keywords = self._check_slavery_keywords(title)
            article_risk += keyword_risk
            
            # Factor de región de alto riesgo
            if country in self.high_risk_regions:
                article_risk *= 1.5
                risk_explanations.append(f"Source from high-risk region: {country}")
            
            # Factor de industria de alto riesgo (basado en dominio)
            if self._check_high_risk_industry(domain):
                article_risk *= 1.4
                risk_explanations.append(f"High-risk industry domain: {domain}")
            
            # Factor de dominio confiable
            if domain in self.trusted_domains:
                article_risk *= 1.3
                risk_explanations.append(f"Reliable source: {domain}")
            
            # Factor de sentimiento negativo (usando TextBlob)
            if sentiment < -0.2:  # Umbral más estricto para negatividad
                article_risk *= (1 + abs(sentiment) * 0.7)  # Mayor peso al sentimiento negativo
                risk_explanations.append(f"Strong negative sentiment: {sentiment:.2f}")
            
            # Añadir explicaciones basadas en palabras clave encontradas
            if found_keywords:
                risk_explanations.append(f"Slavery keywords: {', '.join(found_keywords)}")
            
            total_risk += article_risk
        
        # Calcular riesgo promedio y normalizar a escala 0-100
        avg_risk = total_risk * 10 / len(articles) if articles else 0
        normalized_risk = min(100, avg_risk)
        
        # Crear explicación consolidada
        explanation = self._generate_explanation(normalized_risk, risk_explanations)
        
        return normalized_risk, explanation

    def _analyze_sentiment(self, text):
        """Analiza el sentimiento del texto usando TextBlob"""
        analysis = TextBlob(text)
        return analysis.sentiment.polarity

    def _check_slavery_keywords(self, text):
        """Busca palabras clave de modern slavery en el texto"""
        risk_score = 0
        found_keywords = []
        
        for keyword, weight in self.slavery_keywords.items():
            # Búsqueda de frases completas
            if re.search(r'\b' + keyword.replace(' ', r'\s+') + r'\b', text):
                risk_score += weight
                found_keywords.append(keyword)
        
        return risk_score, found_keywords

    def _check_high_risk_industry(self, domain):
        """Detectar industrias de alto riesgo basado en el dominio"""
        domain_lower = domain.lower()
        return any(industry in domain_lower for industry in self.high_risk_industries)

    def _generate_explanation(self, risk_score, risk_explanations):
        """Genera una explicación basada en el puntaje de riesgo y las razones"""
        if risk_score < 20:
            base = "Low modern slavery risk. Minimal concerning content found."
        elif risk_score < 50:
            base = "Moderate modern slavery risk. Several risk factors detected."
        elif risk_score < 75:
            base = "High modern slavery risk. Significant concerning content identified."
        else:
            base = "Critical modern slavery risk. Urgent attention required."
        
        # Añadir las explicaciones específicas si existen
        if risk_explanations:
            # Contar frecuencia de explicaciones y mostrar las más comunes
            explanation_counts = Counter(risk_explanations)
            top_explanations = [f"{count}x {explanation}" for explanation, count in explanation_counts.most_common(3)]
            details = " Key factors: " + "; ".join(top_explanations)
            return base + details
        
        return base

    def risk_level(self, score):
        """Determina el nivel de riesgo basado en el puntaje"""
        if score >= 70:
            return "Critical"
        elif score >= 50:
            return "High"
        elif score >= 30:
            return "Medium"
        else:
            return "Low"

    def summarize(self, company_name, query):
        """Procesa los artículos y genera un resumen de riesgo de modern slavery"""
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
            "news": articles[:3]
            # "articlesAnalyzed": len(articles)
        }

    def categorize(self, company_name: str) -> str:
        """Categorización basada en industrias de riesgo para modern slavery"""
        name_lower = company_name.lower()
        if any(word in name_lower for word in ['textile', 'garment', 'clothing', 'fashion']):
            return "Textile & Apparel"
        elif any(word in name_lower for word in ['tech', 'electronic', 'computer', 'device']):
            return "Electronics"
        elif any(word in name_lower for word in ['agriculture', 'farm', 'food', 'produce']):
            return "Agriculture & Food"
        elif any(word in name_lower for word in ['mining', 'extraction', 'resource', 'natural']):
            return "Mining & Extraction"
        elif any(word in name_lower for word in ['construction', 'build', 'contractor', 'engineering']):
            return "Construction"
        else:
            return "General"