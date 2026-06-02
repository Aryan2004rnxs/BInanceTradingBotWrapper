from binance.client import Client
from binance.exceptions import BinanceAPIException
from bot.logging_config import logger

class OrderExecutionError(Exception):
    pass

def execute_order(
    client: Client,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: float = None,
    stop_price: float = None
) -> dict:
    
    # 'STOP_LIMIT' order type maps to 'STOP' in the Binance Futures API
    api_order_type = order_type
    if order_type == 'STOP_LIMIT':
        api_order_type = 'STOP'

    params = {
        'symbol': symbol,
        'side': side,
        'type': api_order_type,
        'quantity': quantity
    }

    if order_type == 'LIMIT':
        params['price'] = price
        params['timeInForce'] = 'GTC'
    elif order_type == 'STOP_LIMIT':
        params['price'] = price
        params['stopPrice'] = stop_price
        params['timeInForce'] = 'GTC'

    logger.info(f"Placing order: {side} {quantity} {symbol} ({order_type})")
    logger.debug(f"API request payload: {params}")

    try:
        response = client.futures_create_order(**params)
        
        logger.info(f"Successfully placed order! OrderID: {response.get('orderId')}")
        logger.debug(f"API response payload: {response}")
        
        return response

    except BinanceAPIException as e:
        error_msg = f"Binance API Error (Status Code {e.status_code}): {e.message} (Code: {e.code})"
        logger.error(error_msg, exc_info=True)
        raise OrderExecutionError(error_msg)
        
    except Exception as e:
        error_msg = f"Unexpected error during order placement: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise OrderExecutionError(error_msg)
