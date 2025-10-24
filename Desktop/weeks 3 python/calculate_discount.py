def calculate_discount(price, discount_percent):
    """
    Calculate the final price after applying a discount.
    Only applies the discount if it's 20% or higher.
    
    :param price: Original price (float or int)
    :param discount_percent: Discount percentage (float or int)
    :return: Final price after discount (float)
    """
    if discount_percent >= 20:
        discount_amount = (discount_percent / 100) * price
        final_price = price - discount_amount
        return final_price
    else:
        return price


# Example usage:
print(calculate_discount(1000, 25))  # Output: 750.0
print(calculate_discount(1000, 10))  # Output: 1000


# Prompt user for input
try:
    price = float(input("Enter the original price of the item: "))
    discount_percent = float(input("Enter the discount percentage: "))

    final_price = calculate_discount(price, discount_percent)

    if discount_percent >= 20:
        print(f"Final price after {discount_percent}% discount: {final_price:.2f}")
    else:
        print(f"No discount applied. Original price: {final_price:.2f}")
except ValueError:
    print("Please enter valid numbers for price and discount.")