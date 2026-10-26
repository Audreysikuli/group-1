"""Demos and offline checks for Foundation 1 and A5."""
import sys

from story import (
    DuvetWash,
    HandRinse,
    LaundrySession,
    MachineWash,
    show_choices,
)


class LaundryRequest:
    def __init__(self, student_id, choice, urgent):
        self.student_id = student_id
        self.choice = choice
        self.urgent = urgent


class LaundryQueue:
    """Own pending requests and choose affordable work by priority and arrival."""

    def __init__(self):
        self._requests = []

    @property
    def pending_requests(self):
        return tuple(self._requests)

    def enqueue(self, student_id, choice, urgent=False):
        if not isinstance(student_id, str) or not student_id.strip():
            raise ValueError("Student ID must be a non-empty string.")
        if not callable(getattr(choice, "water_needed", None)):
            raise ValueError("Choice must provide water_needed().")
        if not isinstance(urgent, bool):
            raise ValueError("Urgency must be True or False.")

        request = LaundryRequest(student_id, choice, urgent)
        self._requests.append(request)
        return request

    def _priority_order(self):
        urgent = [request for request in self._requests if request.urgent]
        regular = [request for request in self._requests if not request.urgent]
        return urgent + regular

    def preview_next_affordable(self, session):
        for request in self._priority_order():
            needed = request.choice.water_needed()
            if 0 <= needed <= session.water.remaining:
                return request
        return None

    def complete(self, request, session):
        if not any(pending is request for pending in self._requests):
            return None

        previous_count = session.completed_count
        result = session.book(request.choice)
        if session.completed_count == previous_count + 1:
            self._requests.remove(request)
        return result

    def complete_next(self, session):
        request = self.preview_next_affordable(session)
        if request is None:
            return None
        return self.complete(request, session)


def show_state(session):
    history = [entry["choice"].name for entry in session._entries]
    print(
        f"{session.student}: {session.water.remaining} litres; "
        f"completed: {session.completed_count}; history: {history}"
    )


def run_checks():
    # Urgent FIFO ordering wins over a regular request; preview is read-only.
    queue = LaundryQueue()
    urgent_first = queue.enqueue("S001", HandRinse("First urgent"), urgent=True)
    urgent_second = queue.enqueue("S002", HandRinse("Second urgent"), urgent=True)
    regular_first = queue.enqueue("S003", HandRinse("First regular"))
    session = LaundrySession("Test", 20)
    before = (session.water.remaining, session.completed_count, len(queue.pending_requests))
    assert queue.preview_next_affordable(session) is urgent_first
    assert (session.water.remaining, session.completed_count, len(queue.pending_requests)) == before
    assert queue.complete(urgent_first, session).startswith("Test completes First urgent")
    assert queue.preview_next_affordable(session) is urgent_second
    assert regular_first in queue.pending_requests

    # Skip an unaffordable first urgent job without removing or recording it.
    queue = LaundryQueue()
    too_large = queue.enqueue("S010", DuvetWash(2), urgent=True)
    next_affordable = queue.enqueue("S011", HandRinse("Rinse"), urgent=True)
    queue.enqueue("S012", MachineWash(1))
    session = LaundrySession("Test", 5)
    before = (session.water.remaining, session.completed_count, tuple(queue.pending_requests))
    assert queue.preview_next_affordable(session) is next_affordable
    assert (session.water.remaining, session.completed_count, tuple(queue.pending_requests)) == before
    result = queue.complete_next(session)
    assert result == "Test completes Rinse: 4 litres."
    assert session.water.remaining == 1
    assert session.completed_count == 1
    assert too_large in queue.pending_requests
    assert queue.pending_requests[0] is too_large

    # Invalid urgency is refused without adding a pending request.
    queue = LaundryQueue()
    try:
        queue.enqueue("S020", HandRinse("Rinse"), urgent=1)
    except ValueError:
        pass
    else:
        raise AssertionError("A non-Boolean urgency flag was accepted.")
    assert queue.pending_requests == ()

    # Nothing affordable means no booking, no resource change and no history.
    queue = LaundryQueue()
    queue.enqueue("S030", DuvetWash(2), urgent=True)
    session = LaundrySession("Test", 10)
    before = (session.water.remaining, session.completed_count, tuple(queue.pending_requests))
    assert queue.preview_next_affordable(session) is None
    assert queue.complete_next(session) is None
    assert (session.water.remaining, session.completed_count, tuple(queue.pending_requests)) == before

    # A request not owned by the queue cannot trigger a booking.
    outsider = LaundryRequest("S040", HandRinse("Outside"), urgent=False)
    assert queue.complete(outsider, session) is None
    assert (session.water.remaining, session.completed_count, tuple(queue.pending_requests)) == before
    return 5


def foundation_demo():
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


def queue_demo():
    print("\n=== A5: URGENT LAUNDRY QUEUE ===")
    queue = LaundryQueue()
    first = queue.enqueue("S001", DuvetWash(2), urgent=True)
    queue.enqueue("S002", HandRinse("Hand rinse"), urgent=True)
    queue.enqueue("S003", MachineWash(1))

    session = LaundrySession("Queue desk", 5)
    print("First by priority:", first.student_id, first.choice.name)
    print("Before preview:")
    show_state(session)
    preview = queue.preview_next_affordable(session)
    if preview is None:
        print("No queued job currently fits.")
    else:
        print("Next affordable:", preview.student_id, preview.choice.name)
    print("After preview:")
    show_state(session)
    print("Completed:", queue.complete(preview, session))
    print("After completion:")
    show_state(session)
    print(
        "Unaffordable urgent job remains queued:",
        any(request is first for request in queue.pending_requests),
    )


def main(check_only=False):
    checks = run_checks()
    print(f"Automated checks passed: {checks}")
    if check_only:
        return
    foundation_demo()
    queue_demo()


if __name__ == "__main__":
    main(check_only="--check" in sys.argv)
