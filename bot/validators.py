import re

class ValidationError(ValueError):
    pass

def validate_symbol(symbol: str) -> str:
    if not symbol or not isinstance(symbol, str):
        raise ValidationError("Symbol must be a non-empty string.")
    
    symbol_clean = symbol.strip().upper()
    if not re.match(r'^[A-Z0-9]{3,15}$', symbol_clean):
        raise ValidationError(f"Invalid symbol format: '{symbol}'. Expected alphanumeric symbol (e.g. BTCUSDT).")
    
    return symbol_clean

def validate_side(side: str) -> str:
    if not side or not isinstance(side, str):
        raise ValidationError("Side must be a non-empty string.")
    
    side_clean = side.strip().upper()
    if side_clean not in ('BUY', 'SELL'):
        raise ValidationError(f"Invalid side: '{side}'. Must be either 'BUY' or 'SELL'.")
    
    return side_clean

def validate_order_type(order_type: str) -> str:
    if not order_type or not isinstance(order_type, str):
        raise ValidationError("Order type must be a non-empty string.")
    
    type_clean = order_type.strip().upper()
    if type_clean not in ('MARKET', 'LIMIT', 'STOP_LIMIT'):
        raise ValidationError(f"Invalid order type: '{order_type}'. Supported: MARKET, LIMIT, STOP_LIMIT.")
    
    return type_clean

def validate_quantity(quantity: str | float) -> float:
    try:
        qty_float = float(quantity)
    except (ValueError, TypeError):
        raise ValidationError(f"Quantity '{quantity}' must be a valid number.")
    
    if qty_float <= 0:
        raise ValidationError(f"Quantity {qty_float} must be greater than zero.")
    
    return qty_float

def validate_price(price: str | float, order_type: str) -> float | None:
    order_type_upper = order_type.strip().upper()
    if order_type_upper in ('LIMIT', 'STOP_LIMIT'):
        if price is None or str(price).strip() == "":
            raise ValidationError(f"Price is required for {order_type_upper} orders.")
        try:
            price_float = float(price)
        except (ValueError, TypeError):
            raise ValidationError(f"Price '{price}' must be a valid number.")
        
        if price_float <= 0:
            raise ValidationError(f"Price {price_float} must be greater than zero.")
        return price_float
    
    return None

def validate_stop_price(stop_price: str | float, order_type: str) -> float | None:
    order_type_upper = order_type.strip().upper()
    if order_type_upper == 'STOP_LIMIT':
        if stop_price is None or str(stop_price).strip() == "":
            raise ValidationError("Stop price is required for STOP_LIMIT orders.")
        try:
            stop_price_float = float(stop_price)
        except (ValueError, TypeError):
            raise ValidationError(f"Stop price '{stop_price}' must be a valid number.")
        
        if stop_price_float <= 0:
            raise ValidationError(f"Stop price {stop_price_float} must be greater than zero.")
        return stop_price_float
    
    return None

def validate_all(symbol: str, side: str, order_type: str, quantity: str | float, price: str | float = None, stop_price: str | float = None) -> dict:
    sanitized = {}
    sanitized['symbol'] = validate_symbol(symbol)
    sanitized['side'] = validate_side(side)
    sanitized['order_type'] = validate_order_type(order_type)
    sanitized['quantity'] = validate_quantity(quantity)
    sanitized['price'] = validate_price(price, sanitized['order_type'])
    sanitized['stop_price'] = validate_stop_price(stop_price, sanitized['order_type'])
    return sanitized
