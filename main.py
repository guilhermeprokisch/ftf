import os
import re
import sys
import termios
import tty
from pathlib import Path


def get_nerdfont_icon(file_name):
    icon_mapping = {
        ".txt": "\uF15C",  # File icon
        ".jpg": "\uF1C5",  # Image icon
        ".png": "\uF1C5",  # Image icon
        ".doc": "\uF1C2",  # Word icon
        ".docx": "\uF1C2",  # Word icon
        ".pdf": "\uF1C1",  # PDF icon
        ".xls": "\uF1C3",  # Excel icon
        ".xlsx": "\uF1C3",  # Excel icon
        ".ppt": "\uF1C4",  # PowerPoint icon
        ".pptx": "\uF1C4",  # PowerPoint icon
        ".mp3": "\uF001",  # Music icon
        ".mp4": "\uF008",  # Video icon
        ".zip": "\uF1C6",  # Archive icon
        ".rar": "\uF1C6",  # Archive icon
        ".tar": "\uF1C6",  # Archive icon
        ".gz": "\uF1C6",  # Archive icon
        ".7z": "\uF1C6",  # Archive icon
        ".exe": "\uF013",  # Executable icon
        ".py": "\uF2C8",  # Python icon
        ".java": "\uF17E",  # Java icon
        ".html": "\uF13B",  # HTML icon
        ".css": "\uF13C",  # CSS icon
        ".js": "\uF3B8",  # JavaScript icon
        ".json": "\uF3C9",  # JSON icon
        # Add more mappings as needed
    }

    extension = file_name[file_name.rfind(".") :]  # Extract the file extension
    return icon_mapping.get(
        extension.lower(), "\uF016"
    )  # Return the corresponding icon or default icon


def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return ord(sys.stdin.read(1))
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


class Cursor:
    def __init__(self):
        # self.initial_positon = self.get_inital_positon()
        self.initial_positon = (0, 0)
        self.x = self.initial_positon[0]
        self.y = self.initial_positon[1]

    def move_up(self, lines=1):
        if lines > 0:
            sys.stdout.write(f"\033[{lines}A")
            self.y -= lines

    def move_down(self, lines=1):
        if lines > 0:
            sys.stdout.write(f"\033[{lines}B")
            self.y += lines

    def move_left(self, columns=1):
        if columns > 0:
            sys.stdout.write(f"\033[{columns}D")
            self.x -= columns

    def move_right(self, columns=1):
        if columns > 0:
            sys.stdout.write(f"\033[{columns}C")
            self.x += columns

    def move_to(self, x, y):
        if x >= 0 and y >= 0:
            sys.stdout.write(f"\033[{y+1};{x+1}H")
            self.x = x
            self.y = y

    def move_to_initial_position(self):
        current_x, current_y = self.initial_positon
        self.move_to(current_x, current_y)  # Move the cursor to the current position

    def get_inital_positon(self):
        OldStdinMode = termios.tcgetattr(sys.stdin)
        _ = termios.tcgetattr(sys.stdin)
        _[3] = _[3] & ~(termios.ECHO | termios.ICANON)
        termios.tcsetattr(sys.stdin, termios.TCSAFLUSH, _)
        try:
            _ = ""
            sys.stdout.write("\x1b[6n")
            sys.stdout.flush()
            while not (_ := _ + sys.stdin.read(1)).endswith("R"):
                pass
            res = re.match(r".*\[(?P<y>\d*);(?P<x>\d*)R", _)
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSAFLUSH, OldStdinMode)
        if res:
            return (int(res.group("x")) - 1, int(res.group("y")) - 2)
        return (-1, -1)


class FileSelector:
    def __init__(self, directory="."):
        self.root_directory = os.path.abspath(directory)
        self.length = 0
        self.tree = ["."]
        self.add_itens(
            [
                f"{self.get_absolute_path(file)}"
                for file in os.listdir(self.root_directory)
            ]
        )
        self.selected_indices = []  # Store the indices of selected files
        self.cursor = Cursor()

    def indicator(self):
        return "\33[2K\r\u001b[31m>\u001b[0m"

    def pick_indicator(self):
        return "\u001b[33m*\u001b[0m "

    def indent(self, item, is_selected, is_picked):
        if item == ".":
            return ""
        item_relative_path = self.get_relative_path(item)
        if not is_selected and not is_picked:
            return " " * (item_relative_path.count(os.sep) + 2)
        if is_selected and not is_picked:
            return " " * (item_relative_path.count(os.sep) + 1)
        if is_selected and is_picked:
            return " " * (item_relative_path.count(os.sep) - 1)
        if not is_selected and is_picked:
            return " " * (item_relative_path.count(os.sep))

    def change_root(self, directory):
        self.root_directory = directory
        self.length = 0
        self.tree = [self.root_directory]
        self.add_itens(
            [f"{self.get_absolute_path(file)}" for file in os.listdir(directory)]
        )
        self.selected_indices = []

    def get_relative_path(self, item):
        relative_path = os.path.relpath(os.path.abspath(item), self.root_directory)
        return f"./{relative_path}"

    def get_absolute_path(self, item):
        return f"{self.root_directory}/{item}"

    def display_files(self):
        self.clean_display()
        for index, item in enumerate(self.tree):
            is_selected = index == self.current_index
            is_picked = index in self.selected_indices
            indent = self.indent(item, is_selected, is_picked)

            if item == ".":
                display_name = os.path.basename(os.path.abspath(self.root_directory))
            else:
                display_name = os.path.basename(item)
            if os.path.isdir(item):
                display_name = "\u001b[34m " + display_name
            else:
                display_name = get_nerdfont_icon(item) + " " + display_name

            if is_selected and is_picked:
                print(
                    f"{self.indicator()}{indent}{self.pick_indicator()}\u001b[7m{display_name}\u001b[0m\u001b[0m"
                )
            if is_selected and not is_picked:
                print(
                    f"{self.indicator()}{indent}\u001b[7m{display_name}\u001b[0m\u001b[0m"
                )
            if not is_selected and is_picked:
                print(f"\33[2K\r{indent}{self.pick_indicator()}{display_name}\u001b[0m")
            if not is_selected and not is_picked:
                print(f"\33[2K\r{indent}{display_name}\u001b[0m")

    def clean_display(self):
        self.cursor.move_to_initial_position()
        print(self.length * "\33[2K\r\n")
        self.cursor.move_to_initial_position()

    def add_itens(self, files):
        self.tree.extend(files)
        self.tree = list(set(self.tree))
        self.tree.sort()
        if self.length < len(self.tree):
            self.length = len(self.tree)

    def toggle_file_selection(self):
        if self.current_index in self.selected_indices:
            self.selected_indices.remove(self.current_index)
        else:
            self.selected_indices.append(self.current_index)

    def move_cursor_up(self):
        if self.current_index > 0:
            self.current_index -= 1
        self.cursor.move_up()

    @property
    def current_item(self):
        return self.tree[self.current_index]

    def move_cursor_down(self):
        if self.current_index < len(self.tree) - 1:
            self.current_index += 1
        self.cursor.move_down()

    def add_selected_contents(self):
        selected = self.tree[self.current_index]
        selected_path = os.path.join(self.root_directory, selected)
        if os.path.isdir(selected_path):
            new_files = [f"{selected}/{item}" for item in os.listdir(selected_path)]
            self.add_itens(new_files)

    def remove_selected_folder_contents(self):
        selected = self.tree[self.current_index]
        selected_path = os.path.join(self.root_directory, selected)

        if os.path.isdir(selected_path):
            self.tree = [
                item for item in self.tree if not item.startswith(f"{selected}/")
            ]

    def return_dir(self):
        self.set_root(Path(self.root_directory).parent.absolute())

    def set_root(self, path):
        self.clean_display()
        if os.path.isdir(path):
            self.root_directory = Path(path).absolute()
            self.length = 0
            self.tree = ["."]
            self.add_itens(
                [
                    f"{self.get_absolute_path(item)}"
                    for item in os.listdir(self.root_directory)
                ]
            )
            self.selected_indices = []
            self.current_index = 1

    def run(self):
        self.current_index = 1  # Initialize the selected index
        while True:
            self.display_files()
            char = getch()
            # print("\33[2K\r", char)
            if char == 106:
                self.move_cursor_down()
            elif char == 107:
                self.move_cursor_up()
            elif char == 108:
                self.add_selected_contents()
            elif char == 76:
                self.set_root(self.tree[self.current_index])
            elif char == 104:
                self.remove_selected_folder_contents()
            elif char == 72:
                self.return_dir()
            elif char == 32:  # Spacebar
                self.toggle_file_selection()
            elif char in [27, 113]:
                return
            elif char in {10, 13}:  # Enter key
                break

        selected_files = [self.tree[index] for index in self.selected_indices]
        if not selected_files:
            selected_files = [self.current_item]
        return selected_files


if __name__ == "__main__":
    selector = FileSelector(directory=".")

    # selected_files = ["Hello"]
    selected_files = selector.run()

    # Print the selected file(s)
    for file in selected_files:
        print(file)
