"""Small, deliberately transparent pricing rules."""

from __future__ import annotations


def calculate_total(price_cents: int, quantity: int, discount_code: str | None = None) -> int:
    """Calculate an order total in cents.

    Parameters
    ----------
    price_cents : int
        Unit price in cents.
    quantity : int
        Number of units to charge.
    discount_code : str | None, optional
        Optional code for a ten percent discount.

    Raises
    ------
    ValueError
        If the price or quantity is negative, or if the quantity is zero.

    """
    if price_cents < 0:
        raise ValueError("price cannot be negative")
    if quantity <= 0:
        raise ValueError("quantity must be positive")

    subtotal = price_cents * quantity
    discount = _read_discount(discount_code or "")
    return subtotal - (subtotal * discount // 100)


def _read_discount(code: str) -> int:
    """Return the discount percentage for a known code.

    Parameters
    ----------
    code : str
        Discount code to inspect.

    Returns
    -------
    int
        Discount percentage, or zero when the code is unknown.

    """
    return 10 if code == "WELCOME10" else 0
