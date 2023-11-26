import os

from PyQt6.QtWidgets import (
    QDialog,
)
from PyQt6 import uic



UI = os.path.join(os.path.dirname(__file__), 'main.ui')


class Main(QDialog):


    def __init__(self):
        super(Main, self).__init__()
        uic.loadUi(UI, self)
        
