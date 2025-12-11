import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


@pytest.fixture(scope="session")
def browser():
    """Set up Chrome browser for Selenium."""
    options = webdriver.ChromeOptions()
    # Run headless if you want:
    # options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=options,
    )
    driver.set_window_size(1400, 900)
    yield driver
    driver.quit()


def test_successful_ui_checkout(browser):
    """Full end-to-end Selenium UI checkout test."""
    
    browser.get("http://localhost:5006/")

    # Wait for product list to load (Laptop-X item)
    WebDriverWait(browser, 10).until(
        EC.visibility_of_element_located((By.ID, "product-Laptop-X"))
    )

    # Fill checkout fields
    browser.find_element(By.ID, "product_id").clear()
    browser.find_element(By.ID, "product_id").send_keys("Laptop-X")

    browser.find_element(By.ID, "quantity").clear()
    browser.find_element(By.ID, "quantity").send_keys("1")

    browser.find_element(By.ID, "card_number").clear()
    browser.find_element(By.ID, "card_number").send_keys("4242-4242-4242-4242")  # success card

    # Click checkout
    browser.find_element(By.ID, "checkout-btn").click()

    # Wait for result page
    WebDriverWait(browser, 10).until(
        EC.visibility_of_element_located((By.ID, "message"))
    )

    message = browser.find_element(By.ID, "message").text

    assert "Order created successfully" in message

