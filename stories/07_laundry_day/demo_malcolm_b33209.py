"""Demonstrate Foundation 2: adding water without changing laundry history."""
from story import HandRinse, LaundrySession


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


def main():
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


if __name__ == "__main__":
    main()
