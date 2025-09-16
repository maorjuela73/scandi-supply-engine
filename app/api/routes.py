from flask import Blueprint, request, jsonify, current_app
from ..services.scan_service import ScanService
from ..adapters.gdelt_adapter import GDELTAdapter
from .. import cache

api_bp = Blueprint("api", __name__)

@api_bp.route("/scan", methods=["GET"])
def scan():
    query = request.args.get("query")
    company = request.args.get("company") or query
    if not query:
        return jsonify({"error": "query parameter required"}), 400

    cache_key = f"scan:{query}"
    cached = cache.get(cache_key)
    if cached:
        current_app.logger.debug("cache hit %s", cache_key)
        return jsonify(cached), 200

    adapter = GDELTAdapter()
    service = ScanService(adapter)
    result = service.summarize(company, query)

    cache.set(cache_key, result, timeout=current_app.config.get("CACHE_DEFAULT_TIMEOUT", 300))
    return jsonify(result), 200
