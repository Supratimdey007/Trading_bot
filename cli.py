

from __future__ import annotations

import argparse
import os
import sys


try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from client import BinanceFuturesClient
from orders import (
    build_order_request,
    place_order,
    format_request_summary,
    format_order_result,
)
from validators import ValidationError
from logging_config import get_logger

logger = get_logger("trading_bot.cli")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Place Market / Limit orders on Binance Futures Testnet (USDT-M).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    creds = parser.add_argument_group("API credentials (or set via .env)")
    creds.add_argument("--api-key", default=None,
                       help="Binance Testnet API key (env: BINANCE_TESTNET_API_KEY)")
    creds.add_argument("--api-secret", default=None,
                       help="Binance Testnet API secret (env: BINANCE_TESTNET_API_SECRET)")

    order = parser.add_argument_group("Order parameters")
    order.add_argument("--symbol", required=True,
                       help="Trading pair, e.g. BTCUSDT")
    order.add_argument("--side", required=True,
                       choices=["BUY", "SELL"], type=str.upper,
                       help="BUY or SELL")
    order.add_argument("--type", dest="order_type", required=True,
                       choices=["MARKET", "LIMIT"], type=str.upper,
                       help="MARKET or LIMIT")
    order.add_argument("--quantity", required=True, type=float,
                       help="Quantity in base asset, e.g. 0.01")
    order.add_argument("--price", type=float, default=None,
                       help="Limit price — required when --type LIMIT")
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate and preview without sending the order.")

    return parser


def resolve_credentials(args: argparse.Namespace) -> tuple[str, str]:
    api_key    = args.api_key    or os.getenv("BINANCE_TESTNET_API_KEY", "")
    api_secret = args.api_secret or os.getenv("BINANCE_TESTNET_API_SECRET", "")

    if not api_key or not api_secret:
        print(
            "\n[ERROR] API credentials are missing.\n"
            "Option 1 — create a .env file in this folder:\n"
            "  BINANCE_TESTNET_API_KEY=your_key\n"
            "  BINANCE_TESTNET_API_SECRET=your_secret\n\n"
            "Option 2 — pass them directly:\n"
            "  python cli.py --api-key YOUR_KEY --api-secret YOUR_SECRET ...\n",
            file=sys.stderr,
        )
        sys.exit(1)

    return api_key, api_secret


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    logger.debug("CLI args: %s", vars(args))


    try:
        request = build_order_request(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
        )
    except ValidationError as exc:
        print(f"\n[VALIDATION ERROR] {exc}\n", file=sys.stderr)
        logger.error("Input validation failed: %s", exc)
        sys.exit(2)

  
    print()
    print(format_request_summary(request))

  
    if args.dry_run:
        print("\n[DRY RUN] Order not sent. Remove --dry-run to place it.\n")
        return

  
    api_key, api_secret = resolve_credentials(args)

    try:
        client = BinanceFuturesClient(api_key=api_key, api_secret=api_secret)
    except ValueError as exc:
        print(f"\n[ERROR] {exc}\n", file=sys.stderr)
        sys.exit(1)

    result = place_order(client, request)

    print()
    print(format_order_result(result))
    print()

    if result.success:
        logger.info("Done — order %s is %s", result.order_id, result.status)
    else:
        logger.error("Order failed: %s", result.error_message)
        sys.exit(3)


if __name__ == "__main__":
    main()
