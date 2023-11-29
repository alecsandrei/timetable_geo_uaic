import os
from pathlib import Path
import sys


def resource_path(relative_path: Path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS2
    except Exception:
        base_path = Path('.').absolute()
        base_path = os.path.abspath(".")

    return (base_path / relative_path).as_posix()


DIALOG_ICON = resource_path(Path('timetable_geo_uaic/ui/icon.png'))
MAIN_UI = resource_path(Path('timetable_geo_uaic/ui/main.ui'))
TIMETABLE = resource_path(Path('timetable_geo_uaic/timetable.json'))

