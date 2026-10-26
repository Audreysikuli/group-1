"""Demo for Foundation 1: Duvet Wash."""
from story import DuvetWash, LaundrySession, show_choices


def show_state(session):
    history = [entry["choice"].name for entry in session._entries]
    print(
        f"{session.student}: {session.water.remaining} litres; "
        f"completed: {session.completed_count}; history: {history}"
    )


def main():
    print("=== FOUNDATION 1: DUVET WASH ===")
    duvet = DuvetWash(2)

    print("\n1. Normal case")
    show_choices([duvet])

    session = LaundrySession("Nambi", 20)
    print("\n2. Successful booking")
    print("Before:")
    show_state(session)
    print(session.book(duvet))
    print("After:")
    show_state(session)

    print("\n3. Boundary/refusal cases")
    for quantity in (0, -1, 2.5, True):
        try:
            DuvetWash(quantity)
        except ValueError as error:
            print(f"{quantity!r} duvets: Refused - {error}")

    small_session = LaundrySession("Alex", 10)
    print("Before:")
    show_state(small_session)
    print(small_session.book(duvet))
    print("After:")
    show_state(small_session)


if __name__ == "__main__":
    main()
