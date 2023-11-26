from __future__ import annotations

from typing import Iterable

from attrs import define, field
from PyQt6.QtWidgets import (
    QHeaderView,
    QComboBox,
)

from ui.dialog import Main
from objects import (
    Weekdays,
    TimeIntervals,
    Group,
    Professor,
    Room,
    Subject,
    Groups,
    Professors,
    Rooms,
    Subjects,
    ObjectCreator
)
from timetable_geo_uaic.utils.pyqt_utils import (
    combobox_add_completer,
    create_scroll_label,
    create_tab_widget,
    CheckableComboBox
)
from timetable_geo_uaic.utils.utils import (
    HTMLTableParser,
    HTMLElementsToJson,
    JsonToObjects,
    get_attribute_name
)


@define
class VerticalTimeHorizontalDays:
    row_count: int = 6
    column_count: int = 5
    html_elements_to_json: HTMLElementsToJson = field(init=False)
    json_to_objects: JsonToObjects = field(init=False)
    creator: ObjectCreator = field(init=False)
    timetable: dict = field(factory=dict, init=False)
    ui: Main = field(init=False, default=None)
    comboBox_lectures: dict[str, QComboBox] = field(init=False)
    _weekdays: Weekdays = field(init=False, default=None)
    _time_intervals: TimeIntervals = field(init=False, default=None)
    _group: Group = field(init=False, default=None)
    _groups: Groups = field(init=False, default=None)
    _professors: Professors = field(init=False, default=None)
    _rooms: Rooms = field(init=False, default=None)
    _subjects: Subjects = field(init=False, default=None)


    def __attrs_post_init__(self) -> None:
        self.ui.__init__()
        self.ui = Main()
        # self.comboBox_lectures = {
        #     'groups': self.ui.comboBoxGroup,
        #     'professors': self.ui.comboBoxProfessor,
        #     'rooms': self.ui.comboBoxRoom,
        #     'subjects': self.ui.comboBoxSubject
        # }
        # Populate dialog
        self.load_table(download=False, update_table=False)
        self.style_tableWidgetMain_row_col_count()
        self.style_tableWidgetMain_stretch()
        self.add_weekdays_to_tableWidgetMain()
        self.add_time_intervals_to_tableWidgetMain()
        self.add_lecture_objects_to_comboBox()
        self.style_comboBox_completer()
        self.update_tableWidgetMain()
        # Signals for comboboxes
        self.ui.comboBoxGroup.activated.connect(self.update_tableWidgetMain)
        self.ui.comboBoxProfessor.activated.connect(self.update_tableWidgetMain)
        self.ui.comboBoxRoom.activated.connect(self.update_tableWidgetMain)
        self.ui.comboBoxSubject.activated.connect(self.update_tableWidgetMain)
        # Signals for push buttons
        self.ui.pushButtonDownloadTimetable.pressed.connect(self.load_table)
        self.ui.pushButtonResetGroup.pressed.connect(self.reset_comboBoxGroup)
        self.ui.pushButtonResetProfessor.pressed.connect(self.reset_comboBoxProfessor)
        self.ui.pushButtonResetRoom.pressed.connect(self.reset_comboBoxRoom)
        self.ui.pushButtonResetSubject.pressed.connect(self.reset_comboBoxSubject)
        # Signals for check box
        # self.ui.checkBoxCheckOverlaps.stateChanged.connect(self.handle_checkBoxCheckOverlaps)


    @property
    def weekdays(self) -> Weekdays:
        if self._weekdays is None:
            self._weekdays = self.creator.get_weekdays().names
        return self._weekdays
    

    @property
    def time_intervals(self) -> TimeIntervals:
        if self._time_intervals is None:
            self._time_intervals = self.creator.get_time_intervals().names
        return self._time_intervals
    

    @property
    def groups(self) -> Groups:
        if self._groups is None:
            self._groups = self.creator.get_all_unique(aggregate_object=Groups, timetable_key='groups')
        return self._groups
    

    @property
    def professors(self) -> Professors:
        if self._professors is None:
            self._professors = self.creator.get_all_unique(aggregate_object=Professors, timetable_key='professors')
        return self._professors
    

    @property
    def rooms(self) -> Rooms:
        if self._rooms is None:
            self._rooms = self.creator.get_all_unique(aggregate_object=Rooms, timetable_key='rooms')
        return self._rooms
    
    
    @property
    def subjects(self) -> Subjects:
        if self._subjects is None:
            self._subjects = self.creator.get_all_unique(aggregate_object=Subjects, timetable_key='subjects')
        return self._subjects


    @property
    def comboBoxGroup_text_to_object(self) -> Group:
        """Gets the current text in the combobox widget."""
        text = self.ui.comboBoxGroup.currentText()
        if text in self.groups.names:
            return Group(str(text))
    

    @property
    def comboBoxProfessor_text_to_object(self) -> Professor:
        """Gets the current text in the combobox widget."""
        text = self.ui.comboBoxProfessor.currentText()
        if text in self.professors.names:
            return Professor(str(text))
    

    @property
    def comboBoxRoom_text_to_object(self) -> Room:
        """Gets the current text in the combobox widget."""
        text = self.ui.comboBoxRoom.currentText()
        if text in self.rooms.names:
            return Room(str(text))
    

    @property
    def comboBoxSubject_text_to_object(self) -> Subject:
        """Gets the current group in the combobox widget."""
        text = self.ui.comboBoxSubject.currentText()
        if text in self.subjects.names:
            return Subject(str(text))


    @staticmethod
    def filter_by_iterable_object(timetable: dict, objects: Iterable[type], timetable_key: str) -> dict:
        filtered = {}
        for weekday, intervals in timetable.items():
            filtered[weekday] = {k: {} for k in intervals}
            for interval, lectures in intervals.items():
                filtered[weekday][interval] = {k: [] for k in lectures}
                lecture_objects = lectures[timetable_key]
                for i, object_ in enumerate(lecture_objects):
                    if any(x.name in object_.names for x in objects):
                        filtered[weekday][interval]['groups'] += [lectures['groups'][i]]
                        filtered[weekday][interval]['professors'] += [lectures['professors'][i]]
                        filtered[weekday][interval]['rooms'] += [lectures['rooms'][i]]
                        filtered[weekday][interval]['subjects'] += [lectures['subjects'][i]]
        return filtered


    def load_table(self, download=True, update_table=True) -> None:
        parser = HTMLTableParser()
        self.html_elements_to_json = HTMLElementsToJson(parser=parser)
        if download:
            self.html_elements_to_json.save_json()
        json = self.html_elements_to_json.read_json()
        self.timetable = JsonToObjects(json).convert_timetable()
        self.creator = ObjectCreator(self.timetable)
        if update_table:
            self.update_tableWidgetMain()


    def comboBox_lectures_to_checkableComboBox(self):
        pass


    def checkableComboBox_lectures_to_comboBox(self):
        pass


    def add_groups_to_comboBoxGroup(self) -> None:
        # only add non-aggretate type group to combobox
        items = [group.name for group in self.groups if not group.aggregate]
        self.ui.comboBoxGroup.addItems(items)
        

    def add_professors_to_comboBoxProfessor(self) -> None:
        items = [professor.name for professor in self.professors]
        self.ui.comboBoxProfessor.addItems(items)


    def add_rooms_to_comboBoxRoom(self) -> None:
        items = [room.name for room in self.rooms]
        self.ui.comboBoxRoom.addItems(items)


    def add_subjects_to_comboBoxSubject(self) -> None:
        items = [group.name for group in self.subjects]
        self.ui.comboBoxSubject.addItems(items)


    def add_lecture_objects_to_comboBox(self) -> None:
        self.add_groups_to_comboBoxGroup()
        self.add_professors_to_comboBoxProfessor()
        self.add_rooms_to_comboBoxRoom()
        self.add_subjects_to_comboBoxSubject()


    def reset_comboBoxGroup(self) -> None:
        combobox_add_completer(self.ui.comboBoxGroup)
        self.update_tableWidgetMain()


    def reset_comboBoxProfessor(self) -> None:
        combobox_add_completer(self.ui.comboBoxProfessor)
        self.update_tableWidgetMain()


    def reset_comboBoxRoom(self) -> None:
        combobox_add_completer(self.ui.comboBoxRoom)
        self.update_tableWidgetMain()


    def reset_comboBoxSubject(self) -> None:
        combobox_add_completer(self.ui.comboBoxSubject)
        self.update_tableWidgetMain()


    def style_tableWidgetMain_row_col_count(self) -> None:
        self.ui.tableWidgetMain.setRowCount(self.row_count)
        self.ui.tableWidgetMain.setColumnCount(self.column_count)


    def style_tableWidgetMain_stretch(self) -> None:
        h_header = self.ui.tableWidgetMain.horizontalHeader()
        v_header = self.ui.tableWidgetMain.verticalHeader()    
        for i in range(self.row_count):
            v_header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        for i in range(self.column_count):
            h_header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)


    def style_comboBox_completer(self) -> None:
        combobox_add_completer(self.ui.comboBoxGroup)
        combobox_add_completer(self.ui.comboBoxProfessor)
        combobox_add_completer(self.ui.comboBoxRoom)
        combobox_add_completer(self.ui.comboBoxSubject)


    def add_weekdays_to_tableWidgetMain(self) -> None:
        self.ui.tableWidgetMain.setHorizontalHeaderLabels(self.weekdays)


    def add_time_intervals_to_tableWidgetMain(self) -> None:
        self.ui.tableWidgetMain.setVerticalHeaderLabels(self.time_intervals)


    def add_scroll_label_to_tableWidgetMain_cells(self, filtered_timetable: dict) -> None:
        for c, day in enumerate(self.weekdays):
            for r, interval in enumerate(self.time_intervals):
                cell_widget_w_tabs = create_tab_widget()
                self.ui.tableWidgetMain.setCellWidget(r, c, cell_widget_w_tabs)
                for i, v in enumerate(filtered_timetable[day][interval].values()):
                    if not v:
                        continue
                    for i, lecture in enumerate(v):
                        text = ', '.join(lecture.names) + '\n'
                        if cell_widget_w_tabs.count() < i+1:
                            cell_widget_w_tabs.addTab(create_scroll_label(), str(i))
                        label = cell_widget_w_tabs.widget(i)
                        label.setText(label.text() + text)


    def update_tableWidgetMain(self) -> None:
        group_object = [self.comboBoxGroup_text_to_object]
        professor_object =  [self.comboBoxProfessor_text_to_object]
        room_object = [self.comboBoxRoom_text_to_object]
        subject_object = [self.comboBoxSubject_text_to_object]
        filtered_timetable = self.timetable.copy()
        for objects, timetable_key in zip([group_object, professor_object, room_object, subject_object],
                                          ['groups', 'professors', 'rooms', 'subjects']):
            if None in objects:
                continue
            if timetable_key == 'groups':
                objects = self.groups.get_belonging_groups(objects[0])
            filtered_timetable = self.filter_by_iterable_object(timetable=filtered_timetable, objects=objects, timetable_key=timetable_key)
            print(filtered_timetable)
        self.add_scroll_label_to_tableWidgetMain_cells(filtered_timetable=filtered_timetable)

    def handle_checkBoxCheckOverlaps(self) -> None:
        if self.ui.checkBoxCheckOverlaps.isChecked():
            self.comboBox_lectures_to_checkableComboBox()
        else:
            self.checkableComboBox_lectures_to_comboBox()
        self.add_lecture_objects_to_comboBox()
