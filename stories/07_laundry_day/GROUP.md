# Laundry Day group work

## Selected later-topic options

### A5 — The urgent laundry queue

- **User need:** Help the hostel attendant choose a laundry job that can finish with the water currently available, while giving urgent requests priority.
- **Inputs:** Student ID, a laundry choice, an urgency Boolean, and the current `LaundrySession`.
- **Rules:** Urgent requests come before regular requests; arrival order is preserved within each priority. Previewing does not change the queue, water or history. If the first request in priority order does not fit, leave it queued and preview the next affordable request. Complete and remove a request only when `LaundrySession.book()` records its success.
- **Expected outcomes:** The attendant can see the next affordable request without changing state, successfully book and remove it, and retain uncompleted requests after an unaffordable or invalid booking.
- **OOP design:** `LaundryQueue` owns pending requests and priority/order policy. It collaborates with the existing `LaundrySession` to spend water and record completed work; it does not duplicate the session's booking rules.
- **Member responsible:** Sikuli Mukasa Christel (branch `Sikuli_Musaka_B33495`; access number B33495).
- **Merged PR links:** None yet; this work has not been merged.
- **Demo command:** `py -3 stories/07_laundry_day/demo_sikuli_b33495.py`
- **Check/test command:** `py -3 stories/07_laundry_day/demo_sikuli_b33495.py --check`
- **Result:** Five offline checks pass. Urgent requests retain FIFO order, an unaffordable first urgent request stays queued while the next affordable request completes, and refused/unaffordable work leaves the session and queue unchanged. The demo prints resource and history before and after preview and completion.
