import os
from binance.client import Client
from dotenv import load_dotenv
from bot.logging_config import logger

load_dotenv()

class BinanceClientError(Exception):
    pass

def get_binance_client() -> Client:
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    logger.debug("Initializing Binance Client (Testnet)...")
    
    if not api_key or not api_secret:
        error_msg = (
            "Binance API credentials missing. Please configure BINANCE_API_KEY and "
            "BINANCE_API_SECRET in your .env file."
        )
        logger.error(error_msg)
        raise BinanceClientError(error_msg)
    
    # Safely mask key for logs
    masked_key = f"{api_key[:6]}...{api_key[-4:]}" if len(api_key) > 10 else "Invalid Key"
    logger.info(f"Using API Key: {masked_key}")
    
    try:
        client = Client(api_key=api_key, api_secret=api_secret, testnet=True)
        
        # Test connection
        client.futures_ping()
        logger.info("Connected to Binance Futures Testnet API successfully.")
        return client
    except Exception as e:
        error_msg = f"Failed to connect to Testnet API: {e}"
        logger.error(error_msg, exc_info=True)
        raise BinanceClientError(error_msg)
