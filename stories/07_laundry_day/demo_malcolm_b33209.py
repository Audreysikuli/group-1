"""Demonstrate water refills and strict laundry-request errors."""
from story import ClothesAirer, DuvetWash, HandRinse, LaundrySession


class LaundryChoiceError(Exception):
    """Raised when no laundry choice is supplied."""


class LaundryRequestError(Exception):
    """Raised when a choice has an invalid water requirement."""


class LaundryResourceError(Exception):
    """Raised when a valid request exceeds the available water."""


class StrictLaundrySession(LaundrySession):
    def safe_book(self, choice):
        if choice is None:
            raise LaundryChoiceError("A laundry choice is required.")

        needed = choice.water_needed()
        if not isinstance(needed, int) or isinstance(needed, bool) or needed < 0:
            raise LaundryRequestError(
                "The water requirement must be a non-negative whole number."
            )
        if needed > self.water.remaining:
            raise LaundryResourceError(
                f"This choice needs {needed} litres, but only "
                f"{self.water.remaining} remain."
            )

        return self.book(choice)


class NegativeQuoteChoice:
    name = "Negative quote test"

    def water_needed(self):
        return -1


def state(session):
    history = tuple(
        (entry["choice"].name, entry["cost"]) for entry in session._entries
    )
    return session.water.remaining, session.completed_count, history


def show_state(session):
    history = [name for name, _ in state(session)[2]]
    print(
        f"{session.student}: {session.water.remaining} litres; "
        f"completed: {session.completed_count}; history: {history}"
    )


def attempt(session, choice):
    try:
        result = session.safe_book(choice)
    except LaundryChoiceError as error:
        print(f"Friendly refusal: {error}")
        return False
    except LaundryRequestError as error:
        print(f"Friendly refusal: {error}")
        return False
    except LaundryResourceError as error:
        print(f"Friendly refusal: {error}")
        return False
    else:
        print(result)
        return True
    finally:
        print("Attempt complete.")


def assert_refused(session, choice, error_type):
    before = state(session)
    try:
        session.safe_book(choice)
    except error_type:
        pass
    else:
        raise AssertionError(f"{error_type.__name__} was not raised.")
    assert state(session) == before


def run_checks():
    assert_refused(
        StrictLaundrySession("Check", 10), None, LaundryChoiceError
    )
    assert_refused(
        StrictLaundrySession("Check", 10), NegativeQuoteChoice(), LaundryRequestError
    )
    assert_refused(
        StrictLaundrySession("Check", 3),
        HandRinse("Hand rinse"),
        LaundryResourceError,
    )

    session = StrictLaundrySession("Check", 10)
    assert session.safe_book(HandRinse("Hand rinse")).startswith("Check completes")
    assert state(session) == (6, 1, (("Hand rinse", 4),))

    zero_cost_session = StrictLaundrySession("Check", 0)
    assert zero_cost_session.safe_book(ClothesAirer()).startswith("Check completes")
    assert state(zero_cost_session) == (0, 1, (("Clothes airer", 0),))
    return 5


def foundation_2_demo():
    print("=== FOUNDATION 2: ADD MORE WATER ===")
    session = LaundrySession("Malcolm", 10)
    session.book(HandRinse("Hand rinse"))

    print("\n1. Normal case: add 5 litres")
    before = state(session)
    print("Before:")
    show_state(session)
    assert session.water.add_more(5) is True
    print("add_more(5): True")
    print("After:")
    show_state(session)
    after = state(session)
    assert after == (before[0] + 5, before[1], before[2])

    print("\n2. Boundary/refusal cases")
    for amount in (0, -1, 2.5, True):
        before = state(session)
        print(f"Before add_more({amount!r}):")
        show_state(session)
        result = session.water.add_more(amount)
        print(f"add_more({amount!r}): {result}")
        print("After:")
        show_state(session)
        assert result is False
        assert state(session) == before


def strict_booking_demo():
    print("\n=== STRICT LAUNDRY REQUESTS ===")
    session = StrictLaundrySession("Malcolm", 5)
    attempts = (
        ("Missing choice", None),
        ("Invalid quote", NegativeQuoteChoice()),
        ("Not enough water", DuvetWash(1)),
        ("Affordable request", HandRinse("Hand rinse")),
        ("Valid zero-cost choice", ClothesAirer()),
    )

    for label, choice in attempts:
        print(f"\n{label}")
        print("Before:")
        show_state(session)
        succeeded = attempt(session, choice)
        print("After:")
        show_state(session)
        if label in ("Missing choice", "Invalid quote", "Not enough water"):
            assert succeeded is False
        else:
            assert succeeded is True


def main():
    checks = run_checks()
    print(f"Automated checks passed: {checks}")
    foundation_2_demo()
    strict_booking_demo()


if __name__ == "__main__":
    main()
