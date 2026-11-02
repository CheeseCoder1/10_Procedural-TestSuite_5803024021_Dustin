"""OO module: Order state machine with an ExpressOrder subclass."""
from enum import Enum


class OrderState(Enum):
    CREATED = "CREATED"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class InvalidTransitionError(Exception):
    """Raised when an event is not allowed in the current state."""


class Order:
    BASE_SHIPPING_FEE = 10_000

    def __init__(self, order_id, amount):
        if amount <= 0:
            raise ValueError("amount must be positive")
        self.order_id = order_id
        self.amount = amount
        self.state = OrderState.CREATED

    def _move(self, event, allowed_from, target):
        if self.state not in allowed_from:
            raise InvalidTransitionError(
                f"cannot {event} when order is {self.state.value}"
            )
        self.state = target

    def pay(self):
        self._move("pay", {OrderState.CREATED}, OrderState.PAID)

    def ship(self):
        self._move("ship", {OrderState.PAID}, OrderState.SHIPPED)

    def deliver(self):
        self._move("deliver", {OrderState.SHIPPED}, OrderState.DELIVERED)

    def cancel(self):
        self._move("cancel", {OrderState.CREATED, OrderState.PAID},
                   OrderState.CANCELLED)

    def shipping_fee(self):
        return self.BASE_SHIPPING_FEE

    def total(self):
        return self.amount + self.shipping_fee()


class ExpressOrder(Order):
    """Express orders cost more and cannot be cancelled once paid."""
    EXPRESS_SURCHARGE = 15_000

    def shipping_fee(self):
        return super().shipping_fee() + self.EXPRESS_SURCHARGE

    def cancel(self):
        if self.state == OrderState.PAID:
            raise InvalidTransitionError("express order cannot be cancelled after payment")
        super().cancel()
