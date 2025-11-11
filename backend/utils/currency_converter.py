"""Currency conversion utility for multi-region marina management"""

from typing import Dict, Optional
from datetime import datetime, timedelta
from ..logger import setup_logger


logger = setup_logger(__name__)


class CurrencyConverter:
    """Handle currency conversions for Mediterranean marinas"""

    # Exchange rates (base: EUR) - In production, these would come from an API
    # Updated daily via ECB, XE, or similar service
    EXCHANGE_RATES = {
        "EUR": 1.0,
        "USD": 1.09,
        "GBP": 0.85,
        "TRY": 32.50,
        "CHF": 0.95,
        "HRK": 7.53,  # Croatian Kuna (for historical data)
        "RSD": 117.0,  # Serbian Dinar
    }

    # Currency symbols for display
    CURRENCY_SYMBOLS = {
        "EUR": "€",
        "USD": "$",
        "GBP": "£",
        "TRY": "₺",
        "CHF": "CHF",
        "HRK": "kn",
        "RSD": "дин.",
    }

    def __init__(self):
        """Initialize currency converter"""
        self.rates = self.EXCHANGE_RATES.copy()
        self.last_update = datetime.now()
        logger.info(f"Currency converter initialized with {len(self.rates)} currencies")

    def convert(
        self,
        amount: float,
        from_currency: str,
        to_currency: str
    ) -> float:
        """
        Convert amount from one currency to another

        Args:
            amount: Amount to convert
            from_currency: Source currency code (e.g., "EUR")
            to_currency: Target currency code (e.g., "USD")

        Returns:
            Converted amount

        Raises:
            ValueError: If currency code is not supported
        """
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        if from_currency not in self.rates:
            raise ValueError(f"Unsupported source currency: {from_currency}")

        if to_currency not in self.rates:
            raise ValueError(f"Unsupported target currency: {to_currency}")

        if from_currency == to_currency:
            return amount

        # Convert to EUR first (base currency), then to target
        amount_in_eur = amount / self.rates[from_currency]
        converted_amount = amount_in_eur * self.rates[to_currency]

        logger.debug(
            f"Converted {amount} {from_currency} to "
            f"{converted_amount:.2f} {to_currency}"
        )

        return round(converted_amount, 2)

    def format_amount(self, amount: float, currency: str) -> str:
        """
        Format amount with currency symbol

        Args:
            amount: Amount to format
            currency: Currency code

        Returns:
            Formatted string (e.g., "€150.00" or "$163.50")
        """
        currency = currency.upper()
        symbol = self.CURRENCY_SYMBOLS.get(currency, currency)

        # For currencies like EUR, USD, GBP - symbol comes first
        if currency in ["EUR", "USD", "GBP", "CHF"]:
            return f"{symbol}{amount:,.2f}"
        # For currencies like TRY - symbol comes after
        else:
            return f"{amount:,.2f} {symbol}"

    def get_rate(self, from_currency: str, to_currency: str) -> float:
        """
        Get exchange rate between two currencies

        Args:
            from_currency: Source currency code
            to_currency: Target currency code

        Returns:
            Exchange rate
        """
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        if from_currency == to_currency:
            return 1.0

        rate = (self.rates[to_currency] / self.rates[from_currency])
        return round(rate, 4)

    def get_all_rates(self, base_currency: str = "EUR") -> Dict[str, float]:
        """
        Get all exchange rates relative to a base currency

        Args:
            base_currency: Base currency code

        Returns:
            Dictionary of currency codes to exchange rates
        """
        base_currency = base_currency.upper()
        if base_currency not in self.rates:
            raise ValueError(f"Unsupported base currency: {base_currency}")

        rates = {}
        for currency in self.rates:
            rates[currency] = self.get_rate(base_currency, currency)

        return rates

    def update_rates(self, new_rates: Dict[str, float]) -> None:
        """
        Update exchange rates (in production, this would be called by a scheduled task)

        Args:
            new_rates: Dictionary of currency codes to rates (base: EUR)
        """
        self.rates.update(new_rates)
        self.last_update = datetime.now()
        logger.info(f"Exchange rates updated at {self.last_update.isoformat()}")

    def get_supported_currencies(self) -> list[str]:
        """Get list of supported currency codes"""
        return list(self.rates.keys())

    def is_supported(self, currency: str) -> bool:
        """Check if a currency is supported"""
        return currency.upper() in self.rates


# Singleton instance
_converter_instance: Optional[CurrencyConverter] = None


def get_currency_converter() -> CurrencyConverter:
    """Get or create global currency converter instance"""
    global _converter_instance
    if _converter_instance is None:
        _converter_instance = CurrencyConverter()
    return _converter_instance


# Convenience functions
def convert_currency(amount: float, from_currency: str, to_currency: str) -> float:
    """Convert currency amount (convenience function)"""
    converter = get_currency_converter()
    return converter.convert(amount, from_currency, to_currency)


def format_currency(amount: float, currency: str) -> str:
    """Format currency amount (convenience function)"""
    converter = get_currency_converter()
    return converter.format_amount(amount, currency)
