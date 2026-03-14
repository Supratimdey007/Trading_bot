
from __future__ import annotations

import hashlib
import hmac
import time
from typing import Any
from urllib.parse import urlencode

import requests

from logging_config import get_logger

BASE_URL = "https://testnet.binancefuture.com"
RECV_WINDOW = 5000

logger = get_logger("trading_bot.client")


class BinanceAPIError(Exception):
    def __init__(self, status_code: int, code: int, message: str):
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(f"HTTP {status_code} | code={code} | {message}")


class BinanceFuturesClient:
    def __init__(self, api_key: str, api_secret: str, timeout: int = 10):
        if not api_key or not api_secret:
            raise ValueError("api_key and api_secret must not be empty.")
        self._api_key = api_key
        self._api_secret = api_secret
        self._timeout = timeout
        self._session = requests.Session()
        self._session.headers.update(
            {
                "X-MBX-APIKEY": self._api_key,
                "Content-Type": "application/x-www-form-urlencoded",
            }
        )
        logger.debug("BinanceFuturesClient initialised (base_url=%s)", BASE_URL)

    def _sign(self, params: dict) -> dict:
        params["timestamp"] = int(time.time() * 1000)
        params["recvWindow"] = RECV_WINDOW
        query_string = urlencode(params)
        signature = hmac.new(
            self._api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    def _request(
        self,
        method: str,
        endpoint: str,
        params: dict | None = None,
        signed: bool = False,
    ) -> Any:
        params = params or {}
        if signed:
            params = self._sign(params)

        url = BASE_URL + endpoint
        logger.debug("→ %s %s  params=%s", method.upper(), url, params)

        try:
            if method.upper() == "GET":
                response = self._session.get(url, params=params, timeout=self._timeout)
            elif method.upper() == "POST":
                response = self._session.post(url, data=params, timeout=self._timeout)
            elif method.upper() == "DELETE":
                response = self._session.delete(url, params=params, timeout=self._timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
        except requests.exceptions.ConnectionError as exc:
            logger.error("Network connection error: %s", exc)
            raise
        except requests.exceptions.Timeout as exc:
            logger.error("Request timed out: %s", exc)
            raise

        logger.debug("← HTTP %s  body=%s", response.status_code, response.text[:500])

        try:
            data = response.json()
        except ValueError:
            response.raise_for_status()
            return {}

        if isinstance(data, dict) and "code" in data and data["code"] != 200:
            err_code = data["code"]
            err_msg = data.get("msg", "Unknown error")
            logger.error("Binance API error: HTTP %s | code=%s | %s", response.status_code, err_code, err_msg)
            raise BinanceAPIError(response.status_code, err_code, err_msg)

        if not response.ok:
            response.raise_for_status()

        return data

    def get_server_time(self) -> dict:
        return self._request("GET", "/fapi/v1/time")

    def get_account_info(self) -> dict:
        return self._request("GET", "/fapi/v2/account", signed=True)

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: float | None = None,
        time_in_force: str = "GTC",
        reduce_only: bool = False,
    ) -> dict:
        params: dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
        }

        if order_type == "LIMIT":
            if price is None:
                raise ValueError("price is required for LIMIT orders.")
            params["price"] = price
            params["timeInForce"] = time_in_force

        if reduce_only:
            params["reduceOnly"] = "true"

        logger.info(
            "Placing %s %s order | symbol=%s qty=%s price=%s",
            side, order_type, symbol, quantity,
            price if price else "MARKET",
        )
        response = self._request("POST", "/fapi/v1/order", params=params, signed=True)
        logger.info(
            "Order placed successfully | orderId=%s status=%s",
            response.get("orderId"), response.get("status"),
        )
        return response

    def cancel_order(self, symbol: str, order_id: int) -> dict:
        params = {"symbol": symbol, "orderId": order_id}
        return self._request("DELETE", "/fapi/v1/order", params=params, signed=True)

    def get_open_orders(self, symbol: str | None = None) -> list:
        params = {}
        if symbol:
            params["symbol"] = symbol.upper()
        return self._request("GET", "/fapi/v1/openOrders", params=params, signed=True)
