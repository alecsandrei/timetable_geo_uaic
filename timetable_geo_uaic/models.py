from __future__ import annotations

from collections import OrderedDict

from attrs import define, field
from PyQt6.QtWidgets import (
    QHeaderView,
    QComboBox,
)

from .ui.dialog import Main
from .objects import (
    Weekdays,
    TimeIntervals,
    Group,
    Groups,
    Professors,
    Rooms,
    Subjects,
    ObjectCreator
)
from .utils.pyqt_utils import (
    combobox_add_completer,
    create_scroll_label,
    create_tab_widget,
    CheckableComboBox
)
from .utils.utils import (
    Table,
    HTMLTableParser,
    HTMLElementsToJson,
    JsonToObjects,
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


    def __attrs_post_init__(self) -> None:
        self.ui.__init__()
        self.ui = Main()
        self.comboBox_lectures = OrderedDict(
            groups=self.ui.comboBoxGroup,
            professors=self.ui.comboBoxProfessor,
            rooms=self.ui.comboBoxRoom,
            subjects=self.ui.comboBoxSubject
        )
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
        self.add_comboBox_signals()
        # Signals for push buttons
        self.ui.pushButtonDownloadTimetable.pressed.connect(self.load_table)
        self.ui.pushButtonResetGroup.pressed.connect(self.reset_comboBoxGroup)
        self.ui.pushButtonResetProfessor.pressed.connect(self.reset_comboBoxProfessor)
        self.ui.pushButtonResetRoom.pressed.connect(self.reset_comboBoxRoom)
        self.ui.pushButtonResetSubject.pressed.connect(self.reset_comboBoxSubject)
        # Signals for check box
        self.ui.checkBoxCheckOverlaps.stateChanged.connect(self.handle_checkBoxCheckOverlaps)


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
        return self.creator.get_all_unique(aggregate_object=Groups, timetable_key='groups')
    

    @property
    def professors(self) -> Professors:
        return self.creator.get_all_unique(aggregate_object=Professors, timetable_key='professors')
    

    @property
    def rooms(self) -> Rooms:
        return self.creator.get_all_unique(aggregate_object=Rooms, timetable_key='rooms')
    
    
    @property
    def subjects(self) -> Subjects:
        return self.creator.get_all_unique(aggregate_object=Subjects, timetable_key='subjects')


    @property
    def table_parser(self) -> Table:
        years = self.ui.lineEditYears.text().strip()
        semester = self.ui.lineEditSemester.text().strip()
        if not years or not semester:
            return Table()
        return Table(years=years.split('-'), semester=semester)

    @staticmethod
    def filter_by_iterable_object(timetable: dict, comboBox_lecture: str, timetable_key: str) -> dict:
        filtered = {}
        for weekday, intervals in timetable.items():
            filtered[weekday] = {k: {} for k in intervals}
            for interval, lectures in intervals.items():
                filtered[weekday][interval] = {k: [] for k in lectures}
                lecture_objects = lectures[timetable_key]
                for i, objects in enumerate(lecture_objects):
                    if any(x in objects for x in comboBox_lecture):
                        filtered[weekday][interval]['groups'] += [lectures['groups'][i]]
                        filtered[weekday][interval]['professors'] += [lectures['professors'][i]]
                        filtered[weekday][interval]['rooms'] += [lectures['rooms'][i]]
                        filtered[weekday][interval]['subjects'] += [lectures['subjects'][i]]
        return filtered


    def load_table(self, download=True, update_table=True) -> None:
        parser = HTMLTableParser(table=self.table_parser)
        self.html_elements_to_json = HTMLElementsToJson(parser=parser)
        if download:
            self.html_elements_to_json.save_json()
        json = self.html_elements_to_json.read_json()
        self.timetable = JsonToObjects(json).convert_timetable()
        self.creator = ObjectCreator(self.timetable)
        if update_table:
            self.update_tableWidgetMain()
            self.add_lecture_objects_to_comboBox()
            self.style_comboBox_completer()
        

    def convert_combobox_to(self, object_: QComboBox | CheckableComboBox):
        layout = self.ui.frameFilters.layout()
        for lecture_element, comboBox in self.comboBox_lectures.items():
            self.comboBox_lectures[lecture_element] = object_()
            layout.replaceWidget(comboBox, self.comboBox_lectures[lecture_element])
            comboBox.close()


    def add_groups_to_comboBoxGroup(self) -> None:
        # only add non-aggretate type group to combobox
        items = [group.name for group in self.groups if not group.aggregate]
        self.comboBox_lectures['groups'].addItems(items)
        

    def add_professors_to_comboBoxProfessor(self) -> None:
        items = [professor.name for professor in self.professors]
        self.comboBox_lectures['professors'].addItems(items)


    def add_rooms_to_comboBoxRoom(self) -> None:
        items = [room.name for room in self.rooms]
        self.comboBox_lectures['rooms'].addItems(items)


    def add_subjects_to_comboBoxSubject(self) -> None:
        items = sorted(list({subject.timetable_name for subject in self.subjects}))
        self.comboBox_lectures['subjects'].addItems(items)


    def clear_lecture_objects_from_comboBox(self) -> None:
        for comboBox in self.comboBox_lectures.values():
            comboBox.clear()


    def add_lecture_objects_to_comboBox(self) -> None:
        self.clear_lecture_objects_from_comboBox() # first clear the contents of the comboboxes
        self.add_groups_to_comboBoxGroup()
        self.add_professors_to_comboBoxProfessor()
        self.add_rooms_to_comboBoxRoom()
        self.add_subjects_to_comboBoxSubject()


    def add_comboBox_signals(self):
        for comboBox in self.comboBox_lectures.values():
            if isinstance(comboBox, CheckableComboBox):
                comboBox.currentTextChanged.connect(self.update_tableWidgetMain)
            elif isinstance(comboBox, QComboBox):
                comboBox.activated.connect(self.update_tableWidgetMain)


    def reset_comboBoxGroup(self) -> None:
        if isinstance(self.comboBox_lectures['groups'], CheckableComboBox):
            self.comboBox_lectures['groups'].deselect_items()
        combobox_add_completer(self.comboBox_lectures['groups'])
        self.update_tableWidgetMain()


    def reset_comboBoxProfessor(self) -> None:
        if isinstance(self.comboBox_lectures['professors'], CheckableComboBox):
            self.comboBox_lectures['professors'].deselect_items()
        combobox_add_completer(self.comboBox_lectures['professors'])
        self.update_tableWidgetMain()


    def reset_comboBoxRoom(self) -> None:
        if isinstance(self.comboBox_lectures['rooms'], CheckableComboBox):
            self.comboBox_lectures['rooms'].deselect_items()
        combobox_add_completer(self.comboBox_lectures['rooms'])
        self.update_tableWidgetMain()


    def reset_comboBoxSubject(self) -> None:
        if isinstance(self.comboBox_lectures['subjects'], CheckableComboBox):
            self.comboBox_lectures['subjects'].deselect_items()
        combobox_add_completer(self.comboBox_lectures['subjects'])
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
        for comboBox in self.comboBox_lectures.values():
            combobox_add_completer(comboBox)


    def add_weekdays_to_tableWidgetMain(self) -> None:
        self.ui.tableWidgetMain.setHorizontalHeaderLabels(self.weekdays)


    def add_time_intervals_to_tableWidgetMain(self) -> None:
        self.ui.tableWidgetMain.setVerticalHeaderLabels(self.time_intervals)


    def add_scroll_label_to_tableWidgetMain_cells(self, filtered_timetable: dict) -> None:
        for c, day in enumerate(self.weekdays):
            for r, interval in enumerate(self.time_intervals):
                cell_widget_w_tabs = create_tab_widget()
                self.ui.tableWidgetMain.setCellWidget(r, c, cell_widget_w_tabs)
                for v in filtered_timetable[day][interval].values():
                    if not v:
                        continue
                    for i, lecture in enumerate(v):
                        text = ', '.join(lecture.names)
                        if not isinstance(lecture, Subjects):
                            text += '\n'
                        if cell_widget_w_tabs.count() < i+1:
                            cell_widget_w_tabs.addTab(create_scroll_label(), str(i))
                        label = cell_widget_w_tabs.widget(i)
                        label.setText(label.text() + text)


    def get_comboBox_lectures_current_data(self) -> list[str] | None:
        for combobox in self.comboBox_lectures.values():
            if isinstance(combobox, CheckableComboBox):
                yield combobox.currentData()
            elif isinstance(combobox, QComboBox):
                text = combobox.currentText()
                yield [text] if text else None


    def update_tableWidgetMain(self) -> None:
        filtered_timetable = self.timetable.copy()
        for lecture_element, timetable_key in zip(self.get_comboBox_lectures_current_data(), self.comboBox_lectures):
            if not lecture_element:
                continue
            filtered_timetable = self.filter_by_iterable_object(timetable=filtered_timetable, comboBox_lecture=lecture_element, timetable_key=timetable_key)
        self.add_scroll_label_to_tableWidgetMain_cells(filtered_timetable=filtered_timetable)


    def handle_checkBoxCheckOverlaps(self) -> None:
        if self.ui.checkBoxCheckOverlaps.isChecked():
            self.convert_combobox_to(object_=CheckableComboBox)
        else:
            self.convert_combobox_to(object_=QComboBox)
        self.add_lecture_objects_to_comboBox()
        self.add_comboBox_signals()
        self.style_comboBox_completer()
