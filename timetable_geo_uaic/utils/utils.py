"""HTML, json and other utilities."""
from __future__ import annotations

import os
from typing import Any

import json
from unidecode import unidecode
from attrs import define, field
from bs4 import Tag, ResultSet

from ..request import request_table
from ..objects import (
    Weekday,
    TimeInterval,
    Group,
    Groups,
    Professor,
    Professors,
    Room,
    Rooms,
    Subject,
    Subjects,
    ObjectCreator
)



def _check_is_openable(filepath) -> bool:
    try:
        with open(filepath, 'r') as f:
            json.load(f)
        return True
    except:
        return False
    
def _check_is_file(filepath: str) -> bool:
    """Checks if an input file is a file."""
    if not os.path.isfile(filepath):
        return False
    else:
        return True

def check_json_is_valid(filepath) -> bool:
    return _check_is_file(filepath) and _check_is_openable(filepath)


@define
class _Table:
    """Describes an HTML code table."""
    tag: Tag


@define
class HTMLTableParser:
    _table: _Table = field(init=False, default=None)
    _tag: Tag = field(init=False, default=None)
    _thead: Tag = field(init=False, default=None)
    _tbody: Tag = field(init=False, default=None)
    _tr: ResultSet = field(init=False, default=None)


    @property
    def table(self) -> _Table:
        if self._table is None:
            self._table = _Table(request_table())
        return self._table
    

    @property
    def tag(self) -> Tag:
        if self._tag is None:
            self._tag = self.table.tag
        return self._tag
    

    @property
    def thead(self) -> Tag:
        if self._thead is None:
            self._thead = self.tag.find('thead')
        return self._thead
    
    @property
    def tbody(self) -> Tag:
        if self._tbody is None:
            self._tbody = self.tag.find('tbody')
        return self._tbody
    
    @property
    def tr(self) -> ResultSet[Any]:
        """Will return a ResultSet with 6 Tag objects, each tag corresponding to a time interval.
        The tags contain all the detailed information about each subject."""
        if self._tr is None:
            self._tr = self.tbody.find_all('tr', recursive=False)
            self._tr = self._tr[:-1] # without the footer
        return self._tr

    def get_elements_from_lines(self, result_set: ResultSet, class_: str) -> list[tuple[tuple[str]]]:
        lines = self.find_all_from_result_set(result_set, 'tr', {'class': class_})
        elements: list[tuple[str]] = []
        for line in lines:
            sub_element = tuple()
            for span in line:
                sub_sub_element = tuple()
                for subspan in span:
                    text = subspan.getText().strip()
                    sub_sub_element += (unidecode(text), )
                sub_element += (sub_sub_element, )
            elements.append(sub_element)
        return elements
    
    def get_weekdays(self) -> list[str]:
        result_set = self.thead.find_all('th', attrs={'class': 'xAxis'})
        return [unidecode(result.getText()) 
                for result in result_set]
    
    def get_intervals(self) -> list[str]:
        intervals = self.tbody.find_all('th', attrs={'class': 'yAxis'})
        return [unidecode(interval.getText())
                for interval in intervals]

    def get_subjects(self) -> list[tuple[tuple[str]]]:
        """Returns the subjects as a list of tuples."""
        return self.get_elements_from_lines(self.tr, 'line1')
    
    def get_groups(self) -> list[tuple[tuple[str]]]:
        return self.get_elements_from_lines(self.tr, 'studentsset line0')
    
    def get_professors(self) -> list[tuple[tuple[str]]]:
        return self.get_elements_from_lines(self.tr, 'teacher line2')
    
    def get_rooms(self) -> list[tuple[tuple[str]]]:
        return self.get_elements_from_lines(self.tr, 'room line3')

    @staticmethod
    def find_all_from_result_set(result_set: ResultSet, name: str, *args, **kwargs) -> list[Tag]:
        extracted_attrs = []
        for tag in result_set:
            elements = tag.find_all(name, *args, **kwargs)
            extracted_attrs.append(elements)
        return extracted_attrs
    

@define
class HTMLElementsToJson:
    parser: HTMLTableParser = field(default=None)
    _weekdays: list[str] = field(init=False, default=None)
    _time_intervals: list[tuple[str]] = field(init=False, default=None)
    _groups: list[tuple[tuple[str]]] = field(init=False, default=None)
    _subjects: list[tuple[tuple[str]]] = field(init=False, default=None)
    _professors: list[tuple[tuple[str]]] = field(init=False, default=None)
    _rooms: list[tuple[tuple[str]]] = field(init=False, default=None)
    timetable: dict = field(factory=dict, init=False)

    @property
    def json_file(self) -> str:
        return json.dumps(self.timetable, indent=2)
    
    @property
    def json_file_path(self) -> str:
        return os.path.join(os.path.dirname(__file__), '../timetable.json')

    @property
    def weekdays(self) -> list[str]:
        if self._weekdays is None:
            self._weekdays = self.parser.get_weekdays()
        return self._weekdays
    
    @property
    def time_intervals(self) -> list[tuple[str]]:
        if self._time_intervals is None:
            self._time_intervals = self.parser.get_intervals()
        return self._time_intervals
    
    @property
    def groups(self) -> list[tuple[tuple[str]]]:
        if self._groups is None:
            self._groups = self.parser.get_groups()
        return self._groups
    
    @property
    def subjects(self) -> list[tuple[tuple[str]]]:
        if self._subjects is None:
            self._subjects = self.parser.get_subjects()
        return self._subjects
    
    @property
    def professors(self) -> list[tuple[tuple[str]]]:
        if self._professors is None:
            self._professors = self.parser.get_professors()
        return self._professors
    
    @property
    def rooms(self) -> list[tuple[tuple[str]]]:
        if self._rooms is None:
            self._rooms = self.parser.get_rooms()
        return self._rooms
    
    def add_weekdays(self) -> None:
        for weekday in self.weekdays:
            self.timetable[weekday] = None

    def add_intervals(self) -> None:
        for k in self.timetable:
            self.timetable[k] = {time_interval: {} for time_interval in self.time_intervals}

    def add_to_intervals(self, table_element: str) -> None:
        property_ = getattr(self, table_element)
        for i, interval in enumerate(self.timetable.values()):
            for j, v in enumerate(interval.values()):
                v[table_element] = property_[j][i]
            
    def add_groups(self) -> None:
        self.add_to_intervals('groups')

    def add_subjects(self) -> None:
        self.add_to_intervals('subjects')

    def add_professors(self) -> None:
        self.add_to_intervals('professors')

    def add_rooms(self) -> None:
        self.add_to_intervals('rooms')

    def create_json_attribute(self) -> None:
        self.add_weekdays()
        self.add_intervals()
        self.add_groups()
        self.add_professors()
        self.add_rooms()
        self.add_subjects()
                    
    def save_json(self) -> None:
        self.create_json_attribute()
        with open(self.json_file_path, 'w') as f:
            f.write(self.json_file)

    def read_json(self) -> dict:
        if not check_json_is_valid(self.json_file_path):
            if self.parser is None:
                self.parser = HTMLTableParser()
            self.save_json()
        return json.load(open(self.json_file_path))
    

@define
class JsonToObjects:
    timetable: dict = field(factory=dict)
    creator: ObjectCreator = field(init=False)

    def __attrs_post_init__(self):
        self.creator = ObjectCreator(self.timetable)

    def to_weekday_objects(self):
        self.timetable = {Weekday(k): v for k, v in self.timetable.items()}

    def to_timeinterval_objects(self):
        self.timetable = {TimeInterval(k): v for k, v in self.timetable.values()}

    def to_objects(self, object: type, aggregate_object: type, timetable_key: str, split_separator=None, split_maxsplit=-1):
        for weekday, daily_timetable in self.timetable.items():
            for interval, lectures in daily_timetable.items():
                    to_object = lambda x: aggregate_object(
                        [object(lecture_object) for lecture_object in x.split(split_separator, split_maxsplit)]
                        )
                    self.timetable[weekday][interval][timetable_key] = [to_object(x) for x in lectures[timetable_key]]

    def convert_timetable(self):
        self.to_objects(Group, Groups, 'groups', ',')
        self.to_objects(Professor, Professors, 'professors', ',')
        self.to_objects(Room, Rooms, 'rooms', split_maxsplit=0)
        self.to_objects(Subject, Subjects, 'subjects', split_maxsplit=0)
        return self.timetable


def get_attribute_name(class_, obj):
    for name, value in vars(class_).items():
        if value is obj:
            return name
    return None