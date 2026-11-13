# -*- coding: utf-8 -*-

import datetime
import re




def is_valid_date(text):
    return isinstance(text, str) and re.match(r"^(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[012])/\d{4}$" , text) is not None


def date_key(text):
    return text[6:] + text[3:5] + text[:2]

def date_with_now(date_str):
    today_str = datetime.now().strftime("%d/%m/%Y")
    return date_key(today_str) <= date_key(date_str)


class PlanItem:
    def __init__(self, date, exercise_id, planned_minutes):
        self.date = date                         
        self.exercise_id = exercise_id            
        self.planned_minutes = planned_minutes   

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, value):
        if not is_valid_date(value):
            raise ValueError("Ngày phải có dạng dd/mm/yyyy")
        self._date = value

    @property
    def exercise_id(self):
        return self._exercise_id

    @exercise_id.setter
    def exercise_id(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Mã bài tập không được để trống")
        self._exercise_id = value

    @property
    def planned_minutes(self):
        return self._planned_minutes

    @planned_minutes.setter
    def planned_minutes(self, value):
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError("Thời lượng dự kiến phải là số lớn hơn 0")
        self._planned_minutes = value

    def to_dict(self):
        return {"date": self.date, "exercise_id": self.exercise_id,
                "planned_minutes": self.planned_minutes}

    @staticmethod
    def from_dict(d):
        return PlanItem(d["date"], d["exercise_id"], d["planned_minutes"])


class TrainingPlan:

    
    def __init__(self, plan_id, user_id, name, start_date, end_date, items=None):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Tên kế hoạch không được để trống")
        if date_with_now(start_date) is False:
             raise ValueError("Ngày bắt đầu không được ở trong quá khứ")
        if not is_valid_date(start_date) or not is_valid_date(end_date):
            raise ValueError("Ngày bắt đầu và ngày kết thúc phải có dạng dd/mm/yyyy")
        if date_key(end_date) < date_key(start_date):
            raise ValueError("Ngày kết thúc phải sau hoặc bằng ngày bắt đầu")
        self.plan_id = plan_id
        self.user_id = user_id
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.items = []
        if items is not None:
            for item in items:
                self.add_plan_item(item)

    def add_plan_item(self, plan_item):
        d = date_key(plan_item.date)
        if d < date_key(self.start_date) or d > date_key(self.end_date):
            raise ValueError("Phạm vi ngày tháng không phù hợp với kế hoạch")
        for old in self.items:
            if old.date == plan_item.date and old.exercise_id == plan_item.exercise_id:
                raise ValueError(f"Đã có mục {plan_item.exercise_id} vào ngày {plan_item.date}")
        self.items.append(plan_item)

    def remove_plan_item(self, date, exercise_id):
        for i, item in enumerate(self.items):
            if item.date == date and item.exercise_id == exercise_id:
                self.items.pop(i)
                return True
        return False

    def get_items_by_date(self, date):
        return [item for item in self.items if item.date == date]

  
    @property
    def total_planned_minutes(self):
        total = 0
        for item in self.items:
            total += item.planned_minutes
        return total


    def get_done_minutes(self, item, activities):
        done = 0
        for a in activities:
            if a.user_id != self.user_id:
                continue
            if a.date != item.date:
                continue
            if a.exercise is None:
                continue
            if a.exercise.exercise_id != item.exercise_id:
                continue
            done += a.duration
        if done > item.planned_minutes:
            done = item.planned_minutes
        return done

    def get_total_done_minutes(self, activities):
        total = 0
        for item in self.items:
            total += self.get_done_minutes(item, activities)
        return total

    def get_completion(self, activities):
        planned = self.total_planned_minutes
        if planned == 0:
            return 0.0
        return round(self.get_total_done_minutes(activities) / planned * 100, 1)

    def get_progress_by_date(self, activities):
        result = {}
        for item in self.items:
            if item.date not in result:
                result[item.date] = {"date": item.date, "planned": 0, "actual": 0}
            result[item.date]["planned"] += item.planned_minutes
            result[item.date]["actual"] += self.get_done_minutes(item, activities)
        rows = list(result.values())
        rows.sort(key=lambda r: date_key(r["date"]))
        return rows

   
    def to_dict(self):
        return {"plan_id": self.plan_id, "user_id": self.user_id, "name": self.name,
                "start_date": self.start_date, "end_date": self.end_date,
                "items": [i.to_dict() for i in self.items]}

    @staticmethod
    def from_dict(d):
        items = [PlanItem.from_dict(x) for x in d.get("items", [])]
        return TrainingPlan(d["plan_id"], d["user_id"], d["name"],
                            d["start_date"], d["end_date"], items)
