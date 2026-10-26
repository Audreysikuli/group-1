from story import ClothesAirer, LaundryChoice, LaundrySession, show_choices


airer = ClothesAirer()
assert not issubclass(ClothesAirer, LaundryChoice)

show_choices([airer])

session = LaundrySession("B33235", 0)
print(session.book(airer))
print(f"Completed: {session.completed_count}")
print(f"Remaining water: {session.water.remaining} litres")

assert session.completed_count == 1
assert session.water.remaining == 0