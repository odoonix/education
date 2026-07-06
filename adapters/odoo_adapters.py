import requests
import urllib3
from typing import List, Dict, Any
from config.settings import get_settings
from utils.logger import logger

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class OdooAdapter:
    def __init__(self):
        self.settings = get_settings()
        self.base_url = f"{self.settings.ODOO_URL}/json/2"
        self.headers = {
            "Authorization": f"Bearer {self.settings.ODOO_API_KEY}",
            "Content-Type": "application/json",
        }

    def _call(self, model: str, method: str, params: dict = None) -> Any:
        url = f"{self.base_url}/{model}/{method}"
        payload = params or {}

        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30, verify=False)
            
            if response.status_code != 200:
                logger.error("Odoo API Error", status=response.status_code, response_text=response.text[:300])
                raise Exception(f"Odoo returned {response.status_code}")

            result = response.json()
            return result if not isinstance(result, dict) else result.get("result", result)
        except Exception as e:
            logger.error("API call failed", model=model, method=method, error=str(e))
            raise

    def get_contacts(self, limit: int = 10) -> List[Dict]:
        logger.info("Fetching contacts", limit=limit)
        params = {
            "domain": [],
            "fields": ["id", "name", "email", "phone", "city", "active"],
            "limit": limit
        }
        return self._call("res.partner", "search_read", params)

    def get_products(self, limit: int = 10) -> List[Dict]:
        logger.info("Fetching products", limit=limit)
        params = {
            "domain": [],
            "fields": ["id", "name", "default_code", "list_price", "type", "active"],
            "limit": limit
        }
        return self._call("product.product", "search_read", params)

    def get_sale_orders(self, limit: int = 5) -> List[Dict]:
        logger.info("Fetching sale orders", limit=limit)
        params = {
            "domain": [],
            "fields": ["id", "name", "partner_id", "date_order", "state", "amount_total", "amount_paid", "is_expired"],
            "limit": limit
        }
        return self._call("sale.order", "search_read", params)