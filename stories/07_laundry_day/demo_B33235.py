import json
from pathlib import Path
from tempfile import TemporaryDirectory

from story import (
	ClothesAirer,
	EcoWash,
	FeaturedEcoWash,
	HandRinse,
	LaundryChoice,
	LaundryChoiceError,
	LaundryRequestError,
	LaundryResourceError,
	LaundrySession,
	MachineWash,
	SunDry,
	StrictLaundrySession,
	show_choices,
)


def history_labels(session):
	return [entry["choice"].name for entry in session._entries]


class NegativeQuoteChoice:
	name = "Negative quote"

	def water_needed(self):
		return -1


def session_state(session):
	return session.water.remaining, session.completed_count


def check_strict_booking():
	session = StrictLaundrySession("B33235", 8)

	before = session_state(session)
	try:
		session.safe_book(None)
	except LaundryChoiceError:
		pass
	else:
		raise AssertionError("A missing choice should raise LaundryChoiceError.")
	assert session_state(session) == before

	before = session_state(session)
	try:
		session.safe_book(NegativeQuoteChoice())
	except LaundryRequestError:
		pass
	else:
		raise AssertionError("A negative quote should raise LaundryRequestError.")
	assert session_state(session) == before

	before = session_state(session)
	try:
		session.safe_book(MachineWash(2))
	except LaundryResourceError:
		pass
	else:
		raise AssertionError("An unaffordable choice should raise LaundryResourceError.")
	assert session_state(session) == before

	before = session_state(session)
	zero_result = session.safe_book(SunDry())
	assert zero_result == "B33235 completes Sun drying: 0 litres."
	assert session_state(session) == (before[0], before[1] + 1)

	affordable_result = session.safe_book(HandRinse("Hand rinse"))
	assert affordable_result == "B33235 completes Hand rinse: 4 litres."
	assert session_state(session) == (4, 2)


def show_safe_booking(session, choice, label):
	try:
		result = session.safe_book(choice)
	except LaundryChoiceError as error:
		print(f"{label}: Please choose a laundry option. ({error})")
	except LaundryRequestError as error:
		print(f"{label}: The request is invalid. ({error})")
	except LaundryResourceError as error:
		print(f"{label}: There is not enough water. ({error})")
	else:
		print(f"{label}: {result}")
	finally:
		print(f"{label} attempt complete.")


airer = ClothesAirer()
assert not issubclass(ClothesAirer, LaundryChoice)
show_choices([airer])

# The JSON format supports MachineWash, HandRinse, EcoWash, FeaturedEcoWash,
# SunDry and ClothesAirer, reconstructed only from fixed type labels.
session = LaundrySession("B33235", 100)
choices = [
	MachineWash(2),
	HandRinse("Hand rinse"),
	EcoWash(2),
	FeaturedEcoWash(2),
	SunDry(),
	airer,
]
for choice in choices:
	print(session.book(choice))

choices[0].kilograms = 4  # The original successful quote remains saved as 10.

with TemporaryDirectory() as directory:
	save_path = Path(directory) / "laundry.json"
	session.save_json(save_path)
	restored = LaundrySession.load_json(save_path)

	assert restored is not session
	assert restored.water is not session.water
	assert restored.student == session.student
	assert restored.water.remaining == session.water.remaining
	assert restored.completed_count == session.completed_count == 6
	assert history_labels(restored) == history_labels(session)
	assert [type(entry["choice"]) for entry in restored._entries] == [
		MachineWash, HandRinse, EcoWash, FeaturedEcoWash, SunDry, ClothesAirer
	]
	assert restored._entries[0]["cost"] == 10
	assert restored._entries[0]["choice"].water_needed() == 20
	print(f"Restored {restored.completed_count} successes; balance: {restored.water.remaining} litres")

	print(restored.book(ClothesAirer()))
	assert restored.completed_count == 7
	assert restored.water.remaining == session.water.remaining

	before_failure = (restored.water.remaining, restored.completed_count, history_labels(restored))
	missing_path = Path(directory) / "missing.json"
	try:
		LaundrySession.load_json(missing_path)
	except FileNotFoundError:
		print("Missing file refused.")
	else:
		raise AssertionError("A missing file should be refused.")

	malformed_path = Path(directory) / "malformed.json"
	malformed_path.write_text("{not json", encoding="utf-8")
	try:
		LaundrySession.load_json(malformed_path)
	except ValueError as error:
		print(f"Malformed JSON refused: {error}")
	else:
		raise AssertionError("Malformed JSON should be refused.")

	invalid_path = Path(directory) / "invalid.json"
	invalid_path.write_text(
		json.dumps({
			"student": "B33235",
			"remaining": 0,
			"entries": [{"choice": {"type": "unknown_choice", "name": "Unknown"}, "cost": 0}],
		}),
		encoding="utf-8",
	)
	try:
		LaundrySession.load_json(invalid_path)
	except ValueError as error:
		print(f"Invalid record refused: {error}")
	else:
		raise AssertionError("An unknown choice label should be refused.")

	assert (restored.water.remaining, restored.completed_count, history_labels(restored)) == before_failure

print(f"Completed: {restored.completed_count}")
print(f"Remaining water: {restored.water.remaining} litres")

check_strict_booking()
print("\nStrict booking checks passed.")
strict_session = StrictLaundrySession("B33235", 8)
show_safe_booking(strict_session, None, "Missing choice")
show_safe_booking(strict_session, NegativeQuoteChoice(), "Invalid quote")
show_safe_booking(strict_session, MachineWash(2), "Insufficient water")
show_safe_booking(strict_session, SunDry(), "Zero-cost choice")
show_safe_booking(strict_session, HandRinse("Hand rinse"), "Affordable choice")
