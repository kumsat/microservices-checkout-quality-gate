from pytest_bdd import scenarios, given, when, then, parsers

from tests.api_clients.inventory_api import InventoryAPI
from tests.api_clients.order_api import OrderAPI
from tests.api_clients.product_api import ProductAPI
from tests.api_clients.cart_api import CartAPI
from tests.api_clients.payment_api import PaymentAPI

# We use a constant test user ID for all steps
USER_ID = "user-123"

# Link this step file to the feature file
scenarios("../features/checkout.feature")


@given(parsers.parse('the product "{product_id}" has stock {stock:d} in the inventory system'))
def set_initial_stock(product_id, stock):
    """
    GIVEN step:
    Ensure that the product has a known stock before the test.
    """
    InventoryAPI().set_stock(product_id, stock)


@when(parsers.parse('the user buys {quantity:d} units of "{product_id}"'))
def perform_checkout(product_id, quantity):
    """
    WHEN step:
    Simulate the checkout flow across multiple microservices:
    - Read product price
    - Add item to cart
    - Reserve inventory
    - Charge payment
    - Create order
    """
    product_api = ProductAPI()
    cart_api = CartAPI()
    inv_api = InventoryAPI()
    pay_api = PaymentAPI()
    order_api = OrderAPI()

    # 1) Get product info (including price)
    product = product_api.get_product(product_id)

    # 2) Add to cart
    cart_api.add_item(USER_ID, product_id, quantity)

    # 3) Reserve inventory
    reserve_resp = inv_api.reserve(product_id, quantity)
    assert reserve_resp.status_code == 200, "Inventory reservation failed"

    # 4) Compute total price
    total_price = product["price"] * quantity

    # 5) Charge payment (4242... is a 'success' card)
    payment_resp = pay_api.charge(card_number="4242-4242-4242-4242", amount=total_price)
    assert payment_resp["status"] == "SUCCESS", "Payment failed"

    # 6) Create order
    order_api.create_order(USER_ID, {product_id: quantity}, total_price)


@then(parsers.parse('an order should be created with {quantity:d} units of "{product_id}"'))
def verify_order_created(product_id, quantity):
    """
    THEN step:
    Verify the latest order for this user contains the correct quantity.
    """
    resp = OrderAPI().get_latest_order(USER_ID)
    assert resp.status_code == 200, "No order found for user"
    order = resp.json()
    assert order["items"][product_id] == quantity, "Order quantity mismatch"


@then(parsers.parse('the inventory for "{product_id}" should now be {expected_stock:d}'))
def verify_inventory(product_id, expected_stock):
    """
    AND step:
    Verify that the inventory was reduced correctly after checkout.
    """
    current_stock = InventoryAPI().get_stock(product_id)
    assert current_stock == expected_stock, f"Expected stock {expected_stock}, got {current_stock}"

