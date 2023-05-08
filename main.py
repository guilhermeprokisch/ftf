import os
import re
import shutil
import string
import subprocess
import sys
import termios
import tty
from pathlib import Path


def memoize(func):
    cache = {}

    def wrapper(*args):
        if args in cache:
            return cache[args]
        else:
            result = func(*args)
            cache[args] = result
            return result

    return wrapper


@memoize
def get_exa_icon(filepath):
    output = subprocess.check_output(["lsd", "--icon", "always", filepath]).decode(
        "utf-8"
    )
    icon = output.split()[0]
    return icon


def get_nerdfont_icon(file_name):
    # if file_name:
    #     if os.path.isdir(file_name) or file_name[-1] == "/":
    #         return "\u001b[34m "
    #     return get_exa_icon(file_name) + " "
    # return " "
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

    if file_name:
        if os.path.isdir(file_name) or file_name[-1] == "/":
            return "\u001b[34m "

    extension = file_name[file_name.rfind(".") :]  # Extract the file extension
    return icon_mapping.get(extension.lower(), "\uF016") + " "


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
        self.marked_to_copy = []
        self.marked_to_cut = []
        self.marked_as_new = []
        self.rename = {}
        self.edit_mode = False
        self.rename_mode = False
        self.add_mode = False
        self.exit_signal = False

    def arrow_indicator(self):
        if self.is_selected:
            if self.edit_mode:
                return "\33[2K\r\u001b[33m>\u001b[0m"
            return "\33[2K\r\u001b[34m>\u001b[0m"
        return ""

    def pick_indicator(self):
        if self.is_picked:
            return "\u001b[33m*\u001b[0m "
        return ""

    def highlight_indicator(self, string):
        if self.is_selected:
            return f"\u001b[7m{string}\u001b[0m\u001b[0m"
        return f"{string}\u001b[0m"

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

    def action_indicator(self):
        if self.is_marked_to_copy:
            return "\033[1;32m  copy \033[0m"
        if self.is_marked_to_cut:
            return "\033[1;35m 󰆐 cut \033[0m"
        if self.is_marked_to_delete:
            return "\033[1;31m  delete\u001b[0m "
        if self.is_new or self.is_adding:
            return "\033[1;33m  new \u001b[0m "
        if self.is_renaming:
            return "\033[1;33m 󰙏 renaming \u001b[0m "
        return ""

    def display_files(self):
        for index, item in enumerate(self.tree):
            self.is_selected = index == self.current_index
            self.is_picked = index in self.selected_indices
            self.is_marked_to_copy = item in self.marked_to_copy
            self.is_marked_to_cut = item in self.marked_to_cut
            self.is_marked_to_delete = item in self.marked_to_delete
            self.is_new = item in self.marked_as_new
            self.is_renaming = self.rename_mode and self.is_selected
            self.is_adding = self.add_mode and self.is_selected

            indent = self.indent(item, self.is_selected, self.is_picked)

            item_icon = get_nerdfont_icon(item)

            if item == ".":
                basename = os.path.basename(os.path.abspath(self.root_directory))
            else:
                basename = os.path.basename(os.path.abspath(item))

            display_string = item_icon + basename

            if self.is_marked_to_delete:
                display_string = f"\u001b[9m{display_string}\u001b"

            if self.is_renaming:
                display_string = get_nerdfont_icon(self.text_input) + self.text_input

            if self.is_adding:
                new_file_display_string = (
                    get_nerdfont_icon(self.text_input) + self.text_input
                )
                print(
                    f" {indent}{self.pick_indicator()}{display_string}",
                    file=sys.stderr,
                )
                print(
                    f"{self.arrow_indicator()}{indent}{self.highlight_indicator(new_file_display_string)}{self.action_indicator()}",
                    file=sys.stderr,
                )
                continue

            print(
                f"{self.arrow_indicator()}{indent}{self.pick_indicator()}{self.highlight_indicator(display_string)}{self.action_indicator()}",
                file=sys.stderr,
            )

    def display_command(self):
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

        self.tree = self.sort_tree(self.tree)

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
        if self.current_item in self.marked_to_delete:
            self.marked_to_delete.remove(self.current_item)
            return
        self.marked_to_delete.append(self.current_item)

    def mark_item_to_copy(self):
        if self.current_item in self.marked_to_copy:
            self.marked_to_copy.remove(self.current_item)
            return
        self.marked_to_copy.append(self.current_item)

    def mark_item_to_cut(self):
        if self.current_item in self.marked_to_cut:
            self.marked_to_cut.remove(self.current_item)
            return
        self.marked_to_cut.append(self.current_item)

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
        for item in self.marked_to_delete:
            if os.path.isdir(item):
                shutil.rmtree(item, ignore_errors=True)
            else:
                os.remove(item)

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

    def exit_edit_mode(self):
        self.edit_mode = False
        if self.add_mode:
            self.add_file()
            self.add_mode = False
        if self.rename_mode:
            self.rename_items()
            self.rename_mode = False
        self.text_input = ""

    def rename_items(self):
        if self.text_input != "":
            new_name = os.path.dirname(self.current_item) + "/" + self.text_input
            os.rename(
                self.current_item,
                new_name,
            )
            self.tree[self.current_index] = new_name

    def add_file(self):
        if self.text_input != "":
            if os.path.isdir(self.current_item):
                new_path = (
                    os.path.dirname(self.current_item + "/") + "/" + self.text_input
                )
            else:
                new_path = os.path.dirname(self.current_item) + "/" + self.text_input

            if new_path[-1] == "/":
                if not os.path.exists(new_path):
                    os.makedirs(new_path)
            else:
                Path(new_path).touch()
            self.tree.insert(self.current_index + 1, new_path)
            self.marked_as_new.append(new_path)
        self.current_index += 1

    def paste_items(self):
        for src in self.marked_to_copy:
            if os.path.isdir(self.current_item):
                dst = self.current_item + "/" + os.path.basename(os.path.abspath(src))
            else:
                dst = (
                    os.path.dirname(self.current_item)
                    + "/"
                    + os.path.basename(os.path.abspath(src))
                )
            shutil.copy(src, dst)
            self.tree.insert(self.current_index + 1, dst)
            self.current_index += 1
            self.marked_as_new.append(dst)
        for src in self.marked_to_cut:
            if os.path.isdir(self.current_item):
                dst = self.current_item + "/" + os.path.basename(os.path.abspath(src))
            else:
                dst = (
                    os.path.dirname(self.current_item)
                    + "/"
                    + os.path.basename(os.path.abspath(src))
                )
            shutil.move(src, dst)
            self.tree.remove(src)
            self.tree.insert(self.current_index + 1, dst)
            self.current_index += 1
            self.marked_as_new.append(dst)
        self.marked_to_copy = []

    def pre_exit(self):
        if self.mark_item_to_delete:
            self.delete_itens()
        if self.selected_file == [self.root_directory]:
            return self.selected_file

    def run(self):
        self.current_index = -1  # Initialize the selected index
        self.selected_file = []
        if len(self.tree) == 1:
            print("", file=sys.stderr)
            return
        while True:
            self.clean_display()
            self.display_files()
            if self.exit_signal:
                return self.pre_exit()
            char = getch()
            # print(char, file=sys.stderr)
            # return
            if not self.edit_mode:
                if char == 106:
                    if self.current_index == -1:
                        self.move_cursor_down()
                    self.move_cursor_down()
                elif char == 107:
                    self.move_cursor_up()
                elif char == 108:
                    self.add_selected_contents()
                elif char == 76:
                    self.set_root(self.tree[self.current_index])
                elif char == 104:
                    self.remove_selected_folder_contents()
                elif char == 100:
                    self.mark_item_to_delete()
                elif char == 121:
                    self.mark_item_to_copy()
                elif char == 120:
                    self.mark_item_to_cut()
                elif char == 112:
                    self.paste_items()
                elif char == 114:
                    self.text_input = os.path.basename(self.current_item)
                    self.rename_mode = True
                    self.edit_mode = True
                    continue
                elif char == 97:
                    self.edit_mode = True
                    self.add_mode = True
                    continue
                elif char == 72:
                    self.return_dir()
                elif char == 32:  # Spacebar
                    self.toggle_file_selection()
                elif char == 113:
                    self.current_index = -1
                    self.selected_file = [self.root_directory]
                    self.exit_signal = True
                elif char in {10, 13}:  # Enter key
                    break
                else:
                    pass

            if self.edit_mode:
                if char in {10, 13, 27}:
                    self.exit_edit_mode()
                    continue
                if chr(char) in string.printable:
                    self.text_input += chr(char)
                if char == 127:
                    self.text_input = self.text_input[:-1]

        self.selected_file = [self.tree[index] for index in self.selected_indices]
        if not self.selected_file:
            self.selected_file = [self.current_item]
        return self.selected_file

    def sort_tree(self, paths):
        def sort_key(path):
            return tuple(
                (1 if os.path.isdir(p) else 2, p) for p in path.split(os.path.sep)
            )

        sorted_paths = sorted(paths, key=sort_key)
        return sorted_paths


if __name__ == "__main__":
    print("\033[?25l", end="", file=sys.stderr)
    selector = FileSelector(directory=".")
    selected_files = selector.run()
    print("\033[?25h", end="", file=sys.stderr)
    if selected_files:
        for file in selected_files:
            print(file, end="")
