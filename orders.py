

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from client import BinanceFuturesClient, BinanceAPIError
from validators import validate_all, ValidationError
from logging_config import get_logger

logger = get_logger("trading_bot.orders")


@dataclass
class OrderRequest:
    symbol: str
    side: str
    order_type: str
    quantity: float
    price: float | None = None


@dataclass
class OrderResult:
    success: bool
    order_id: int | None = None
    status: str | None = None
    executed_qty: float | None = None
    avg_price: float | None = None
    raw_response: dict = field(default_factory=dict)
    error_message: str | None = None


def build_order_request(
    symbol: str,
    side: str,
    order_type: str,
    quantity,
    price=None,
) -> OrderRequest:
    clean = validate_all(symbol, side, order_type, quantity, price)
    return OrderRequest(
        symbol=clean["symbol"],
        side=clean["side"],
        order_type=clean["order_type"],
        quantity=clean["quantity"],
        price=clean.get("price"),
    )


def place_order(client: BinanceFuturesClient, request: OrderRequest) -> OrderResult:
    try:
        response: dict[str, Any] = client.place_order(
            symbol=request.symbol,
            side=request.side,
            order_type=request.order_type,
            quantity=request.quantity,
            price=request.price,
        )
    except ValidationError as exc:
        logger.error("Validation error: %s", exc)
        return OrderResult(success=False, error_message=str(exc))
    except BinanceAPIError as exc:
        logger.error("Binance API error: %s", exc)
        return OrderResult(success=False, error_message=str(exc))
    except Exception as exc:
        logger.exception("Unexpected error while placing order: %s", exc)
        return OrderResult(success=False, error_message=f"Unexpected error: {exc}")

    executed_qty = response.get("executedQty")
    avg_price = response.get("avgPrice")

    return OrderResult(
        success=True,
        order_id=response.get("orderId"),
        status=response.get("status"),
        executed_qty=float(executed_qty) if executed_qty is not None else None,
        avg_price=float(avg_price) if avg_price is not None else None,
        raw_response=response,
    )


def format_request_summary(request: OrderRequest) -> str:
    lines = [
        "┌─── Order Request ────────────────────────────",
        f"│  Symbol     : {request.symbol}",
        f"│  Side       : {request.side}",
        f"│  Type       : {request.order_type}",
        f"│  Quantity   : {request.quantity}",
    ]
    if request.price is not None:
        lines.append(f"│  Price      : {request.price}")
    lines.append("└──────────────────────────────────────────────")
    return "\n".join(lines)


def format_order_result(result: OrderResult) -> str:
    if not result.success:
        return (
            "┌─── Order FAILED ─────────────────────────────\n"
            f"│  Error : {result.error_message}\n"
            "└──────────────────────────────────────────────"
        )

    lines = [
        "┌─── Order SUCCESS ────────────────────────────",
        f"│  Order ID     : {result.order_id}",
        f"│  Status       : {result.status}",
    ]
    if result.executed_qty is not None:
        lines.append(f"│  Executed Qty : {result.executed_qty}")
    if result.avg_price is not None:
        lines.append(f"│  Avg Price    : {result.avg_price}")
    lines.append("└──────────────────────────────────────────────")
    return "\n".join(lines)
