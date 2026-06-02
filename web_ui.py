import os
import sys
from flask import Flask, jsonify, request, render_template

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from bot.client import get_binance_client, BinanceClientError
from bot.orders import execute_order, OrderExecutionError
from bot.validators import validate_all, ValidationError
from bot.logging_config import LOG_FILE_PATH, logger

app = Flask(__name__)
app.template_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/connection', methods=['GET'])
def check_connection():
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    
    if not api_key or not api_secret:
        return jsonify({
            "status": "disconnected",
            "reason": "API credentials missing in .env configuration."
        })
        
    try:
        get_binance_client()
        return jsonify({
            "status": "connected"
        })
    except BinanceClientError as e:
        return jsonify({
            "status": "disconnected",
            "reason": str(e)
        })
    except Exception as e:
        return jsonify({
            "status": "disconnected",
            "reason": f"Unexpected connection error: {str(e)}"
        })

@app.route('/api/order', methods=['POST'])
def place_order():
    data = request.get_json() or {}
    
    symbol = data.get("symbol")
    side = data.get("side")
    order_type = data.get("order_type")
    quantity = data.get("quantity")
    price = data.get("price")
    stop_price = data.get("stop_price")

    logger.info(f"Web UI Request: {data}")

    try:
        validated = validate_all(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price
        )
        
        client = get_binance_client()
        response = execute_order(
            client=client,
            symbol=validated["symbol"],
            side=validated["side"],
            order_type=validated["order_type"],
            quantity=validated["quantity"],
            price=validated["price"],
            stop_price=validated["stop_price"]
        )
        
        return jsonify({
            "success": True,
            "response": response
        })
        
    except ValidationError as e:
        logger.error(f"Web UI Validation Error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except BinanceClientError as e:
        logger.error(f"Web UI Client connection failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 502
    except OrderExecutionError as e:
        logger.error(f"Web UI Order execution failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        logger.critical(f"Web UI Critical error: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": f"Internal Server Error: {str(e)}"
        }), 500

@app.route('/api/logs', methods=['GET'])
def get_logs():
    lines_to_return = 50
    if not os.path.exists(LOG_FILE_PATH):
        return jsonify({
            "logs": ["No logs yet. Place an order to see log logs here."]
        })
        
    try:
        with open(LOG_FILE_PATH, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            tail_lines = [line.strip() for line in lines[-lines_to_return:]]
            return jsonify({
                "logs": tail_lines
            })
    except Exception as e:
        return jsonify({
            "logs": [f"Error reading logs: {str(e)}"]
        }), 500

if __name__ == '__main__':
    print("*" * 60)
    print("Starting Binance Futures Testnet Trading Bot Web UI...")
    print("Navigate to http://127.0.0.1:5001 in your browser.")
    print("*" * 60)
    app.run(host='127.0.0.1', port=5001, debug=True)
