# Trading Bot — Binance Futures Testnet (USDT-M)

A clean, structured Python CLI application that places **Market** and **Limit** orders on the Binance Futures Testnet.

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py          # package exports
│   ├── client.py            # Binance REST API wrapper (auth, signing, HTTP)
│   ├── orders.py            # order placement logic + result formatting
│   ├── validators.py        # all input validation rules
│   └── logging_config.py   # file + console logging setup
├── cli.py                   # CLI entry point (argparse)
├── .env.example             # copy to .env and add your keys
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Get Testnet credentials

1. Go to <https://testnet.binancefuture.com>
2. Register / log in
3. Navigate to **API Management** → **Generate Key**
4. Copy your **API Key** and **API Secret**

### 2. Clone / unzip the project

```bash
cd trading_bot
```

### 3. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate   
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure credentials

```bash
cp .env.example .env

```

---

## How to Run

### Basic syntax

```bash
python cli.py --symbol <SYMBOL> --side <BUY|SELL> --type <MARKET|LIMIT> --quantity <QTY> [--price <PRICE>]
```

### Examples

#### Market BUY 0.01 BTC
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

#### Limit SELL 0.01 BTC at $60,000
```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 60000
```

#### Market BUY 0.1 ETH
```bash
python cli.py --symbol ETHUSDT --side BUY --type MARKET --quantity 0.1
```

#### Dry-run (validate only, do NOT send order)
```bash
python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.01 --price 50000 --dry-run
```

#### Pass credentials inline (overrides .env)
```bash
python cli.py --api-key YOUR_KEY --api-secret YOUR_SECRET \
              --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

---

## Sample Output

```
┌─── Order Request ────────────────────────────
│  Symbol     : BTCUSDT
│  Side       : BUY
│  Type       : MARKET
│  Quantity   : 0.01
└──────────────────────────────────────────────

┌─── Order SUCCESS ────────────────────────────
│  Order ID     : 3379040
│  Status       : FILLED
│  Executed Qty : 0.01
│  Avg Price    : 43250.5
└──────────────────────────────────────────────
```

---

## Logging

All API requests, responses, and errors are written to **`trading_bot.log`** (DEBUG level) in the project root.  
The console shows INFO-level messages only.

---

## Assumptions

- All orders are placed on the **USDT-M** perpetual futures market.
- Testnet base URL: `https://testnet.binancefuture.com`
- LIMIT orders use `timeInForce=GTC` (Good Till Cancelled) by default.
- The `python-dotenv` package is optional — credentials can also be passed as CLI flags.

---

## Bonus Features Implemented

- `--dry-run` flag for safe pre-flight validation
- Full DEBUG-level logging to `trading_bot.log`
- Clean separation: client layer / order logic layer / CLI layer
- Typed dataclasses (`OrderRequest`, `OrderResult`) for structured data flow
