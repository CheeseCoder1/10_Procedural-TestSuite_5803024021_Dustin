"""State-based tests for Order and ExpressOrder."""
import itertools
import pytest
from order import Order, ExpressOrder, OrderState as S, InvalidTransitionError

EVENTS = ["pay", "ship", "deliver", "cancel"]

# (state, event) -> next state   (the transition table)
VALID = {
    (S.CREATED, "pay"): S.PAID,
    (S.CREATED, "cancel"): S.CANCELLED,
    (S.PAID, "ship"): S.SHIPPED,
    (S.PAID, "cancel"): S.CANCELLED,
    (S.SHIPPED, "deliver"): S.DELIVERED,
}

# event sequence needed to reach each state from CREATED
PATH_TO = {
    S.CREATED: [],
    S.PAID: ["pay"],
    S.SHIPPED: ["pay", "ship"],
    S.DELIVERED: ["pay", "ship", "deliver"],
    S.CANCELLED: ["cancel"],
}


def make(cls, state):
    o = cls("A1", 100_000)
    for ev in PATH_TO[state]:
        getattr(o, ev)()
    assert o.state == state
    return o


# ---------- construction ----------
def test_initial_state_created():
    assert Order("A1", 1).state == S.CREATED

def test_invalid_amount():
    with pytest.raises(ValueError):
        Order("A1", 0)


# ---------- valid transitions ----------
@pytest.mark.parametrize("key,target", VALID.items(), ids=lambda x: str(x))
def test_valid_transition(key, target):
    state, event = key
    o = make(Order, state)
    getattr(o, event)()
    assert o.state == target


# ---------- invalid transitions (every other state/event pair) ----------
INVALID = [(s, e) for s, e in itertools.product(S, EVENTS) if (s, e) not in VALID]

@pytest.mark.parametrize("state,event", INVALID, ids=lambda x: getattr(x, "value", x))
def test_invalid_transition(state, event):
    o = make(Order, state)
    with pytest.raises(InvalidTransitionError):
        getattr(o, event)()
    assert o.state == state          # state must be unchanged


def test_full_happy_path():
    o = Order("A1", 100_000)
    o.pay(); o.ship(); o.deliver()
    assert o.state == S.DELIVERED


# ---------- inheritance / polymorphism ----------
def test_express_is_an_order():
    assert isinstance(ExpressOrder("E1", 1), Order)

@pytest.mark.parametrize("cls,fee", [(Order, 10_000), (ExpressOrder, 25_000)])
def test_polymorphic_shipping_fee(cls, fee):
    o = cls("X", 100_000)
    assert o.shipping_fee() == fee
    assert o.total() == 100_000 + fee    # total() inherited, uses overridden fee

def test_express_inherits_normal_flow():
    o = ExpressOrder("E1", 100_000)
    o.pay(); o.ship(); o.deliver()
    assert o.state == S.DELIVERED

def test_express_can_cancel_before_payment():
    o = make(ExpressOrder, S.CREATED)
    o.cancel()
    assert o.state == S.CANCELLED

def test_express_cannot_cancel_after_payment():
    o = make(ExpressOrder, S.PAID)
    with pytest.raises(InvalidTransitionError):
        o.cancel()
    assert o.state == S.PAID

def test_express_cancel_still_blocked_from_shipped():
    o = make(ExpressOrder, S.SHIPPED)
    with pytest.raises(InvalidTransitionError):   # goes through super().cancel()
        o.cancel()

def test_normal_order_can_cancel_after_payment():
    o = make(Order, S.PAID)
    o.cancel()
    assert o.state == S.CANCELLED
