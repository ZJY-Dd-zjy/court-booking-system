from sa_duiqi import optimize_with_time

time_slots = [
    {"slot_id": 1, "date": "2026-08-15", "start_time": "08:00", "end_time": "09:30", "index": 0},
    {"slot_id": 2, "date": "2026-08-15", "start_time": "10:00", "end_time": "11:30", "index": 1},
]

courts = [
    {"id": 1, "court_name": "羽毛球A", "type": "羽毛球", "location": "A区", "slot_id": 1, "unique_key": "court_0_slot_1"},
    {"id": 2, "court_name": "羽毛球A", "type": "羽毛球", "location": "A区", "slot_id": 2, "unique_key": "court_0_slot_2"},
    {"id": 3, "court_name": "乒乓球B", "type": "乒乓球", "location": "B区", "slot_id": 1, "unique_key": "court_1_slot_1"},
    {"id": 4, "court_name": "乒乓球B", "type": "乒乓球", "location": "B区", "slot_id": 2, "unique_key": "court_1_slot_2"},
]

users = [
    {"id": 1, "name": "用户1", "preference": "羽毛球"},
    {"id": 2, "name": "用户2", "preference": "乒乓球"},
]

r = optimize_with_time(courts, users, time_slots, preferences={
    "max_iterations": 200,
    "iterations_per_temp": 10,
    "verbose": False
})

print("violations:", r["violations"])
print("match_rate:", r["match_rate"])
for a in r["assignments"]:
    print(a)
