from story import (
    HandRinse,
    LaundryChoiceError,
    LaundryRequestError,
    LaundryResourceError,
    MachineWash,
    StrictLaundrySession,
    SunDry,
    WaterTank,
)


tank = WaterTank(10)

before = tank.remaining
accepted = tank.add_more(5)
print(f"Add 5: {accepted}; water {before} -> {tank.remaining}")

for amount in (0, -2, 1.5, True):
    before = tank.remaining
    accepted = tank.add_more(amount)
    print(f"Add {amount!r}: {accepted}; water {before} -> {tank.remaining}")


class NegativeChoice:
    name = "Negative choice"

    def water_needed(self):
        return -1


def try_booking(session, choice, label):
    before = (session.water.remaining, session.completed_count)
    try:
        result = session.safe_book(choice)
        print(f"{label}: {result}")
        return None
    except LaundryChoiceError as error:
        assert (session.water.remaining, session.completed_count) == before
        print(f"Choice error: {error}")
        return LaundryChoiceError
    except LaundryRequestError as error:
        assert (session.water.remaining, session.completed_count) == before
        print(f"Request error: {error}")
        return LaundryRequestError
    except LaundryResourceError as error:
        assert (session.water.remaining, session.completed_count) == before
        print(f"Resource error: {error}")
        return LaundryResourceError
    finally:
        print(f"{label} attempt complete.")


session = StrictLaundrySession("B33209", 4)
assert try_booking(session, None, "Missing choice") is LaundryChoiceError
assert try_booking(session, NegativeChoice(), "Invalid quote") is LaundryRequestError
assert try_booking(session, MachineWash(), "Insufficient water") is LaundryResourceError
assert (session.water.remaining, session.completed_count) == (4, 0)
assert try_booking(session, SunDry(), "Zero-cost choice") is None
assert (session.water.remaining, session.completed_count) == (4, 1)
assert try_booking(session, HandRinse("Hand rinse"), "Affordable choice") is None
assert (session.water.remaining, session.completed_count) == (0, 2)
