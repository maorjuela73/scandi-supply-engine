Perfecto 🚀. Te armo un **`README.md` completo**, claro y orientado a desarrolladores para que puedan poner en marcha tu proyecto en local sin fricción.

---

```markdown
# ⚙️ scandi-supply-engine

Backend service for scanning and assessing **modern slavery risks** in supply chains.  
This API powers the [`scandi-supply-scan`](https://github.com/<your-org>/scandi-supply-scan) frontend, enabling companies, researchers, and the public to explore the risk level of brands and products using open data sources like [GDELT](https://www.gdeltproject.org/).

---

## 🚀 Features
- **Company Scan API** → `/api/v1/scan?query=<company>`
  - Fetches recent news articles from GDELT
  - Normalizes and enriches results
  - Provides a basic risk score and summary
- **Modular Architecture**
  - `adapters` for external data sources (e.g., GDELT)
  - `services` for risk scoring & business logic
  - `api` for REST endpoints
- **Caching layer** with support for in-memory or Redis
- **Health check endpoint** at `/health`

---

## 🛠 Tech Stack
- Python **3.10+**
- [Flask](https://flask.palletsprojects.com/) for the API
- [Requests](https://docs.python-requests.org/) for external data integration
- [Flask-Caching](https://flask-caching.readthedocs.io/) for caching
- [pytest](https://docs.pytest.org/) for testing

---

## ⚡ Getting Started (Local Setup)

### 1. Clone the repository
```bash
git clone https://github.com/<your-org>/scandi-supply-engine.git
cd scandi-supply-engine
````

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
.venv\Scripts\activate      # Windows PowerShell
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the development server

```bash
python run.py
```

The API should now be running on:

```
http://127.0.0.1:5000
```

---

## 🧪 Testing

Run the test suite with:

```bash
pytest -v
```

---

## 📡 Example API Usage

Search for a company (e.g., Nike):

```bash
curl "http://127.0.0.1:5000/api/v1/scan?query=Nike"
```

Example response:

```json
{
  "company": "Nike",
  "risk_score": 5,
  "risk_level": "Medium",
  "articles": [
    {
      "title": "Nike Air Max 1000 Release",
      "url": "https://wwd.com/...",
      "domain": "wwd.com",
      "date": "2025-08-07"
    }
  ]
}
```

---

## ✅ Roadmap

* [ ] Persistent storage (PostgreSQL for Scans & Articles)
* [ ] Advanced risk heuristics (keywords, severity, recency)
* [ ] Authentication with API keys
* [ ] OpenAPI/Swagger documentation
* [ ] Dockerfile & CI/CD pipeline

---

## 🤝 Contributing

We welcome contributions!

* Fork the repository
* Create a feature branch (`feature/<short-description>`)
* Commit your changes following [Conventional Commits](https://www.conventionalcommits.org/)
* Submit a Pull Request

---

## 📜 License

MIT License. See [LICENSE](LICENSE) for details.

```