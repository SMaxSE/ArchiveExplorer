import sys

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtWidgets import QGridLayout
from PyQt6.QtWidgets import QLabel
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtWidgets import QProgressBar
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtWidgets import QSizePolicy
from PyQt6.QtWidgets import QTreeWidget
from PyQt6.QtWidgets import QWidget

from extensions.arc import ARC


class ArchiveExplorer:
    def __init__(self) -> None:
        self.__application = QApplication(sys.argv)
        self.__window = QMainWindow()
        self.__widget = QWidget(self.__window)
        self.__layout = QGridLayout(self.__widget)
        self.__open_button = QPushButton(self.__widget)
        self.__unpack_button = QPushButton(self.__widget)
        self.__repack_button = QPushButton(self.__widget)
        self.__current_file_label = QLabel(self.__widget)
        self.__all_files_label = QLabel(self.__widget)
        self.__current_file_progress_bar = QProgressBar(self.__widget)
        self.__all_files_progress_bar = QProgressBar(self.__widget)
        self.__file_tree_widget = QTreeWidget(self.__widget)
        self.__widget.setLayout(self.__layout)
        self.__window.setCentralWidget(self.__widget)
        self.__layout.addWidget(self.__open_button, 0, 0, 1, 1)
        self.__layout.addWidget(self.__unpack_button, 0, 1, 1, 1)
        self.__layout.addWidget(self.__repack_button, 0, 2, 1, 2)
        self.__layout.addWidget(self.__file_tree_widget, 1, 0, 1, 4)
        self.__layout.addWidget(self.__current_file_label, 2, 0, 1, 1)
        self.__layout.addWidget(self.__all_files_label, 3, 0, 1, 1)
        self.__layout.addWidget(self.__current_file_progress_bar, 2, 1, 1, 3)
        self.__layout.addWidget(self.__all_files_progress_bar, 3, 1, 1, 3)
        self.__open_button.setIcon(QIcon("files\\icons\\openButtonIcon.png"))
        self.__unpack_button.setIcon(QIcon("files\\icons\\unpackButtonIcon.png"))
        self.__repack_button.setIcon(QIcon("files\\icons\\repackButtonIcon.png"))
        self.__open_button.setIconSize(QSize(25, 25))
        self.__unpack_button.setIconSize(QSize(25, 25))
        self.__repack_button.setIconSize(QSize(25, 25))
        self.__open_button.setMinimumSize(150, 30)
        self.__unpack_button.setMinimumSize(150, 30)
        self.__repack_button.setMinimumSize(150, 30)
        self.__open_button.setMaximumSize(150, 30)
        self.__unpack_button.setMaximumSize(150, 30)
        self.__repack_button.setMaximumSize(150, 30)
        self.__open_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.__unpack_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.__repack_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.__open_button.clicked.connect(self.__on_open_button_click)
        self.__unpack_button.clicked.connect(self.__on_unpack_button_click)
        self.__file_tree_widget.setHeaderLabel("")
        self.__current_file_progress_bar.setTextVisible(False)
        self.__all_files_progress_bar.setTextVisible(False)
        self.__current_file_label.setText("Current file load:")
        self.__all_files_label.setText("All files load:")
        self.__files = []
        self.__window.show()
        sys.exit(self.__application.exec())

    def __on_open_button_click(self) -> None:
        files = QFileDialog.getOpenFileNames(None, "Select files", "C:\\", "Lost Planet (*.arc)")
        for i, file in enumerate(files[0]):
            if files[1] == "Lost Planet (*.arc)":
                self.__files.append(ARC(file))
            self.__files[i].open(self.__file_tree_widget)

    def __on_unpack_button_click(self) -> None:
        folder = QFileDialog.getExistingDirectory(None, "Select folder:", "C:\\", QFileDialog.ShowDirsOnly)
        for file in self.__files:
            file.unpack(folder)
