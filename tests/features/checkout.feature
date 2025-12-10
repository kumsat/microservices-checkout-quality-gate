Feature: Checkout workflow for microservices shop
  As a customer
  I want to buy products successfully
  So that my order is created and inventory is updated

  Scenario: Successful checkout reduces inventory and creates an order
    Given the product "Laptop-X" has stock 5 in the inventory system
    When the user buys 2 units of "Laptop-X"
    Then an order should be created with 2 units of "Laptop-X"
    And the inventory for "Laptop-X" should now be 3

  Scenario: Payment failure does not create an order and keeps inventory unchanged
    Given the product "Laptop-X" has stock 5 in the inventory system
    When the user tries to buy 2 units of "Laptop-X" with a failing payment method
    Then no order should be created for this user
    And the inventory for "Laptop-X" should remain at 5

  Scenario: Checkout fails when stock is insufficient
    Given the product "Mouse-Z" has stock 1 in the inventory system
    When the user tries to buy 3 units of "Mouse-Z"
    Then no order should be created for this user
    And the inventory for "Mouse-Z" should remain at 1

