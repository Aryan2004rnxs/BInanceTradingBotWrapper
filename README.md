# Binance Trading Bot Wrapper

A Python-based Binance Futures Testnet trading bot with an API wrapper, interactive CLI, and web dashboard for placing and monitoring USDT-M futures orders.

## Features

* **Binance Futures Testnet Integration**
* **Interactive CLI** for guided order placement
* **Web Dashboard** with real-time logs and connection status
* **Input Validation** for symbols, quantities, and prices
* **Structured Logging** with automatic log rotation
* **Mock Testing** without hitting the Binance API

## Project Structure

```text
BinanceTradingBotWrapper/
├── bot/
│   ├── client.py
│   ├── validators.py
│   ├── orders.py
│   └── logging_config.py
├── templates/index.html
├── cli.py
├── web_ui.py
├── test_mock_run.py
└── requirements.txt
```

## Installation

```bash
git clone <repo-url>
cd BinanceTradingBotWrapper

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env
```

Add your Binance Testnet API credentials to `.env`.

## Usage

### Interactive CLI

```bash
python cli.py
```

### Command Line

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### Web Dashboard

```bash
python web_ui.py
```

Open: `http://127.0.0.1:5001`

## Testing

```bash
python test_mock_run.py
```

## 
