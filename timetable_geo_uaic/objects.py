from __future__ import annotations

import re
from collections import UserList

from attrs import define, field



@define
class Group:
    """This object describes an University group."""
    name: str
    year: int = field(init=False)
    programme: str = field(init=False)
    aggregate: bool = field(init=False)


    def __attrs_post_init__(self) -> None:
        self.name = self.name.strip()
        self.year = self._get_group_year()
        self.programme = self._get_group_programme()
        self.aggregate = self._is_group_aggregate()


    def _get_group_numerical_code(self) -> int:
        return re.findall(r'\d+', self.name)[0]


    def _get_group_length(self) -> int:
        """Returns the digit length of a group name (e.g. GR34 will return 2, GR114 will return 3)."""
        return len(self._get_group_numerical_code())
    

    def _get_group_year(self) -> int:
        """Returns the year of a group."""
        return re.findall(r'\d', self.name)[0]
    

    def _get_group_programme(self) -> int:
        """Returns the programme of a group (e.g. GR or GM)."""
        return re.findall(r'\D+', self.name)[0]
    

    def _is_group_aggregate(self) -> bool:
        return self._get_group_length() == 1 or self._get_group_length() == 3
    

@define(frozen=True)
class Groups(UserList):
    """This class describes a collection of Group objects. There cannot be duplicate Group objects."""
    data: list[Group] = field(factory=list)
    sort_values: bool = True
    _names: list[str] = field(init=False)
    

    def __attrs_post_init__(self) -> None:
        if self.sort_values and self.data:
            self.sort()


    @property
    def names(self) -> list[str]:
        return [group.name for group in self.data]
    

    def sort(self) -> None:
        self.data.sort(key=lambda x: x.name)


    def get_belonging_groups(self, group: Group) -> tuple[Group]:
        """Returns the belonging aggregates of a group as a Groups object.
        For example, for GM22 it returns a Groups object containing Group objects
        of GM2, GM221, GM222."""
        if not isinstance(group, Group):
            return []
        groups = [group]
        for aggregate in self:
            if not aggregate.aggregate:
                continue
            if aggregate._get_group_length() == 3 and not group.name in aggregate.name:
                continue
            if aggregate.year == group.year and aggregate.programme == group.programme:
                groups.append(aggregate)
        return Groups(groups)
    

    def append(self, group: Group) -> None:
        super().append(group)
        self.sort()


@define
class Professor:
    name: str


    def __attrs_post_init__(self) -> None:
        self.name = self.name.strip()


@define(frozen=True)
class Professors(UserList):
    data: list[Professor] = field(factory=list)
    sort_values: bool = True
    _names: list[str] = field(init=False)


    def __attrs_post_init__(self) -> None:
        if self.sort_values and self.data:
            self.sort()


    @property
    def names(self) -> list[str]:
        return [professor.name for professor in self.data]
    

    def sort(self) -> None:
        self.data.sort(key=lambda x: x.name)


    def append(self, professor: Professor) -> None:
        super().append(professor)
        self.sort()


@define
class Room:
    """This object describes a Room where lectures/seminars take place."""
    name: str


    def __attrs_post_init__(self) -> None:
        self.name = self.name.strip()


@define(frozen=True)
class Rooms(UserList):
    data: list[Room] = field(factory=list)
    sort_values: bool = True
    _names: list[str] = field(init=False)


    def __attrs_post_init__(self) -> None:
        if self.sort_values and self.data:
            self.sort()

    @property
    def names(self) -> list[str]:
        return [room.name for room in self.data]
    

    def sort(self) -> None:
        self.data.sort(key=lambda x: x.name)


    def append(self, subject: Room) -> None:
        super().append(subject)
        self.sort()


@define
class Subject:
    """This object describes a University subject."""
    name: str


@define(frozen=True)
class Subjects(UserList):
    data: list[Subject] = field(factory=list)
    sort_values: bool = True
    _names: list[str] = field(init=False)


    def __attrs_post_init__(self) -> None:
        if self.sort_values and self.data:
            self.sort()


    @property
    def names(self) -> list[str]:
        return [subject.name for subject in self.data]
    

    def sort(self) -> None:
        self.data.sort(key=lambda x: x.name)


    def append(self, subject: Subject) -> None:
        super().append(subject)
        self.sort()


# To refactor the code at some point to include this object
@define
class Lecture:
    subject: Subject | list[Subject]
    professor: Professor | list[Professor]
    room: Room
    group: Group | list[Group]


@define
class TimeInterval:
    name: str # e.g. '10-12', '12-14'


@define
class TimeIntervals(UserList):
    data: list[TimeInterval]
    _names: list[str] = field(init=False, default=None)


    @property
    def names(self) -> list[str]:
        return [time_interval.name for time_interval in self.data]


@define
class Weekday:
    """This class describes a weekday."""
    name: str


@define
class Weekdays(UserList):
    """This class describes a weekday."""
    data: list[Weekday]
    _names: list[str] = field(init=False, default=None)


    @property
    def names(self) -> list[str]:
        return [weekday.name for weekday in self.data]


@define
class Timetable:
    weekday: list[Weekday]


@define
class ObjectCreator:
    """This class will be used to create objects using the dictionary created with the HTMLElementsToJson class."""
    timetable: dict = field(factory=dict)
    

    def get_time_intervals(self) -> TimeIntervals:
        time_intervals = self.timetable['LUNI']
        return TimeIntervals([TimeInterval(time_interval) for time_interval in time_intervals])
    

    def get_weekdays(self) -> Weekdays:
        return Weekdays([Weekday(weekday) for weekday in self.timetable])
    

    def get_all_unique(self, aggregate_object: type, timetable_key: str) -> type:
        unique = aggregate_object()
        for time_intervals in self.timetable.values():
            for v in time_intervals.values():
                for objects in v[timetable_key]:
                    for object_ in objects:
                        if object_.name not in unique.names:
                            unique.append(object_)
        return unique
