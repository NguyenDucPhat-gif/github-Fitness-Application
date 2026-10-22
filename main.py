from DataManager import DataManager
from Sports import Exercise, Running, Swimming, Cycling
from WorkoutManager import WorkoutManager

exercises = [Exercise.from_dict(d) for d in DataManager("exercises.json").load_data()]
ex = {e.exercise_id: e for e in exercises}

wm = WorkoutManager(DataManager("activities.json"), exercises)
wm.add_activity(Running("A01", "duc01", "14/10/2026", 25, 5, ex["E02"], "Cao"))
wm.add_activity(Swimming("A02", "duc01", "14/10/2026", 45, 1.5, ex["E03"], "Vừa"))
wm.add_activity(Cycling("A03", "duc01", "15/10/2026", 60, 20, ex["E06"], "Nhẹ"))

for a in wm.activities_list:
    print(a.activity_id, a.activity_type, a.calories, "|", a.get_summary())
print("Calo 14/10:", wm.get_total_calories_by_date("14/10/2026"))