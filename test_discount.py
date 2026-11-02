"""Basis-path tests for calculate_final_price. V(G)=5 -> 5 tests."""
import pytest
from discount import calculate_final_price


# P1: D1=T                         -> error
def test_p1_invalid_total():
    with pytest.raises(ValueError):
        calculate_final_price(0, False)

# P2 (baseline): D1=F, D2=T, D4=F  -> 10%
def test_p2_big_total_non_member():
    assert calculate_final_price(500_000, False) == 450_000

# P3: D1=F, D2=T, D4=T             -> 10% + 5%
def test_p3_big_total_member():
    assert calculate_final_price(500_000, True) == 425_000

# P4: D1=F, D2=F, D3=T, D4=F       -> 5%
def test_p4_mid_total_non_member():
    assert calculate_final_price(200_000, False) == 190_000

# P5: D1=F, D2=F, D3=F, D4=F       -> no discount
def test_p5_small_total_non_member():
    assert calculate_final_price(100_000, False) == 100_000


# Extra: boundary values and the member + small total combo
@pytest.mark.parametrize("total,member,expected", [
    (1, False, 1),
    (199_999, False, 199_999),
    (499_999, False, 474_999),   # 5% of 499,999 -> rounded
    (100_000, True, 95_000),
    (-5, True, None),
])
def test_boundaries(total, member, expected):
    if expected is None:
        with pytest.raises(ValueError):
            calculate_final_price(total, member)
    else:
        assert calculate_final_price(total, member) == expected
