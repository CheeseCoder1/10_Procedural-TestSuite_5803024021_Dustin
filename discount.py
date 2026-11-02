"""Procedural module: discount calculation."""


def calculate_final_price(total, is_member):
    """Return the final price after discount.

    Rules:
      - total must be > 0, otherwise ValueError
      - total >= 500_000  -> 10% discount
      - total >= 200_000  -> 5% discount
      - members get an extra 5% discount
    """
    if total <= 0:                      # D1
        raise ValueError("total must be positive")

    rate = 0.0
    if total >= 500_000:                # D2
        rate = 0.10
    elif total >= 200_000:              # D3
        rate = 0.05

    if is_member:                       # D4
        rate += 0.05

    return round(total * (1 - rate))
