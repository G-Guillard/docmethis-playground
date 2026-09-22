"""Order creation and checkout orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from demo_shop.catalog import Catalog, OutOfStockError, ProductNotFound
from demo_shop.pricing import calculate_total
from demo_shop.receipts import write_receipt


@dataclass(frozen=True, slots=True)
class Order:
    """An accepted order ready for fulfilment.

    Attributes
    ----------
    sku : str
        SKU ordered by the customer.
    quantity : int
        Number of units ordered.
    total_cents : int
        Total amount charged in cents.

    """

    sku: str
    quantity: int
    total_cents: int
    ean: int


def check_order(order: Order, min_quantity: int) -> bool:
    if not isinstance(min_quantity, int):
        raise TypeError("min_quantity must be an int")
    return order.quantity >= min_quantity


def create_order(
    catalog: Catalog,
    sku: str,
    quantity: int,
    discount_code: str | None = None,
) -> Order:
    """Create an order after checking stock and price.

    Parameters
    ----------
    catalog : Catalog
        Catalog used to find the requested product.
    sku : str
        SKU to order.
    quantity : int
        Number of units to order.
    discount_code : str | None, optional
        Optional discount code passed to the pricing rules.

    Returns
    -------
    Order
        The validated order.

    Raises
    ------
    ProductNotFound
        If the SKU is not in the catalog.
    OutOfStockError
        If the requested quantity is not available.
    ValueError
        If the quantity is not positive.

    """
    try:
        product = catalog.find(sku)
    except ProductNotFound:
        raise
    if quantity <= 0:
        raise ValueError("quantity must be positive")
    if quantity > product.stock:
        raise OutOfStockError(f"Only {product.stock} unit(s) available")
    total_cents = calculate_total(product.price_cents, quantity, discount_code)
    return Order(sku=product.sku, quantity=quantity, total_cents=total_cents)


def place_order(
    catalog: Catalog,
    sku: str,
    quantity: int,
    receipt_path: Path,
    discount_code: str | None = None,
) -> Order:
    """Create an order and write its receipt to disk.

    Parameters
    ----------
    catalog : Catalog
        Catalog used to find the requested product.
    sku : str
        SKU to order.
    quantity : int
        Number of units to order.
    receipt_path : Path
        Destination path for the receipt.
    discount_code : str | None, optional
        Optional discount code passed to the pricing rules.

    Returns
    -------
    Order
        The order written to the receipt.

    Raises
    ------
    ProductNotFound
        If the SKU is not in the catalog.
    OutOfStockError
        If the requested quantity is not available.
    ValueError
        If the quantity is not positive.
    OSError
        If the receipt cannot be written.

    """
    try:
        order = create_order(catalog, sku, quantity, discount_code)
    except ProductNotFound:
        raise
    except OutOfStockError:
        raise
    except ValueError:
        raise
    try:
        write_receipt(order, receipt_path)
    except OSError:
        raise
    return order
