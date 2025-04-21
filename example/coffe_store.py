import sys
import os
from collections import Counter
from secrets import randbits

from persistify.persistify import save_s, load_s


class Store:
    class Product:
        def __init__(self, name: str, price: float) -> None:
            self.name = name
            self.price = price

        def __str__(self) -> str:
            return f"{self.name}"

        @property
        def cost(self) -> float:
            return self.price

        @cost.setter
        def cost(self, new_cost) -> None:
            self.price = new_cost

    def __init__(self) -> None:
        self.products = []

    def __str__(self) -> str:
        if len(self.products) > 0:
            return f"Store have: {''.join([str(product) for product in self.products])}"
        else:
            return "There is nothing in the store yet."

    def add_product(self, product: "Product"):
        self.products.append(product)


database = os.path.join(os.path.dirname(__file__), "coffe_store.pydat")
key = randbits(2**8)


def main():
    best_coffe = Store()

    latte = Store.Product("Latte", 1.23)
    latte_count = 3
    americano = Store.Product("Americano", 1.0)
    americano_count = 1

    for _ in range(latte_count):
        best_coffe.add_product(latte)

    for _ in range(americano_count):
        best_coffe.add_product(americano)

    print("Saving my store data to database.")

    with open(database, "w") as f:
        save_s(f, best_coffe, key)

    while True:
        command = input("What do you want today: ").strip().lower()

        if command == "coffe":
            with open(database) as f:
                store_data = load_s(f, key, (Store, Store.Product))

            print("Now in stock:")
            count = Counter(store_data.products)

            for i, (product, count) in enumerate(count.most_common()):
                print(
                    f"{i + 1}. {str(product).capitalize()} {count}x - {product.cost}."
                )

        if command in ("nothing", "break", "exit", "stop", "bye"):
            break

    print("Goodbye!")


if __name__ == "__main__":
    main()
