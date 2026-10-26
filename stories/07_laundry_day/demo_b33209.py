from story import WaterTank


tank = WaterTank(10)

before = tank.remaining
accepted = tank.add_more(5)
print(f"Add 5: {accepted}; water {before} -> {tank.remaining}")

for amount in (0, -2, 1.5, True):
    before = tank.remaining
    accepted = tank.add_more(amount)
    print(f"Add {amount!r}: {accepted}; water {before} -> {tank.remaining}")
