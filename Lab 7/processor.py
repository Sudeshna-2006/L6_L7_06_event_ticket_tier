
def decode_promo_voucher(voucher_code):
    try:
        if not isinstance(voucher_code, str):
            return "Invalid voucher code"

        code = voucher_code.strip()

        if code.count('-') != 1:
            return "Invalid voucher code"

        prefix, pct_str = code.split('-')

        if not prefix.strip() or not pct_str.isdigit():
            return "Invalid voucher code"

        percentage = int(pct_str)

        if percentage < 1 or percentage > 100:
            return "Invalid voucher code"

        return f"Valid {prefix.upper()}: {percentage}% OFF"

    except (ValueError, TypeError, AttributeError):
        return "Invalid voucher code"


def calculate_seat_tier_price(tier_spec):
    try:
        if not isinstance(tier_spec, str):
            return None

        parts = tier_spec.split('@')

        if len(parts) != 2:
            return None

        tier = parts[0].strip().upper()
        row_str = parts[1].strip()

        tier_rates = {
            "VIP": 150.0,
            "PREMIUM": 90.0,
            "GENERAL": 45.0
        }

        if tier not in tier_rates or not row_str.isdigit():
            return None

        row = int(row_str)

        return tier_rates[tier] + (row * 2.0)

    except (ValueError, TypeError, AttributeError):
        return None


def parse_attendee_badge(badge_csv):
    try:
        if not isinstance(badge_csv, str):
            return "Invalid attendee badge"

        tokens = badge_csv.split(',')

        if len(tokens) != 3:
            return "Invalid attendee badge"

        name = tokens[0].strip()
        age_str = tokens[1].strip()
        seat = tokens[2].strip()

        if not name or not seat or not age_str.isdigit():
            return "Invalid attendee badge"

        age = int(age_str)

        category = "Child" if age < 18 else "Adult"

        return f"{name} [{category}] - Seat {seat}"

    except (ValueError, TypeError, AttributeError):
        return "Invalid attendee badge"


def main():
    print("==== Running decode_promo_voucher ====")
    v_input = input("Enter voucher (e.g. EARLY-20): ")
    print("Voucher:", decode_promo_voucher(v_input))

    print("\n==== Running calculate_seat_tier_price ====")
    t_input = input("Enter tier spec (e.g. VIP@4): ")
    print("Seat Price: $", calculate_seat_tier_price(t_input))

    print("\n==== Running parse_attendee_badge ====")
    b_input = input("Enter badge CSV (Name,Age,Seat): ")
    print("Badge:", parse_attendee_badge(b_input))


if __name__ == "__main__":
    main()
