import sys
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
import questionary

from bot.client import get_binance_client, BinanceClientError
from bot.orders import execute_order, OrderExecutionError
from bot.validators import validate_all, ValidationError
from bot.logging_config import logger

console = Console()

def display_welcome():
    welcome_text = Text()
    welcome_text.append("⚡ Binance Futures Testnet Trading Bot ⚡\n", style="bold yellow")
    welcome_text.append("USDT-M Futures trading client.", style="italic cyan")
    console.print(Panel(welcome_text, border_style="blue", expand=False))

def run_interactive() -> dict:
    display_welcome()
    
    symbol = questionary.text(
        "Enter Symbol (e.g. BTCUSDT):",
        default="BTCUSDT",
        validate=lambda val: True if len(val.strip()) > 0 else "Symbol cannot be empty."
    ).ask()
    
    if symbol is None:
        raise KeyboardInterrupt()

    side = questionary.select(
        "Select Side:",
        choices=["BUY", "SELL"]
    ).ask()
    
    if side is None:
        raise KeyboardInterrupt()

    order_type = questionary.select(
        "Select Order Type:",
        choices=["MARKET", "LIMIT", "STOP_LIMIT"]
    ).ask()
    
    if order_type is None:
        raise KeyboardInterrupt()

    quantity = questionary.text(
        "Enter Quantity (e.g. 0.001):",
        validate=lambda val: True if re_match_float(val) else "Must be a valid positive number."
    ).ask()
    
    if quantity is None:
        raise KeyboardInterrupt()

    price = None
    stop_price = None

    if order_type in ("LIMIT", "STOP_LIMIT"):
        price = questionary.text(
            f"Enter Limit Price (for {order_type}):",
            validate=lambda val: True if re_match_float(val) else "Must be a valid positive number."
        ).ask()
        if price is None:
            raise KeyboardInterrupt()

    if order_type == "STOP_LIMIT":
        stop_price = questionary.text(
            "Enter Stop (Trigger) Price:",
            validate=lambda val: True if re_match_float(val) else "Must be a valid positive number."
        ).ask()
        if stop_price is None:
            raise KeyboardInterrupt()

    return {
        "symbol": symbol,
        "side": side,
        "order_type": order_type,
        "quantity": quantity,
        "price": price,
        "stop_price": stop_price
    }

def re_match_float(val: str) -> bool:
    try:
        f = float(val)
        return f > 0
    except ValueError:
        return False

def print_order_request_summary(inputs: dict):
    table = Table(title="Order Request Summary", title_style="bold magenta", border_style="magenta")
    table.add_column("Parameter", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Symbol", inputs["symbol"])
    table.add_row("Side", inputs["side"])
    table.add_row("Order Type", inputs["order_type"])
    table.add_row("Quantity", str(inputs["quantity"]))
    
    if inputs.get("price") is not None:
        table.add_row("Limit Price", str(inputs["price"]))
    if inputs.get("stop_price") is not None:
        table.add_row("Stop (Trigger) Price", str(inputs["stop_price"]))

    console.print(table)

def print_order_response_details(response: dict):
    table = Table(title="Binance API Response Details", title_style="bold green", border_style="green")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Order ID", str(response.get("orderId", "N/A")))
    table.add_row("Client Order ID", str(response.get("clientOrderId", "N/A")))
    table.add_row("Status", str(response.get("status", "N/A")))
    table.add_row("Executed Qty", str(response.get("executedQty", "N/A")))
    
    avg_price = response.get("avgPrice")
    if not avg_price or float(avg_price) == 0.0:
        avg_price = response.get("price", "N/A")
    table.add_row("Avg/Limit Price", str(avg_price))
    table.add_row("Time In Force", str(response.get("timeInForce", "N/A")))

    console.print(table)

def main():
    parser = argparse.ArgumentParser(
        description="Binance Futures Testnet (USDT-M) trading bot client CLI."
    )
    parser.add_argument("--symbol", type=str, help="Trading symbol (e.g. BTCUSDT)")
    parser.add_argument("--side", type=str, choices=["BUY", "SELL"], help="BUY or SELL")
    parser.add_argument("--type", type=str, choices=["MARKET", "LIMIT", "STOP_LIMIT"], help="Order Type")
    parser.add_argument("--quantity", type=str, help="Order Quantity")
    parser.add_argument("--price", type=str, help="Limit Price (required for LIMIT / STOP_LIMIT)")
    parser.add_argument("--stop-price", type=str, help="Stop/Trigger Price (required for STOP_LIMIT)")
    parser.add_argument("-i", "--interactive", action="store_true", help="Force interactive CLI mode")

    args = parser.parse_args()

    # Default to interactive if no args provided
    is_interactive = args.interactive or (
        len(sys.argv) == 1 or 
        (len(sys.argv) == 2 and args.interactive)
    )

    try:
        if is_interactive:
            raw_inputs = run_interactive()
        else:
            raw_inputs = {
                "symbol": args.symbol,
                "side": args.side,
                "order_type": args.type,
                "quantity": args.quantity,
                "price": args.price,
                "stop_price": args.stop_price
            }
            if not raw_inputs["symbol"] or not raw_inputs["side"] or not raw_inputs["order_type"] or not raw_inputs["quantity"]:
                parser.print_help()
                console.print("\n[bold red]Error:[/bold red] Missing required arguments. Provide --symbol, --side, --type, and --quantity, or run interactively.")
                sys.exit(1)

        logger.info(f"CLI Input Received: {raw_inputs}")

        validated = validate_all(
            symbol=raw_inputs["symbol"],
            side=raw_inputs["side"],
            order_type=raw_inputs["order_type"],
            quantity=raw_inputs["quantity"],
            price=raw_inputs["price"],
            stop_price=raw_inputs["stop_price"]
        )
        
        print_order_request_summary(validated)

        console.print("[yellow]Connecting to Binance Futures Testnet...[/yellow]")
        client = get_binance_client()

        console.print("[yellow]Placing order...[/yellow]")
        response = execute_order(
            client=client,
            symbol=validated["symbol"],
            side=validated["side"],
            order_type=validated["order_type"],
            quantity=validated["quantity"],
            price=validated["price"],
            stop_price=validated["stop_price"]
        )

        success_panel = Panel(
            "[bold green]SUCCESS: Order executed successfully on Binance Futures Testnet sandbox![/bold green]",
            border_style="green"
        )
        console.print(success_panel)
        
        print_order_response_details(response)
        console.print(f"[dim]Detailed API logs saved to 'trading_bot.log'[/dim]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled. Exiting.[/yellow]")
        sys.exit(0)
    except ValidationError as e:
        logger.error(f"Validation Error: {e}")
        console.print(Panel(f"[bold red]Validation Error:[/bold red] {e}", border_style="red"))
        sys.exit(1)
    except BinanceClientError as e:
        console.print(Panel(f"[bold red]Connection Error:[/bold red] {e}", border_style="red"))
        sys.exit(1)
    except OrderExecutionError as e:
        console.print(Panel(f"[bold red]Order Execution Failed:[/bold red] {e}", border_style="red"))
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Unhandled exception: {e}", exc_info=True)
        console.print(Panel(f"[bold red]Critical Error:[/bold red] {e}", border_style="red"))
        sys.exit(1)

if __name__ == "__main__":
    main()
