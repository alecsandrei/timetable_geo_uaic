from __future__ import annotations

from PyQt6.QtCore import (
    Qt,
    QEvent,
)
from PyQt6.QtGui import (
    QFontMetrics,
    QStandardItem,
    QPalette,
)
from PyQt6.QtWidgets import (
    QScrollArea,
    QLabel,
    QWidget,
    QVBoxLayout,
    QComboBox,
    QCompleter,
    QTabWidget,
    QStyledItemDelegate,
    QApplication,
)



def create_tab_widget() -> QTabWidget:
    widget = QTabWidget()
    widget.setTabBarAutoHide(True)
    return widget


def create_scroll_label() -> ScrollLabel:
    return ScrollLabel()


def combobox_add_completer(combobox: QComboBox) -> None:
    combobox.setEditable(True)
    combobox.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
    combobox.completer().setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
    combobox.setCurrentIndex(-1)


class ScrollLabel(QScrollArea):
    """A scrollable label object."""
    # source code: https://www.geeksforgeeks.org/pyqt5-scrollable-label/
    # constructor
    def __init__(self) -> None:
        super(ScrollLabel, self).__init__()
        # making widget resizable
        self.setWidgetResizable(True)
        # making qwidget object
        content = QWidget(self)
        self.setWidget(content)
        # vertical box layout
        lay = QVBoxLayout(content)
        # creating label
        self.label = QLabel(content)
        # setting alignment to the text
        self.label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        # making label multi-line
        self.label.setWordWrap(True)
        # adding label to the layout
        lay.addWidget(self.label)


    def setText(self, text) -> None:
        # setting text to the label
        self.label.setText(text)


    def text(self) -> str:
        return self.label.text()


class CheckableComboBox(QComboBox):
    # source code: https://gis.stackexchange.com/questions/350148/qcombobox-multiple-selection-pyqt5
    # Subclass Delegate to increase item height
    class Delegate(QStyledItemDelegate):
        def sizeHint(self, option, index):
            size = super().sizeHint(option, index)
            size.setHeight(20)
            return size


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make the combo editable to set a custom text, but readonly
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)

        # Use custom delegate
        self.setItemDelegate(CheckableComboBox.Delegate())

        # Update the text when an item is toggled
        self.model().dataChanged.connect(self.updateText)

        # Hide and show popup when clicking the line edit
        self.lineEdit().installEventFilter(self)
        self.closeOnLineEditClick = False

        # Prevent popup from closing when clicking on an item
        self.view().viewport().installEventFilter(self)


    def resizeEvent(self, event):
        # Recompute text to elide as needed
        self.updateText()
        super().resizeEvent(event)


    def eventFilter(self, object, event):

        if object == self.lineEdit():
            if event.type() == QEvent.Type.MouseButtonRelease:
                if self.closeOnLineEditClick:
                    self.hidePopup()
                else:
                    self.showPopup()
                return True
            return False

        if object == self.view().viewport():
            if event.type() == QEvent.Type.MouseButtonRelease:
                index = self.view().indexAt(event.pos())
                item = self.model().item(index.row())

                if item.checkState() == Qt.CheckState.Checked:
                    item.setCheckState(Qt.CheckState.Unchecked)
                else:
                    item.setCheckState(Qt.CheckState.Checked)
                return True
        return False


    def showPopup(self):
        super().showPopup()
        # When the popup is displayed, a click on the lineedit should close it
        self.closeOnLineEditClick = True


    def hidePopup(self):
        super().hidePopup()
        # Used to prevent immediate reopening when clicking on the lineEdit
        self.startTimer(100)
        # Refresh the display text when closing
        self.updateText()


    def timerEvent(self, event):
        # After timeout, kill timer, and reenable click on line edit
        self.killTimer(event.timerId())
        self.closeOnLineEditClick = False


    def updateText(self):
        texts = []
        for i in range(self.model().rowCount()):
            if self.model().item(i).checkState() == Qt.CheckState.Checked:
                texts.append(self.model().item(i).text())
        text = ", ".join(texts)

        # Compute elided text (with "...")
        metrics = QFontMetrics(self.lineEdit().font())
        elidedText = metrics.elidedText(text, Qt.TextElideMode.ElideRight, self.lineEdit().width())
        self.lineEdit().setText(elidedText)


    def deselect_items(self):
        for i in range(self.model().rowCount()):
            self.model().item(i).setCheckState(Qt.CheckState.Unchecked)


    def addItem(self, text, data=None):
        item = QStandardItem()
        item.setText(text)
        if data is None:
            item.setData(text)
        else:
            item.setData(data)
        item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable)
        item.setData(Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)
        self.model().appendRow(item)


    def addItems(self, texts, datalist=None):
        for i, text in enumerate(texts):
            try:
                data = datalist[i]
            except (TypeError, IndexError):
                data = None
            self.addItem(text, data)


    def currentData(self):
        # Return the list of selected items data
        res = []
        for i in range(self.model().rowCount()):
            if self.model().item(i).checkState() == Qt.CheckState.Checked:
                res.append(self.model().item(i).data())
        return res
