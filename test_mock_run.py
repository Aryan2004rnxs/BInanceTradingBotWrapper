import os
import sys

# Ensure the root directory is in the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Remove existing log file to start fresh BEFORE importing logger/cli
log_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "trading_bot.log"))
if os.path.exists(log_file):
    try:
        os.remove(log_file)
    except OSError:
        pass

import unittest
from unittest.mock import patch
from binance.client import Client

# Set mock credentials before importing bot modules so client initialization passes
os.environ["BINANCE_API_KEY"] = "mock_key_abc123XYZ7890123456789"
os.environ["BINANCE_API_SECRET"] = "mock_secret_abc123XYZ7890123456789"

# We bypass writing to .env here so we don't overwrite user's actual keys
from cli import main as cli_main

def mock_futures_ping(self):
    """Mock connection health check (does nothing, indicating success)."""
    return {}

def mock_futures_create_order(self, **kwargs):
    """Mock order placement returning realistic Binance API response structures."""
    symbol = kwargs.get("symbol", "BTCUSDT")
    side = kwargs.get("side", "BUY")
    order_type = kwargs.get("type", "LIMIT")
    quantity = kwargs.get("quantity", 0.0)
    price = kwargs.get("price")
    stop_price = kwargs.get("stopPrice", "0.00")

    if order_type == "MARKET":
        return {
            "orderId": 87654321,
            "symbol": symbol,
            "status": "FILLED",
            "clientOrderId": "mock_client_order_id_market",
            "price": "0.00",
            "avgPrice": "99500.00",
            "origQty": str(quantity),
            "executedQty": str(quantity),
            "cumQuote": str(99500.0 * float(quantity)),
            "timeInForce": "GTC",
            "type": "MARKET",
            "reduceOnly": False,
            "closePosition": False,
            "side": side,
            "positionSide": "BOTH",
            "stopPrice": "0.00",
            "workingType": "CONTRACT_PRICE",
            "priceProtect": False,
            "origType": "MARKET",
            "updateTime": 1780000000000
        }
    elif order_type == "LIMIT":
        return {
            "orderId": 87654322,
            "symbol": symbol,
            "status": "NEW",
            "clientOrderId": "mock_client_order_id_limit",
            "price": f"{float(price):.2f}" if price else "0.00",
            "avgPrice": "0.00",
            "origQty": str(quantity),
            "executedQty": "0",
            "cumQuote": "0",
            "timeInForce": "GTC",
            "type": "LIMIT",
            "reduceOnly": False,
            "closePosition": False,
            "side": side,
            "positionSide": "BOTH",
            "stopPrice": "0.00",
            "workingType": "CONTRACT_PRICE",
            "priceProtect": False,
            "origType": "LIMIT",
            "updateTime": 1780000000000
        }
    elif order_type == "STOP":
        return {
            "orderId": 87654323,
            "symbol": symbol,
            "status": "NEW",
            "clientOrderId": "mock_client_order_id_stop",
            "price": f"{float(price):.2f}" if price else "0.00",
            "avgPrice": "0.00",
            "origQty": str(quantity),
            "executedQty": "0",
            "cumQuote": "0",
            "timeInForce": "GTC",
            "type": "STOP",
            "reduceOnly": False,
            "closePosition": False,
            "side": side,
            "positionSide": "BOTH",
            "stopPrice": f"{float(stop_price):.2f}" if stop_price else "0.00",
            "workingType": "CONTRACT_PRICE",
            "priceProtect": False,
            "origType": "STOP",
            "updateTime": 1780000000000
        }
    else:
        raise Exception(f"Unsupported mock order type: {order_type}")

@patch.object(Client, "futures_ping", mock_futures_ping)
@patch.object(Client, "futures_create_order", mock_futures_create_order)
def run_cli_case(args_list):
    """Helper to patch command line args and run the main entry point."""
    print(f"\n{'='*60}\nRUNNING: python cli.py {' '.join(args_list)}\n{'='*60}")
    # Backup argv
    old_argv = sys.argv
    sys.argv = ["cli.py"] + args_list
    try:
        cli_main()
    except SystemExit as e:
        print(f"CLI Exited with status: {e.code}")
    finally:
        sys.argv = old_argv

@patch.object(Client, "futures_ping", mock_futures_ping)
@patch.object(Client, "futures_create_order", mock_futures_create_order)
def test_web_ui():
    from web_ui import app
    print("\n" + "="*60)
    print("RUNNING WEB UI ENDPOINT VERIFICATION TESTS")
    print("="*60)
    
    with app.test_client() as client:
        # 1. Test GET / (HTML template loading)
        res = client.get('/')
        print(f"GET / (index): Status {res.status_code}")
        assert res.status_code == 200, "Failed to load index page"
        
        # 2. Test GET /api/connection
        res = client.get('/api/connection')
        print(f"GET /api/connection: Status {res.status_code}, Response: {res.get_json()}")
        assert res.status_code == 200, "Failed to check connection"
        
        # 3. Test GET /api/logs
        res = client.get('/api/logs')
        print(f"GET /api/logs: Status {res.status_code}, Logs Count: {len(res.get_json().get('logs', []))}")
        assert res.status_code == 200, "Failed to fetch logs"
        
        # 4. Test POST /api/order (MARKET)
        payload = {
            "symbol": "BTCUSDT",
            "side": "BUY",
            "order_type": "MARKET",
            "quantity": 0.002
        }
        res = client.post('/api/order', json=payload)
        print(f"POST /api/order (MARKET): Status {res.status_code}, Response: {res.get_json()}")
        assert res.status_code == 200, "Failed to place Market order via Web UI"
        
        # 5. Test POST /api/order (LIMIT - should fail validation on missing price)
        payload = {
            "symbol": "BTCUSDT",
            "side": "BUY",
            "order_type": "LIMIT",
            "quantity": 0.002
        }
        res = client.post('/api/order', json=payload)
        print(f"POST /api/order (LIMIT - missing price): Status {res.status_code}, Response: {res.get_json()}")
        assert res.status_code == 400, "Expected status 400 for validation failure"
        
        print("\nAll Web UI API validation checks passed successfully!")

if __name__ == "__main__":
    # Case 1: MARKET Order (BUY 0.015 ETHUSDT)
    run_cli_case(["--symbol", "ETHUSDT", "--side", "BUY", "--type", "MARKET", "--quantity", "0.015"])

    # Case 2: LIMIT Order (SELL 0.005 BTCUSDT at 98500.00)
    run_cli_case(["--symbol", "BTCUSDT", "--side", "SELL", "--type", "LIMIT", "--quantity", "0.005", "--price", "98500.00"])

    # Case 3: STOP_LIMIT Order (BUY 0.01 BTCUSDT at 99000.00 with stop price 98800.00)
    run_cli_case(["--symbol", "BTCUSDT", "--side", "BUY", "--type", "STOP_LIMIT", "--quantity", "0.01", "--price", "99000.00", "--stop-price", "98800.00"])

    # Case 4: Validation Fail Case (Invalid side)
    run_cli_case(["--symbol", "BTCUSDT", "--side", "HOLD", "--type", "MARKET", "--quantity", "0.01"])

    # Web UI Verification
    test_web_ui()

    print("\n" + "="*60)
    print("MOCK TEST RUN COMPLETE. Generated 'trading_bot.log'.")
    print("="*60 + "\n")
