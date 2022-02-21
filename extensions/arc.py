import io
import os
import zlib

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QTreeWidget
from PyQt6.QtWidgets import QTreeWidgetItem


class ARC:
    class __Header:
        def __init__(self, arc_stream: io.BufferedReader) -> None:
            self.__arc_stream = arc_stream
            self.__size = 8
            self.__whence = 0
            self.__read()

        def __read_stream(self, offset: int, size: int) -> bytes:
            self.__arc_stream.seek(offset, self.__whence)
            return self.__arc_stream.read(size)

        def __get_name(self) -> str:
            offset = 0
            size = 4
            return self.__read_stream(offset, size).strip(b"\x00").decode("utf-8")

        def __get_version(self) -> int:
            offset = 4
            size = 2
            return int.from_bytes(self.__read_stream(offset, size), "little")

        def __get_file_count(self) -> int:
            offset = 6
            size = 2
            return int.from_bytes(self.__read_stream(offset, size), "little")

        def __read(self) -> None:
            self.__name = self.__get_name()
            self.__version = self.__get_version()
            self.__file_count = self.__get_file_count()

        def get_name(self) -> str:
            return self.__name

        def get_version(self) -> int:
            return self.__version

        def get_file_count(self) -> int:
            return self.__file_count

        def get_size(self) -> int:
            return self.__size

    class __File:
        def __init__(self, number: int, arc_name: str, arc_stream: io.BufferedReader, arc_header_size: int):
            self.__number = number
            self.__arc_name = arc_name
            self.__arc_stream = arc_stream
            self.__size = 80
            self.__whence = 0
            self.__offset_directory = arc_header_size + self.__size * self.__number
            self.__extensions = {
                1018003574: "tex",
                1156029294: "sdl",
                667850998: "rtx",
                883475283: "xfs",
                2047053644: "xfs",
                1815824644: "xfs",
                1471865736: "xfs",
                864821228: "xfs",
                1414542962: "xfs",
                776455971: "xfs",
                222029749: "xfs",
                1696625072: "xfs",
                731104429: "xfs",
                1010633733: "png",
                1437137716: "anm",
                272743838: "mod",
                592277764: "cdf",
                66773634: "efa",
                553864336: "arcs",
                697601978: "dnrs",
                1813848179: "sreq",
                867062535: "spac",
                1210801045: "esl",
                155808719: "scst",
                873417209: "sdst",
                941734221: "ogg",
                131436703: "strq",
                1289707753: "msg",
                1384607967: "efs",
                298329479: "obja",
                490057515: "hit",
                329180445: "lmt",
                1592916818: "lcm",
                956357328: "sbc",
                1023439125: "wed",
                1513942406: "rrd",
                1909891284: "osf",
                1311932796: "bfx",
                1412813435: "havok",
                1212519942: "seq0",
                641763256: "fca",
                1332739548: "fcp",
            }
            self.__read()

        def __read_stream(self, offset, size: int) -> bytes:
            self.__arc_stream.seek(offset, self.__whence)
            return self.__arc_stream.read(size)

        def __get_header(self) -> bytes:
            offset = self.__offset_directory
            size = 80
            return self.__read_stream(offset, size)

        def __get_path(self) -> str:
            offset = self.__offset_directory
            size = 64
            return self.__arc_name + "/" + self.__read_stream(offset, size).strip(b"\x00").decode("utf-8").replace("\\", "/")

        def __get_name(self) -> str:
            return os.path.basename(self.__get_path())

        def __get_extension(self) -> str:
            offset = 64 + self.__offset_directory
            size = 4
            extension_int = int.from_bytes(self.__read_stream(offset, size), "little")
            return self.__extensions[extension_int]

        def __get_compressed_size(self) -> int:
            offset = 68 + self.__offset_directory
            size = 4
            return int.from_bytes(self.__read_stream(offset, size), "little")

        def __get_decompressed_size(self) -> int:
            offset = 72 + self.__offset_directory
            size = 4
            return int.from_bytes(self.__read_stream(offset, size), "little") - 1073741824

        def __get_offset_data(self) -> int:
            offset = 76 + self.__offset_directory
            size = 4
            return int.from_bytes(self.__read_stream(offset, size), "little")

        def __get_data(self) -> bytes:
            offset = self.__offset_data
            size = self.__compressed_size
            return self.__read_stream(offset, size)

        def __read(self) -> None:
            self.__header = self.__get_header()
            self.__path = self.__get_path()
            self.__name = self.__get_name()
            self.__extension = self.__get_extension()
            self.__compressed_size = self.__get_compressed_size()
            self.__decompressed_size = self.__get_decompressed_size()
            self.__offset_data = self.__get_offset_data()
            self.__data = self.__get_data()
            self.__arc_stream.seek(self.__offset_directory, self.__whence)

        def get_number(self) -> int:
            return self.__number

        def get_header(self) -> bytes:
            return self.__header

        def get_path(self) -> str:
            return self.__path

        def get_name(self) -> str:
            return self.__name

        def get_extension(self) -> str:
            return self.__extension

        def get_compressed_size(self) -> int:
            return self.__compressed_size

        def get_decompressed_size(self) -> int:
            return self.__decompressed_size

        def get_offset_directory(self) -> int:
            return self.__offset_directory

        def get_offset_data(self) -> int:
            return self.__offset_data

        def get_data(self) -> bytes:
            return self.__data

    def __init__(self, path: str) -> None:
        if not isinstance(path, str):
            raise ValueError
        self.__read(path)

    def __read(self, path) -> None:
        self.__stream = open(path, "rb")
        self.__name = os.path.basename(path).split(".")[0]
        self.__header = self.__Header(self.__stream)
        self.__files = [self.__File(file, self.__name, self.__stream, self.__header.get_size()) for file in range(self.__header.get_file_count())]
        self.__stream.close()

    def __create_branches(self, tree: tuple[None, dict]) -> None:
        def __set_icon() -> None:
            icon = QIcon("files\\icons\\folderIcon.png" if part != path_len - 1 else "files\\icons\\fileIcon.png")
            branch[1][path_part][0].setIcon(0, icon)

        def __fill_columns_text() -> None:
            tree_widget_item = branch[1][path_part][0]
            current_compressed_size = int(tree_widget_item.text(2))
            current_decompressed_size = int(tree_widget_item.text(3))
            current_file_count = int(tree_widget_item.text(6))
            name = path_part
            extension = "arc" if part == 0 else "folder" if part > 0 and part < path_len - 1 else file.get_extension()
            compressed_size = str(file.get_compressed_size() + (current_compressed_size if part != path_len - 1 else 0))
            decompressed_size = str(file.get_decompressed_size() + (current_decompressed_size if part != path_len - 1 else 0))
            offset_directory = str("-" if part != path_len - 1 else file.get_offset_directory())
            offset_data = str("-" if part != path_len - 1 else file.get_offset_data())
            file_count = str("-" if part == path_len - 1 else current_file_count + 1)
            columns = [name, extension, compressed_size, decompressed_size, offset_directory, offset_data, file_count]
            for column, column_text in enumerate(columns):
                tree_widget_item.setText(column, column_text)

        for file in self.__files:
            path = file.get_path().split("/")
            path_len = len(path)
            branch = tree
            for part, path_part in enumerate(path):
                if path_part not in branch[1] or part == path_len - 1:
                    columns_text = ["", "", "0", "0", "0", "0", "0"]
                    branch[1][path_part] = (QTreeWidgetItem(branch[0], columns_text), {})
                __set_icon()
                __fill_columns_text()
                branch = branch[1][path_part]

    def __set_check_state(self, tree: tuple[None, dict]) -> None:
        tree[1][self.__name][0].setCheckState(0, Qt.CheckState.Unchecked)

    def __fill_tree(self, tree: tuple[None, dict], tree_widget: QTreeWidget) -> None:
        for item in tree[1].values():
            tree_widget.addTopLevelItem(item[0])

    def open(self, tree_widget: QTreeWidget) -> None:
        if not isinstance(tree_widget, QTreeWidget):
            raise ValueError
        header_labels = ["Name", "Type", "Compressed size", "Decompressed size", "Offset directory", "Offset data", "File count"]
        column_widths = [100, 100, 150, 150, 150, 150, 150]
        tree_widget.setHeaderLabels(header_labels)
        for column, column_width in enumerate(column_widths):
            tree_widget.setColumnWidth(column, column_width)
        self.__files.sort(key=lambda file: file.get_path())
        tree = (None, {})
        self.__create_branches(tree)
        self.__set_check_state(tree)
        self.__fill_tree(tree, tree_widget)

    def unpack(self, target_path: str) -> None:
        if not isinstance(target_path, str):
            raise ValueError
        if os.path.exists(target_path):
            for file in self.__files:
                if not os.path.exists(os.path.dirname(f"{target_path}/{file.get_path()}.{file.get_extension()}")):
                    try:
                        os.makedirs(os.path.dirname(f"{target_path}/{file.get_path()}.{file.get_extension()}"))
                    except OSError:
                        raise
                with open(f"{target_path}/{file.get_path()}.{file.get_extension()}", "wb") as f:
                    if file.get_compressed_size() > 0:
                        f.write(zlib.decompress(file.get_data()))
                    else:
                        f.write(file.get_data())
