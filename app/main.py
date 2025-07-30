from user_flow import place_order
from admin_dashboard import view_all_sales
from add_product import add_product_with_components

if __name__ == "__main__":
    print("=== Welcome to Distributed DB Simulation ===")
    print("1. Place an Order")
    print("2. Admin Dashboard - View Sales")
    print("3. Add Product with Components")
    choice = input("Enter choice: ")

    if choice == "1":
        region = input("Enter your region (boston/denver/seattle): ").lower()
        customer = input("Enter your name: ")
        product = input("Enter product name: ")
        quantity = int(input("Enter quantity: "))
        place_order(region, customer, product, quantity)

    elif choice == "2":
        view_all_sales()

    elif choice == "3":
        region = input("Enter region (boston/denver/seattle): ").lower()
        product = input("Enter new product name: ")
        comps = input("Enter required components (comma separated): ").split(",")
        comps = [c.strip() for c in comps]
        quantity = int(input("Enter quantity for this product: "))
        add_product_with_components(region, product, comps, quantity)