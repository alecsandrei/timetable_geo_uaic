from PyQt6.QtWidgets import QApplication

from timetable_geo_uaic.models import VerticalTimeHorizontalDays



def main():
    app = QApplication([])
    model = VerticalTimeHorizontalDays()
    window = model.ui
    window.show()
    app.exec()


if __name__ == '__main__':
    main()