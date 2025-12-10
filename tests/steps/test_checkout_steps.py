from pytest_bdd import scenarios, given, when, then, parsers

from tests.api_clients.inventory_api import InventoryAPI
from tests.api_clients.order_api import OrderAPI
from tests.api_clients.product_api import ProductAPI
from tests.api_clients.cart_api import CartAPI
from tests.api_clients.payment_api import PaymentAPI

# Different users per scenario to avoid order history conflicts
SUCCESS_USER_ID = "user-success"
PAYMENT_FAIL_USER_ID = "user-payment-fail"
INSUFFICIENT_STOCK_USER_ID = "user-insufficient-stock"

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
def perform_successful_checkout(product_id, quantity):
    """
    WHEN (happy path):
    Simulate a successful checkout flow:
    - Get product info
    - Add to cart
    - Reserve inventory
    - Charge payment (success card)
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
    cart_api.add_item(SUCCESS_USER_ID, product_id, quantity)

    # 3) Reserve inventory
    reserve_resp = inv_api.reserve(product_id, quantity)
    assert reserve_resp.status_code == 200, "Inventory reservation failed in happy path"

    # 4) Compute total price
    total_price = product["price"] * quantity

    # 5) Charge payment (4242... is a 'success' card)
    pay_resp, pay_data = pay_api.charge(
        card_number="4242-4242-4242-4242",
        amount=total_price,
    )
    assert pay_resp.status_code == 200, "Payment HTTP status not OK in happy path"
    assert pay_data.get("status") == "SUCCESS", "Payment failed unexpectedly"

    # 6) Create order
    order_api.create_order(SUCCESS_USER_ID, {product_id: quantity}, total_price)


@when(parsers.parse('the user tries to buy {quantity:d} units of "{product_id}" with a failing payment method'))
def checkout_with_failing_payment(product_id, quantity):
    """
    WHEN (payment failure):
    - Reserve inventory successfully
    - Attempt payment with a failing card (starts with 4000)
    - On failure, release inventory
    - Do NOT create an order
    """
    product_api = ProductAPI()
    cart_api = CartAPI()
    inv_api = InventoryAPI()
    pay_api = PaymentAPI()

    # 1) Get product info
    product = product_api.get_product(product_id)

    # 2) Add to cart
    cart_api.add_item(PAYMENT_FAIL_USER_ID, product_id, quantity)

    # 3) Reserve inventory
    reserve_resp = inv_api.reserve(product_id, quantity)
    assert reserve_resp.status_code == 200, "Inventory reservation should succeed before payment fail"

    # 4) Attempt payment with failing card (4000...)
    total_price = product["price"] * quantity
    pay_resp, pay_data = pay_api.charge(
        card_number="4000-0000-0000-0000",
        amount=total_price,
    )

    # Payment must fail
    assert pay_resp.status_code != 200, "Payment should have failed but returned 200"
    assert pay_data.get("status") == "FAILED", "Payment status should be FAILED"

    # 5) Release inventory because payment failed
    from tests.api_clients.inventory_api import InventoryAPI as InvAPI
    InvAPI().release(product_id, quantity=quantity)


@when(parsers.parse('the user tries to buy {quantity:d} units of "{product_id}"'))
def checkout_with_insufficient_stock(product_id, quantity):
    """
    WHEN (insufficient stock):
    - Try to reserve more than available
    - Expect reservation to fail (HTTP 400, INSUFFICIENT_STOCK)
    - No payment, no order
    """
    inv_api = InventoryAPI()

    # Try to reserve more quantity than we have
    reserve_resp = inv_api.reserve(product_id, quantity)
    # We expect insufficient stock (400)
    assert reserve_resp.status_code == 400, "Reservation should fail due to insufficient stock"
    data = reserve_resp.json()
    assert data.get("status") == "INSUFFICIENT_STOCK", "Expected INSUFFICIENT_STOCK status"


@then(parsers.parse('an order should be created with {quantity:d} units of "{product_id}"'))
def verify_order_created(product_id, quantity):
    """
    THEN (happy path):
    Verify the latest order for the success user contains the correct quantity.
    """
    resp = OrderAPI().get_latest_order(SUCCESS_USER_ID)
    assert resp.status_code == 200, "No order found for success user"
    order = resp.json()
    assert order["items"][product_id] == quantity, "Order quantity mismatch in happy path"


@then("no order should be created for this user")
def verify_no_order_created_for_user():
    """
    THEN step:
    For failure scenarios, ensure that no order exists for the involved user.
    Both payment-fail and insufficient-stock use their own user IDs.
    We simply check that no latest order exists (404).
    """
    order_api = OrderAPI()

    # Payment failure user
    resp_fail = order_api.get_latest_order(PAYMENT_FAIL_USER_ID)
    assert resp_fail.status_code == 404, "Order should not exist for payment-fail user"

    # Insufficient stock user
    resp_insufficient = order_api.get_latest_order(INSUFFICIENT_STOCK_USER_ID)
    # It's OK if 404 OR empty history; we check 404 here (our API returns 404 when none)
    assert resp_insufficient.status_code == 404, "Order should not exist for insufficient-stock user"


@then(parsers.parse('the inventory for "{product_id}" should now be {expected_stock:d}'))
def verify_inventory_after_success(product_id, expected_stock):
    """
    AND step (happy path):
    Verify that the inventory was reduced correctly after checkout.
    """
    current_stock = InventoryAPI().get_stock(product_id)
    assert current_stock == expected_stock, f"Expected stock {expected_stock}, got {current_stock}"


@then(parsers.parse('the inventory for "{product_id}" should remain at {expected_stock:d}'))
def verify_inventory_unchanged(product_id, expected_stock):
    """
    AND step (failure paths):
    Verify that the inventory stayed unchanged (payment failed OR insufficient stock).
    """
    current_stock = InventoryAPI().get_stock(product_id)
    assert current_stock == expected_stock, f"Expected stock to remain {expected_stock}, got {current_stock}"

