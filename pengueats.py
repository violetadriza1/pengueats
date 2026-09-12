import datetime as dt
import random
from collections import Counter, defaultdict
from dataclasses import dataclass


@dataclass
class Fish:
    name: str
    quantity: int
    price_per_unit: float
    supplier_cost: float
    freshness_days: int

    def is_fresh(self) -> bool:
        return self.freshness_days > 0

    def age_by_one_day(self) -> None:
        self.freshness_days = max(0, self.freshness_days - 1)


class Inventory:
    LOW_STOCK_THRESHOLD = 5

    def __init__(self) -> None:
        self._stock: dict[str, Fish] = {}

    def add_stock(self, fish: Fish) -> None:
        if fish.name in self._stock:
            existing = self._stock[fish.name]
            existing.quantity += fish.quantity
            existing.freshness_days = max(existing.freshness_days, fish.freshness_days)
        else:
            self._stock[fish.name] = fish

    def use_stock(self, name: str, amount: int) -> bool:
        fish = self._stock.get(name)
        if not fish or fish.quantity < amount or not fish.is_fresh():
            return False
        fish.quantity -= amount
        return True

    def discard_spoiled(self) -> list[str]:
        discarded = []
        for name, fish in list(self._stock.items()):
            fish.age_by_one_day()
            if not fish.is_fresh():
                discarded.append(name)
                del self._stock[name]
        return discarded

    def low_stock_alert(self) -> list[str]:
        return [n for n, f in self._stock.items() if f.quantity <= self.LOW_STOCK_THRESHOLD]

    def available_fish(self) -> list[str]:
        return [n for n, f in self._stock.items() if f.quantity > 0 and f.is_fresh()]

    def snapshot(self) -> dict[str, int]:
        return {name: fish.quantity for name, fish in self._stock.items()}

    def price_of(self, name: str) -> float:
        return self._stock[name].price_per_unit


@dataclass
class Customer:
    name: str
    species: str


@dataclass
class Order:
    customer: Customer
    items: dict[str, int]
    date: dt.date
    total_price: float = 0.0


class OrderManager:
    def __init__(self, inventory: Inventory, finance: "FinanceTracker") -> None:
        self.inventory = inventory
        self.finance = finance
        self.order_history: list[Order] = []

    def place_order(self, customer: Customer, items: dict[str, int], date: dt.date) -> Order | None:
        for fish_name, qty in items.items():
            if fish_name not in self.inventory.available_fish():
                return None

        total = 0.0
        for fish_name, qty in items.items():
            if not self.inventory.use_stock(fish_name, qty):
                return None
            total += self.inventory.price_of(fish_name) * qty

        order = Order(customer=customer, items=items, date=date, total_price=total)
        self.order_history.append(order)
        self.finance.record_income(total, date, description=f"Order from {customer.name}")
        return order


@dataclass
class Transaction:
    date: dt.date
    amount: float
    description: str


class FinanceTracker:
    def __init__(self) -> None:
        self.transactions: list[Transaction] = []

    def record_income(self, amount: float, date: dt.date, description: str) -> None:
        self.transactions.append(Transaction(date, amount, description))

    def record_expense(self, amount: float, date: dt.date, description: str) -> None:
        self.transactions.append(Transaction(date, -abs(amount), description))

    def daily_profit(self) -> dict[dt.date, float]:
        totals: dict[dt.date, float] = defaultdict(float)
        for t in self.transactions:
            totals[t.date] += t.amount
        return dict(sorted(totals.items()))

    def total_profit(self) -> float:
        return sum(t.amount for t in self.transactions)


RECIPE_BOOK: dict[str, list[str]] = {
    "Herring": ["Pickled Herring Rolls", "Herring Chowder"],
    "Salmon": ["Grilled Salmon Steak", "Salmon Sashimi Plate"],
    "Cod": ["Crispy Cod Bites", "Cod & Kelp Stew"],
    "Anchovy": ["Anchovy Ice Toast", "Anchovy Butter Skewers"],
    "Mackerel": ["Smoked Mackerel Bowl", "Mackerel Tartare"],
}


class RecipeSuggester:
    def __init__(self, inventory: Inventory) -> None:
        self.inventory = inventory

    def suggest(self) -> list[str]:
        suggestions = []
        for fish_name in self.inventory.available_fish():
            suggestions.extend(RECIPE_BOOK.get(fish_name, []))
        return suggestions or ["Chef's Surprise (stock running low!)"]


class PreferenceLearner:
    def __init__(self) -> None:
        self._history: dict[str, Counter] = defaultdict(Counter)

    def learn_from_order(self, order: Order) -> None:
        for fish_name, qty in order.items.items():
            self._history[order.customer.name][fish_name] += qty

    def recommend(self, customer_name: str, available: list[str]) -> str | None:
        preferences = self._history.get(customer_name)
        if not preferences:
            return None
        for fish_name, _count in preferences.most_common():
            if fish_name in available:
                return fish_name
        return None


def build_starting_inventory() -> Inventory:
    inv = Inventory()
    inv.add_stock(Fish("Herring", quantity=40, price_per_unit=4.5, supplier_cost=1.8, freshness_days=5))
    inv.add_stock(Fish("Salmon", quantity=25, price_per_unit=7.0, supplier_cost=3.2, freshness_days=4))
    inv.add_stock(Fish("Cod", quantity=30, price_per_unit=5.5, supplier_cost=2.4, freshness_days=6))
    inv.add_stock(Fish("Anchovy", quantity=50, price_per_unit=3.0, supplier_cost=1.0, freshness_days=3))
    inv.add_stock(Fish("Mackerel", quantity=20, price_per_unit=6.0, supplier_cost=2.6, freshness_days=4))
    return inv


def restock_supplies(inventory: Inventory, finance: FinanceTracker, current_date: dt.date) -> None:
    catalogue = {
        "Herring": (4.5, 1.8, 5),
        "Salmon": (7.0, 3.2, 4),
        "Cod": (5.5, 2.4, 6),
        "Anchovy": (3.0, 1.0, 3),
        "Mackerel": (6.0, 2.6, 4),
    }
    low_stock = set(inventory.low_stock_alert()) | (set(catalogue) - set(inventory.snapshot()))
    if not low_stock:
        return

    cost = 0.0
    for name in sorted(low_stock):
        price, supplier_cost, freshness = catalogue[name]
        top_up = random.randint(4, 8)
        inventory.add_stock(Fish(name, top_up, price, supplier_cost, freshness_days=freshness))
        cost += top_up * supplier_cost
    finance.record_expense(cost, current_date, "Fish supplier delivery")


def run_simulation(days: int = 7, seed: int = 42):
    random.seed(seed)

    inventory = build_starting_inventory()
    finance = FinanceTracker()
    orders = OrderManager(inventory, finance)
    suggester = RecipeSuggester(inventory)
    learner = PreferenceLearner()

    customers = [
        Customer("Wally the Walrus", "Walrus"),
        Customer("Sasha the Seal", "Seal"),
        Customer("Ollie the Otter", "Otter"),
        Customer("Pip the Puffin", "Puffin"),
    ]

    start_date = dt.date(2025, 1, 1)
    daily_orders_placed = []

    for day_index in range(days):
        current_date = start_date + dt.timedelta(days=day_index)

        finance.record_expense(15.0, current_date, "Ice block rent")
        restock_supplies(inventory, finance, current_date)

        orders_today = 0
        for customer in customers:
            if random.random() < 0.7:
                available = inventory.available_fish()
                if not available:
                    continue

                recommended = learner.recommend(customer.name, available)
                choice = recommended if recommended else random.choice(available)
                qty = random.randint(1, 3)

                order = orders.place_order(customer, {choice: qty}, current_date)
                if order:
                    learner.learn_from_order(order)
                    orders_today += 1

        daily_orders_placed.append(orders_today)
        discarded = inventory.discard_spoiled()
        if discarded:
            print(f"[{current_date}] Discarded spoiled stock: {', '.join(discarded)}")

    return inventory, finance, orders, suggester, learner, daily_orders_placed


def print_report(inventory, finance, orders, suggester, learner) -> None:
    print("=" * 60)
    print("PENGUEATS: END OF WEEK REPORT")
    print("=" * 60)

    print("\nRemaining inventory:")
    for name, qty in inventory.snapshot().items():
        print(f"  - {name}: {qty} units")

    low_stock = inventory.low_stock_alert()
    if low_stock:
        print(f"\nLow stock alert: {', '.join(low_stock)}")

    print(f"\nTotal orders fulfilled: {len(orders.order_history)}")
    print(f"Total profit: {finance.total_profit():.2f} fish-coins")

    print("\nToday's recipe suggestions based on stock:")
    for dish in suggester.suggest()[:5]:
        print(f"  - {dish}")

    print("\nExample learned recommendation:")
    example_customer = orders.order_history[0].customer.name if orders.order_history else None
    if example_customer:
        rec = learner.recommend(example_customer, inventory.available_fish())
        print(f"  - {example_customer} would likely enjoy: {rec or 'no strong preference yet'}")


if __name__ == "__main__":
    inventory, finance, orders, suggester, learner, daily_orders = run_simulation()
    print_report(inventory, finance, orders, suggester, learner)