"""Demo for Foundation 1: Duvet Wash
   Sikuli Mukasa Christel
   M25B13/052
   B33495
"""


from story import DuvetWash, LaundrySession, show_choices


def main():
    print("=== FOUNDATION 1: DUVET WASH ===")

    duvet = DuvetWash(2)
    choices = [duvet]

    print("\n1. Normal case")
    show_choices(choices)

    print("\n2. Successful booking")
    session = LaundrySession("Nambi", 20)

    print("Before:", session.water.remaining, "litres")
    print("Completed:", session.completed_count)

    print(session.book(duvet))

    print("After:", session.water.remaining, "litres")
    print("Completed:", session.completed_count)

    print("\n3. Refusal case: invalid quantity")
    for quantity in [0, -1, 2.5, True]:
        try:
            DuvetWash(quantity)
        except ValueError as error:
            print(f"{quantity!r}: Refused - {error}")

    print("\n4. Insufficient water")
    small_session = LaundrySession("Alex", 10)

    print("Before:", small_session.water.remaining, "litres")
    print("Completed:", small_session.completed_count)

    print(small_session.book(duvet))

    print("After:", small_session.water.remaining, "litres")
    print("Completed:", small_session.completed_count)


if __name__ == "__main__":
    main()
