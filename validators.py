

from __future__ import annotations

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}


class ValidationError(ValueError):
    """Raised when user-supplied input fails validation."""


def validate_symbol(symbol: str) -> str:
    """Upper-case and check that the symbol is a non-empty string."""
    symbol = symbol.strip().upper()
    if not symbol:
        raise ValidationError("Symbol must not be empty.")
    if not symbol.isalnum():
        raise ValidationError(
            f"Symbol '{symbol}' contains invalid characters. "
            "Use alphanumeric values only, e.g. BTCUSDT."
        )
    return symbol


def validate_side(side: str) -> str:
    """Ensure side is BUY or SELL."""
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValidationError(
            f"Side '{side}' is invalid. Choose from: {', '.join(VALID_SIDES)}."
        )
    return side


def validate_order_type(order_type: str) -> str:
    """Ensure order type is MARKET or LIMIT."""
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Order type '{order_type}' is invalid. "
            f"Choose from: {', '.join(VALID_ORDER_TYPES)}."
        )
    return order_type


def validate_quantity(quantity: str | float) -> float:
    """Ensure quantity is a positive number."""
    try:
        qty = float(quantity)
    except (TypeError, ValueError):
        raise ValidationError(f"Quantity '{quantity}' is not a valid number.")
    if qty <= 0:
        raise ValidationError("Quantity must be greater than zero.")
    return qty


def validate_price(price: str | float | None, order_type: str) -> float | None:
    """
    Price is required for LIMIT orders and must be positive.
    For MARKET orders it is ignored (returns None).
    """
    if order_type == "MARKET":
        return None

    if price is None:
        raise ValidationError("Price is required for LIMIT orders.")

    try:
        p = float(price)
    except (TypeError, ValueError):
        raise ValidationError(f"Price '{price}' is not a valid number.")

    if p <= 0:
        raise ValidationError("Price must be greater than zero.")

    return p


def validate_all(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str | float,
    price: str | float | None = None,
) -> dict:
    """
    Run all validators and return a clean parameter dict.
    Raises ValidationError on the first failure encountered.
    """
    clean_symbol = validate_symbol(symbol)
    clean_side = validate_side(side)
    clean_type = validate_order_type(order_type)
    clean_qty = validate_quantity(quantity)
    clean_price = validate_price(price, clean_type)

    result = {
        "symbol": clean_symbol,
        "side": clean_side,
        "order_type": clean_type,
        "quantity": clean_qty,
    }
    if clean_price is not None:
        result["price"] = clean_price

    return result
