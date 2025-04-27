import json
from typing import List


class FieldType:
    def __init__(self, id: int, name: str, default_value: bool) -> None:
        self.id: int = id
        self.name: str = name
        self.default_value: bool = default_value

    def to_dict(self):
        return {"id": self.id, "name": self.name, "default_value": self.default_value}


class Field:
    types: List[FieldType] = []

    def __init__(self, id, name, default_values):
        self.id = id
        self.name = name

        for t in Field.types:
            if int(self.id) == t.id and t.default_value:
                self.default_values = json.dumps(default_values)
                break

    @staticmethod
    def init_types(types):
        for t in types:
            Field.types.append(
                FieldType(
                    t["field_type_id"], t["field_type_name"], t["field_type_defaults"]
                )
            )


class Teacher:
    """docstring for Teacher ."""

    def __init__(self, id=None, name=None, phone_number=None):
        if id:
            self.id = id
        if name:
            self.name = name
        if phone_number:
            self.phone_number = phone_number


class Class:
    """docstring for Class ."""

    week_days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    def __init__(
        self,
        id=None,
        name=None,
        days_of_week=None,
        time_of_day=None,
        fields=None,
        teachers=None,
        package_id=None,
    ):
        if id:
            self.id = id
        if name:
            self.name = name
        if days_of_week:
            self.days_of_week = self.encode_days_binary(days_of_week)
        if time_of_day:
            self.time_of_day = time_of_day
        if fields:
            self.fields = self.parse_fields(fields)
        if teachers:
            self.teachers = [Teacher(id=t_id) for t_id in teachers]
        if package_id:
            self.package_id = package_id

    def encode_days_binary(self, selected_days):
        return "".join("1" if day in selected_days else "0" for day in Class.week_days)

    def decode_days_binary(self):
        return [Class.week_days[i] for i in range(7) if self.days_of_week[i] == "1"]

    def is_running_on(self, day):
        return day in self.decode_days_binary()

    def parse_fields(self, fields):
        return [
            Field(int(f["field_type_id"]), f["field_name"], f["defaultValues"])
            for f in json.loads(fields)
        ]
