import json
from pathlib import Path
from tempfile import TemporaryDirectory

from story import (
	ClothesAirer,
	EcoWash,
	FeaturedEcoWash,
	HandRinse,
	LaundryChoice,
	LaundrySession,
	MachineWash,
	SunDry,
	show_choices,
)


def history_labels(session):
	return [entry["choice"].name for entry in session._entries]


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