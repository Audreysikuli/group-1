"""Laundry Day Before the Presentation — a complete Weeks 1–6 story.
Run: python3 story.py. All numbers and events are invented for learning.
"""
from abc import ABC, abstractmethod
import json


# ACT 1: The resource owns its value and the rules for changing it.
class WaterTank:
    def __init__(self, amount):
        self.remaining = amount  # Starting values go through the setter too.

    @property
    def remaining(self):
        return self.__remaining  # Name mangling, not a security lock.

    @remaining.setter
    def remaining(self, amount):
        if amount < 0:
            raise ValueError("Remaining litres cannot be negative.")
        self.__remaining = amount

    def use(self, amount):
        if amount <= 0 or amount > self.remaining:
            return False  # Refuse before changing state.
        self.remaining = self.remaining - amount
        return True

    def add_more(self, amount):
        if not isinstance(amount, int) or isinstance(amount, bool) or amount <= 0:
            return False
        self.remaining = self.remaining + amount
        return True


# ACT 2: The abstract family says what every concrete choice must provide.
class LaundryChoice(ABC):
    unit = "litres"  # Class attribute; every instance has its own name.

    def __init__(self, name):
        self.name = name

    def describe(self):
        return f"{self.name} needs {self.water_needed():,} {self.unit}."

    @abstractmethod
    def water_needed(self):
        pass


class MachineWash(LaundryChoice):
    def __init__(self, kilograms=2):
        if not isinstance(kilograms, int) or isinstance(kilograms, bool) or kilograms <= 0:
            raise ValueError("Kilograms must be a positive whole number.")
        super().__init__("Machine wash")
        self.kilograms = kilograms

    def water_needed(self):
        return self.kilograms * 5


class HandRinse(LaundryChoice):  # Siblings show hierarchical inheritance.
    def water_needed(self):
        return 4


class EcoWash(MachineWash):  # A third level in the same family.
    def __init__(self, kilograms=2):
        super().__init__(kilograms)
        self.name = "Eco wash"

    def water_needed(self):
        return super().water_needed() // 2  # Reuse, then specialise, the parent's calculation.


# ACT 3: Multiple inheritance adds a small descriptive ability.
class LaundryHype:
    def describe(self):
        return f"Fresh clothes, fresh start! {super().describe()}"


class FeaturedEcoWash(LaundryHype, EcoWash):
    pass  # The full hierarchy combines multiple and multilevel inheritance.


class SunDry:  # No shared parent: callers use its matching behaviour.
    name = "Sun drying"

    def water_needed(self):
        return 0

    def describe(self):
        return "Sun drying: 0 litres in this classroom model."


class ClothesAirer:
    def __init__(self):
        self.name = "Clothes airer"

    def describe(self):
        return f"{self.name}: 0 litres in this classroom model."

    def water_needed(self):
        return 0


# ACT 4: The coordinator HAS-A resource, and USES-A chosen object.
class LaundrySession:
    def __init__(self, student, amount):
        self.student = student
        self.water = WaterTank(amount)  # Owned part: composition.
        self._entries = []  # Internal by convention; fresh for every instance.

    @property
    def completed_count(self):
        return len(self._entries)  # Read-only: it reflects actual history.

    @staticmethod
    def _choice_to_data(choice):
        choice_type = type(choice)
        if choice_type is MachineWash:
            kind = "machine_wash"
            extra = {"kilograms": choice.kilograms}
        elif choice_type is HandRinse:
            kind = "hand_rinse"
            extra = {}
        elif choice_type is EcoWash:
            kind = "eco_wash"
            extra = {"kilograms": choice.kilograms}
        elif choice_type is FeaturedEcoWash:
            kind = "featured_eco_wash"
            extra = {"kilograms": choice.kilograms}
        elif choice_type is SunDry:
            kind = "sun_dry"
            extra = {}
        elif choice_type is ClothesAirer:
            kind = "clothes_airer"
            extra = {}
        else:
            raise ValueError(f"Unsupported laundry choice type: {choice_type.__name__}.")

        if not isinstance(choice.name, str):
            raise ValueError("Choice names must be strings to save a session.")
        return {"type": kind, "name": choice.name, **extra}

    @staticmethod
    def _choice_from_data(data):
        if not isinstance(data, dict) or not isinstance(data.get("type"), str):
            raise ValueError("Each saved choice must be an object with a type label.")

        kind = data["type"]
        quantity_types = {
            "machine_wash": MachineWash,
            "eco_wash": EcoWash,
            "featured_eco_wash": FeaturedEcoWash,
        }
        simple_types = {
            "hand_rinse": HandRinse,
            "sun_dry": SunDry,
            "clothes_airer": ClothesAirer,
        }
        if kind in quantity_types:
            if set(data) != {"type", "name", "kilograms"}:
                raise ValueError(f"Saved {kind} choice has invalid fields.")
            kilograms = data["kilograms"]
            if not isinstance(kilograms, int) or isinstance(kilograms, bool) or kilograms <= 0:
                raise ValueError("Saved kilograms must be a positive whole number.")
            choice = quantity_types[kind](kilograms)
        elif kind in simple_types:
            if set(data) != {"type", "name"}:
                raise ValueError(f"Saved {kind} choice has invalid fields.")
            choice = simple_types[kind]() if kind != "hand_rinse" else HandRinse(data["name"])
        else:
            raise ValueError(f"Unknown saved laundry choice type: {kind}.")

        if not isinstance(data["name"], str):
            raise ValueError("Saved choice names must be strings.")
        choice.name = data["name"]
        return choice

    def save_json(self, path):
        if not isinstance(self.student, str):
            raise ValueError("Student names must be strings to save a session.")
        remaining = self.water.remaining
        if not isinstance(remaining, int) or isinstance(remaining, bool) or remaining < 0:
            raise ValueError("Remaining litres must be a non-negative whole number to save a session.")

        entries = []
        for entry in self._entries:
            cost = entry["cost"]
            if not isinstance(cost, int) or isinstance(cost, bool) or cost < 0:
                raise ValueError("Saved costs must be non-negative whole numbers.")
            entries.append({"choice": self._choice_to_data(entry["choice"]), "cost": cost})

        data = {"student": self.student, "remaining": remaining, "entries": entries}
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)

    @classmethod
    def load_json(cls, path):
        try:
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as error:
            raise ValueError("Session file contains malformed JSON.") from error

        if not isinstance(data, dict) or set(data) != {"student", "remaining", "entries"}:
            raise ValueError("Session data must contain student, remaining and entries.")
        if not isinstance(data["student"], str):
            raise ValueError("Saved student must be a string.")
        remaining = data["remaining"]
        if not isinstance(remaining, int) or isinstance(remaining, bool) or remaining < 0:
            raise ValueError("Saved remaining litres must be a non-negative whole number.")
        if not isinstance(data["entries"], list):
            raise ValueError("Saved entries must be a list.")

        entries = []
        for saved_entry in data["entries"]:
            if not isinstance(saved_entry, dict) or set(saved_entry) != {"choice", "cost"}:
                raise ValueError("Each saved entry must contain choice and cost.")
            cost = saved_entry["cost"]
            if not isinstance(cost, int) or isinstance(cost, bool) or cost < 0:
                raise ValueError("Saved costs must be non-negative whole numbers.")
            choice = cls._choice_from_data(saved_entry["choice"])
            entries.append({"choice": choice, "cost": cost})

        session = cls(data["student"], remaining)
        session._entries = entries
        return session

    def book(self, choice):
        needed = choice.water_needed()  # Each choice knows its own calculation.
        if needed < 0:
            return "Invalid negative requirement. Nothing recorded."
        if needed == 0 or self.water.use(needed):
            # Save the quoted cost now: later edits to the choice cannot change it.
            self._entries.append({"choice": choice, "cost": needed})
            return f"{self.student} completes {choice.name}: {needed:,} litres."
        return f"Not enough litres for {choice.name}. Nothing recorded."


def show_choices(choices):
    for choice in choices:
        print(choice.describe())  # Same call, different implementations.


# ACT 5: A complete story, including a refusal and independent object state.
def main():
    print("=== LAUNDRY DAY BEFORE THE PRESENTATION ===")
    print("Nambi needs clean clothes for a presentation. The hostel water tank is nearly empty.")
    choices = [MachineWash(), HandRinse("Hand rinse"),
               FeaturedEcoWash(), SunDry()]
    show_choices(choices)  # Includes an unrelated duck-typed guest.
    session = LaundrySession("Nambi", 18)
    other = LaundrySession("Alex", 18)
    print(session.book(choices[2]))
    print(session.book(choices[0]))
    print(session.book(choices[0]))  # Eventually the same request will not fit.
    print(session.book(choices[3]))
    print(other.book(choices[1]))
    print(f"{session.student}: {session.water.remaining:,} litres; completed: {session.completed_count}")
    print(f"{other.student}: {other.water.remaining:,} litres; completed: {other.completed_count}")
    print("MRO (method lookup order):")
    for parent in FeaturedEcoWash.__mro__:
        print(parent.__name__)
    print("Ending: The clothes are ready, and the remaining water is enough for the next person.")


if __name__ == "__main__":
    main()
