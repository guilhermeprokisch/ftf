import os
import re
import shutil
import string
import sys
import termios
import tty
from pathlib import Path
from posixpath import isdir


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
    return icon_mapping.get(extension.lower(), "\uF016")


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
        self.initial_positon = self.get_inital_positon()
        self.x = self.initial_positon[0]
        self.y = self.initial_positon[1]

    def move_up(self, lines=1):
        if lines > 0:
            sys.stderr.write(f"\033[{lines}A")
            self.y -= lines

    def move_down(self, lines=1):
        if lines > 0:
            sys.stderr.write(f"\033[{lines}B")
            self.y += lines

    def move_left(self, columns=1):
        if columns > 0:
            sys.stderr.write(f"\033[{columns}D")
            self.x -= columns

    def move_right(self, columns=1):
        if columns > 0:
            sys.stderr.write(f"\033[{columns}C")
            self.x += columns

    def move_to(self, x, y):
        if x >= 0 and y >= 0:
            sys.stderr.write(f"\033[{y+1};{x+1}H")
            self.x = x
            self.y = y

    def move_to_initial_position(self):
        init_x, init_y = self.initial_positon
        self.move_to(init_x, init_y)  # Move the cursor to the current position

    def get_inital_positon(self):
        OldStdinMode = termios.tcgetattr(sys.stdin)
        _ = termios.tcgetattr(sys.stdin)
        _[3] = _[3] & ~(termios.ECHO | termios.ICANON)
        termios.tcsetattr(sys.stdin, termios.TCSAFLUSH, _)
        try:
            _ = ""
            sys.stderr.write("\x1b[6n")
            sys.stderr.flush()
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
        self.text_input = ""
        self.marked_to_delete = []
        self.marked_to_rename = []
        self.rename = {}
        self.edit_mode = False

    def indicator(self):
        if self.edit_mode:
            return "\33[2K\r\u001b[31m>\u001b[0m"
        return "\33[2K\r\u001b[34m>\u001b[0m"

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
        self.marked_to_delete = []
        self.renaming_var = ""

    def get_relative_path(self, item):
        relative_path = os.path.relpath(os.path.abspath(item), self.root_directory)
        return f"./{relative_path}"

    def get_absolute_path(self, item):
        return f"{self.root_directory}/{item}"

    def display_files(self):
        for index, item in enumerate(self.tree):
            is_selected = index == self.current_index
            is_picked = index in self.selected_indices
            indent = self.indent(item, is_selected, is_picked)

            if os.path.isdir(item):
                item_icon = "\u001b[34m "
            else:
                item_icon = get_nerdfont_icon(item)

            if item == ".":
                display_name = os.path.basename(os.path.abspath(self.root_directory))
            else:
                display_name = os.path.basename(item)
            if os.path.isdir(item):
                display_name = item_icon + display_name
            else:
                display_name = item_icon + " " + display_name

            if index in self.marked_to_delete:
                display_name = f"\u001b[9m{display_name}\u001b"

            if self.marked_to_rename and index == self.marked_to_rename[0]:
                display_name = item_icon + " " + self.text_input

            if is_selected and is_picked:
                print(
                    f"{self.indicator()}{indent}{self.pick_indicator()}\u001b[7m{display_name}\u001b[0m\u001b[0m",
                    file=sys.stderr,
                )
            if is_selected and not is_picked:
                print(
                    f"{self.indicator()}{indent}\u001b[7m{display_name}\u001b[0m\u001b[0m",
                    file=sys.stderr,
                )
            if not is_selected and is_picked:
                print(
                    f"\33[2K\r{indent}{self.pick_indicator()}{display_name}\u001b[0m",
                    file=sys.stderr,
                )
            if not is_selected and not is_picked:
                print(f"\33[2K\r{indent}{display_name}\u001b[0m", file=sys.stderr)

    def display_command(self):
        # print(":", self.command, file=sys.stderr)
        pass

    def clean_display(self):
        self.cursor.move_to_initial_position()
        print((self.length + 1) * "\33[2K\r\n", file=sys.stderr)
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

    def mark_item_to_delete(self):
        if self.current_index in self.marked_to_delete:
            self.marked_to_delete.remove(self.current_index)
            return
        self.marked_to_delete.append(self.current_index)

    def mark_item_to_rename(self):
        self.marked_to_rename.append(self.current_index)

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

    def delete_itens(self):
        for index in self.marked_to_delete:
            item = self.tree[index]
            if os.path.isdir(item):
                shutil.rmtree(item, ignore_errors=True)
                print("removed", self.get_relative_path(item), file=sys.stderr)
            else:
                os.remove(item)
                print("removed", self.get_relative_path(item), file=sys.stderr)

    def set_root(self, path):
        if os.path.isdir(path):
            self.clean_display()
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

    def toggle_edit_mode(self):
        self.edit_mode = not self.edit_mode

        if self.edit_mode == False:
            self.rename_items()
            self.text_input = ""
            self.marked_to_rename = []

        return self.edit_mode

    def rename_items(self):
        os.rename(self.current_item, self.text_input)
        self.tree[self.current_index] = self.get_absolute_path(self.text_input)

    def run(self):
        self.current_index = -1  # Initialize the selected index
        selected_files = []
        if len(self.tree) == 1:
            print("", file=sys.stderr)
            return
        while True:
            self.clean_display()
            self.display_files()
            if selected_files == [self.root_directory]:
                return selected_files
            char = getch()
            # print(char, file=sys.stderr)
            # return
            self.display_command()
            if char == 106 and not self.edit_mode:
                if self.current_index == -1:
                    self.move_cursor_down()
                self.move_cursor_down()
            elif char == 107 and not self.edit_mode:
                self.move_cursor_up()
            elif char == 108 and not self.edit_mode:
                self.add_selected_contents()
            elif char == 76 and not self.edit_mode:
                self.set_root(self.tree[self.current_index])
            elif char == 104 and not self.edit_mode:
                self.remove_selected_folder_contents()
            elif char == 100 and not self.edit_mode:
                self.mark_item_to_delete()
            elif char == 114 and not self.edit_mode:
                if self.toggle_edit_mode():
                    self.mark_item_to_rename()
                else:
                    self.marked_to_rename = self.marked_to_rename[:-1]
            elif char == 72:
                self.return_dir()
            elif char == 32 and not self.edit_mode:  # Spacebar
                self.toggle_file_selection()
            elif char in [113] and not self.edit_mode:
                selected_files = [self.root_directory]
                self.delete_itens()
                self.current_index = -1
            elif char == 27:
                if self.edit_mode:
                    self.toggle_edit_mode()
            elif char in {10, 13}:  # Enter key
                break
            else:
                if chr(char) in string.printable:
                    self.text_input += chr(char)
                elif char == 127:
                    self.text_input = self.text_input[:-1]
                else:
                    self.rename[self.tree[self.marked_to_rename[0]]] = self.text_input
                    pass

        selected_files = [self.tree[index] for index in self.selected_indices]
        if not selected_files:
            selected_files = [self.current_item]

        print(self.rename, file=sys.stderr)
        # return self.rename
        self.delete_itens()
        self.clean_display()
        return selected_files


if __name__ == "__main__":
    print("\033[?25l", end="", file=sys.stderr)
    selector = FileSelector(directory=".")
    selected_files = selector.run()
    print("\033[?25h", end="", file=sys.stderr)
    if selected_files:
        for file in selected_files:
            print(file, end="")
