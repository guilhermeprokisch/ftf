import os
import re
import shutil
import string
import sys
import termios
import tty
from pathlib import Path


def memoize(func):
    cache = {}

    def wrapper(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

    return wrapper


@memoize
def get_terminal_height():
    try:
        return int(os.popen("tput lines", "r").read())
    except OSError:
        return 24  # Default terminal height


@memoize
def get_terminal_width():
    try:
        return int(os.popen("tput columns", "r").read())
    except OSError:
        return 24  # Default terminal height


class NerdFontIcons:

    ICON_MAPPING = {
        "7z": "\u001b[31m\uf410\u001b[0m",
        "a": "\u001b[35m\uf479\u001b[0m",
        "ai": "\u001b[36m\ue7b4\u001b[0m",
        "apk": "\u001b[32m\uf420\u001b[0m",
        "asm": "\u001b[33m\uf471\u001b[0m",
        "asp": "\u001b[34m\uf481\u001b[0m",
        "aup": "\u001b[35m\uf473\u001b[0m",
        "avi": "\u001b[36m\uf03d\u001b[0m",
        "awk": "\u001b[33m\uf489\u001b[0m",
        "bash": "\u001b[32m\ue795\u001b[0m",
        "bat": "\u001b[31m\ue70f\u001b[0m",
        "bmp": "\u001b[36m\uf1c5\u001b[0m",
        "bz2": "\u001b[31m\uf410\u001b[0m",
        "c": "\u001b[34m\ue61e\u001b[0m",
        "c++": "\u001b[34m\ue61d\u001b[0m",
        "cab": "\u001b[31m\ue70f\u001b[0m",
        "cbr": "\u001b[33m\uf411\u001b[0m",
        "cbz": "\u001b[33m\uf411\u001b[0m",
        "cc": "\u001b[34m\ue61d\u001b[0m",
        "class": "\u001b[32m\ue256\u001b[0m",
        "clj": "\u001b[36m\ue768\u001b[0m",
        "cljc": "\u001b[36m\ue768\u001b[0m",
        "cljs": "\u001b[36m\ue76a\u001b[0m",
        "cmake": "\u001b[31m\ue20b\u001b[0m",
        "coffee": "\u001b[33m\ue751\u001b[0m",
        "conf": "\u001b[35m\uf43c\u001b[0m",
        "cp": "\u001b[32m\ue235\u001b[0m",
        "cpio": "\u001b[31m\uf410\u001b[0m",
        "cpp": "\u001b[34m\ue61d\u001b[0m",
        "cs": "\u001b[32m\uf81a\u001b[0m",
        "csh": "\u001b[32m\uf489\u001b[0m",
        "css": "\u001b[34m\ue749\u001b[0m",
        "cue": "\u001b[35m\uf001\u001b[0m",
        "cvs": "\u001b[34m\ue702\u001b[0m",
        "cxx": "\u001b[34m\ue61d\u001b[0m",
        "d": "\u001b[31m\ue7af\u001b[0m",
        "dart": "\u001b[36m\ue798\u001b[0m",
        "db": "\u001b[35m\uf1c0\u001b[0m",
        "deb": "\u001b[31m\uf420\u001b[0m",
        "diff": "\u001b[33m\uf440\u001b[0m",
        "dll": "\u001b[34m\uf481\u001b[0m",
        "doc": "\u001b[34m\uf1c2\u001b[0m",
        "docx": "\u001b[34m\uf1c2\u001b[0m",
        "dump": "\u001b[31m\uf1c0\u001b[0m",
        "edn": "\u001b[32m\ue72c\u001b[0m",
        "eex": "\u001b[35m\ue62d\u001b[0m",
        "efi": "\u001b[31m\uf1c0\u001b[0m",
        "ejs": "\u001b[33m\ue618\u001b[0m",
        "elf": "\u001b[31m\uf489\u001b[0m",
        "elm": "\u001b[36m\ue62c\u001b[0m",
        "epub": "\u001b[32m\ue28a\u001b[0m",
        "erl": "\u001b[31m\ue7b1\u001b[0m",
        "ex": "\u001b[35m\ue62d\u001b[0m",
        "exe": "\u001b[31m\uf013\u001b[0m",
        "exs": "\u001b[35m\ue62d\u001b[0m",
        "f#": "\u001b[36m\ue7a7\u001b[0m",
        "fifo": "\u001b[33m\uf43c\u001b[0m",
        "fish": "\u001b[32m\uf489\u001b[0m",
        "flac": "\u001b[35m\uf001\u001b[0m",
        "flv": "\u001b[36m\uf03d\u001b[0m",
        "fs": "\u001b[36m\ue7a7\u001b[0m",
        "fsi": "\u001b[36m\ue7a7\u001b[0m",
        "fsscript": "\u001b[36m\ue7a7\u001b[0m",
        "fsx": "\u001b[36m\ue7a7\u001b[0m",
        "gem": "\u001b[31m\ue23e\u001b[0m",
        "gemspec": "\u001b[31m\ue23e\u001b[0m",
        "gif": "\u001b[36m\uf1c5\u001b[0m",
        "go": "\u001b[36m\ue626\u001b[0m",
        "gz": "\u001b[31m\uf410\u001b[0m",
        "gzip": "\u001b[31m\uf410\u001b[0m",
        "h": "\u001b[35m\uf0fd\u001b[0m",
        "haml": "\u001b[35m\uf15b\u001b[0m",
        "hbs": "\u001b[33m\ue60f\u001b[0m",
        "hh": "\u001b[35m\uf0fd\u001b[0m",
        "hpp": "\u001b[35m\uf0fd\u001b[0m",
        "hrl": "\u001b[35m\uf0fd\u001b[0m",
        "hs": "\u001b[35m\ue777\u001b[0m",
        "htaccess": "\u001b[33m\uf023\u001b[0m",
        "htm": "\u001b[33m\uf13b\u001b[0m",
        "html": "\u001b[33m\uf13b\u001b[0m",
        "htpasswd": "\u001b[31m\uf023\u001b[0m",
        "cfg": "\u001b[35m\uf43c\u001b[0m",
        "hxx": "\u001b[35m\uf0fd\u001b[0m",
        "ico": "\u001b[36m\uf1c5\u001b[0m",
        "img": "\u001b[35m\uf1c0\u001b[0m",
        "ini": "\u001b[35m\uf43c\u001b[0m",
        "iso": "\u001b[35m\uf1c0\u001b[0m",
        "jar": "\u001b[31m\ue204\u001b[0m",
        "java": "\u001b[31m\ue204\u001b[0m",
        "jl": "\u001b[35m\ue624\u001b[0m",
        "jpeg": "\u001b[36m\uf1c5\u001b[0m",
        "jpg": "\u001b[36m\uf1c5\u001b[0m",
        "js": "\u001b[33m\ue74e\u001b[0m",
        "json": "\u001b[33m\ue60b\u001b[0m",
        "jsx": "\u001b[34m\ue7ba\u001b[0m",
        "key": "\u001b[35m\uf023\u001b[0m",
        "ksh": "\u001b[32m\uf489\u001b[0m",
        "leex": "\u001b[35m\ue62d\u001b[0m",
        "less": "\u001b[34m\ue758\u001b[0m",
        "lha": "\u001b[31m\uf410\u001b[0m",
        "lhs": "\u001b[35m\ue777\u001b[0m",
        "log": "\u001b[33m\uf18d\u001b[0m",
        "lua": "\u001b[36m\ue620\u001b[0m",
        "lzh": "\u001b[31m\uf410\u001b[0m",
        "lzma": "\u001b[31m\uf410\u001b[0m",
        "m4a": "\u001b[35m\uf001\u001b[0m",
        "m4v": "\u001b[36m\uf03d\u001b[0m",
        "markdown": "\u001b[34m\ue609\u001b[0m",
        "md": "\u001b[34m\ue609\u001b[0m",
        "mdx": "\u001b[34m\ue609\u001b[0m",
        "mjs": "\u001b[33m\ue74e\u001b[0m",
        "mkv": "\u001b[36m\uf03d\u001b[0m",
        "ml": "\u001b[33mλ\u001b[0m",
        "mli": "\u001b[33mλ\u001b[0m",
        "mov": "\u001b[36m\uf03d\u001b[0m",
        "mp3": "\u001b[35m\uf001\u001b[0m",
        "mp4": "\u001b[36m\uf03d\u001b[0m",
        "mpeg": "\u001b[36m\uf03d\u001b[0m",
        "mpg": "\u001b[36m\uf03d\u001b[0m",
        "msi": "\u001b[35m\uf1c4\u001b[0m",
        "mustache": "\u001b[33m\ue60f\u001b[0m",
        "nix": "\u001b[36m\uf313\u001b[0m",
        "o": "\u001b[31m\uf471\u001b[0m",
        "ogg": "\u001b[35m\uf001\u001b[0m",
        "part": "\u001b[35m\uf1c0\u001b[0m",
        "pdf": "\u001b[31m\uf1c1\u001b[0m",
        "php": "\u001b[35m\ue73d\u001b[0m",
        "pl": "\u001b[36m\ue769\u001b[0m",
        "pm": "\u001b[36m\ue769\u001b[0m",
        "png": "\u001b[36m\uf1c5\u001b[0m",
        "pp": "\u001b[35m\ue7a8\u001b[0m",
        "ppt": "\u001b[33m\uf1c4\u001b[0m",
        "pptx": "\u001b[33m\uf1c4\u001b[0m",
        "ps1": "\u001b[36m\uf489\u001b[0m",
        "psb": "\u001b[34m\ue7aa\u001b[0m",
        "psd": "\u001b[34m\ue7aa\u001b[0m",
        "pub": "\u001b[31m\uf1c1\u001b[0m",
        "py": "\u001b[33m\ue235\u001b[0m",
        "pyc": "\u001b[33m\ue235\u001b[0m",
        "pyd": "\u001b[33m\ue235\u001b[0m",
        "pyo": "\u001b[33m\ue235\u001b[0m",
        "r": "\u001b[34m\uf25d\u001b[0m",
        "rake": "\u001b[31m\ue21e\u001b[0m",
        "rar": "\u001b[31m\uf410\u001b[0m",
        "rb": "\u001b[31m\ue21e\u001b[0m",
        "rc": "\u001b[31m\uf43c\u001b[0m",
        "rlib": "\u001b[33m\ue7a8\u001b[0m",
        "rmd": "\u001b[34m\uf25d\u001b[0m",
        "rom": "\u001b[35m\uf1c0\u001b[0m",
        "rpm": "\u001b[31m\uf420\u001b[0m",
        "rproj": "\u001b[34m\ue7a7\u001b[0m",
        "rs": "\u001b[38;5;208m\ue7a8\u001b[0m",
        "rss": "\u001b[33m\uf09e\u001b[0m",
        "rtf": "\u001b[34m\uf1c2\u001b[0m",
        "s": "\u001b[31m\uf471\u001b[0m",
        "sass": "\u001b[35m\ue603\u001b[0m",
        "scala": "\u001b[31m\ue737\u001b[0m",
        "scss": "\u001b[35m\ue749\u001b[0m",
        "sh": "\u001b[32m\uf489\u001b[0m",
        "slim": "\u001b[33m\ue73b\u001b[0m",
        "sln": "\u001b[35m\ue70c\u001b[0m",
        "so": "\u001b[31m\uf471\u001b[0m",
        "sql": "\u001b[34m\uf1c0\u001b[0m",
        "styl": "\u001b[32m\ue600\u001b[0m",
        "suo": "\u001b[34m\ue70c\u001b[0m",
        "swift": "\u001b[33m\ue755\u001b[0m",
        "t": "\u001b[32m\ue769\u001b[0m",
        "tar": "\u001b[31m\uf410\u001b[0m",
        "tex": "\u001b[32m\uf034\u001b[0m",
        "tgz": "\u001b[31m\uf410\u001b[0m",
        "toml": "\u001b[38;5;250m\ue615\u001b[0m",
        "torrent": "\u001b[31m\uf481\u001b[0m",
        "ts": "\u001b[34m\ue628\u001b[0m",
        "tsx": "\u001b[34m\ue7ba\u001b[0m",
        "twig": "\u001b[32m\ue61c\u001b[0m",
        "vim": "\u001b[32m\ue62b\u001b[0m",
        "vimrc": "\u001b[32m\ue62b\u001b[0m",
        "vue": "\u001b[32m\ufd42\u001b[0m",
        "wav": "\u001b[35m\uf001\u001b[0m",
        "webm": "\u001b[36m\uf03d\u001b[0m",
        "webmanifest": "\u001b[32m\uf489\u001b[0m",
        "webp": "\u001b[36m\uf1c5\u001b[0m",
        "xbps": "\u001b[31m\uf420\u001b[0m",
        "xcplayground": "\u001b[33m\ue755\u001b[0m",
        "xhtml": "\u001b[33m\uf13b\u001b[0m",
        "xls": "\u001b[32m\uf1c3\u001b[0m",
        "xlsx": "\u001b[32m\uf1c3\u001b[0m",
        "xml": "\u001b[33m\uf72d\u001b[0m",
        "xul": "\u001b[33m\uf72d\u001b[0m",
        "xz": "\u001b[31m\uf410\u001b[0m",
        "yaml": "\u001b[33m\uf481\u001b[0m",
        "yml": "\u001b[33m\uf481\u001b[0m",
        "zip": "\u001b[31m\uf410\u001b[0m",
        "zsh": "\u001b[32m\uf489\u001b[0m",
    }

    ICON_MAPPING_COLORLESS = {
        "7z": "",
        "a": "",
        "ai": "",
        "apk": "",
        "asm": "",
        "asp": "",
        "aup": "",
        "avi": "",
        "awk": "",
        "bash": "",
        "bat": "",
        "bmp": "",
        "bz2": "",
        "c": "",
        "c++": "",
        "cab": "",
        "cbr": "",
        "cbz": "",
        "cc": "",
        "class": "",
        "clj": "",
        "cljc": "",
        "cljs": "",
        "cmake": "",
        "coffee": "",
        "conf": "",
        "cp": "",
        "cpio": "",
        "cpp": "",
        "cs": "",
        "csh": "",
        "css": "",
        "cue": "",
        "cvs": "",
        "cxx": "",
        "d": "",
        "dart": "",
        "db": "",
        "deb": "",
        "diff": "",
        "dll": "",
        "doc": "",
        "docx": "",
        "dump": "",
        "edn": "",
        "eex": "",
        "efi": "",
        "ejs": "",
        "elf": "",
        "elm": "",
        "epub": "",
        "erl": "",
        "ex": "",
        "exe": "",
        "exs": "",
        "f#": "",
        "fifo": "ﳣ",
        "fish": "",
        "flac": "",
        "flv": "",
        "fs": "",
        "fsi": "",
        "fsscript": "",
        "fsx": "",
        "gem": "",
        "gemspec": "",
        "gif": "",
        "go": "",
        "gz": "",
        "gzip": "",
        "h": "",
        "haml": "",
        "hbs": "",
        "hh": "",
        "hpp": "",
        "hrl": "",
        "hs": "",
        "htaccess": "",
        "htm": "",
        "html": "",
        "htpasswd": "",
        "cfg": "",
        "hxx": "",
        "ico": "",
        "img": "",
        "ini": "",
        "iso": "",
        "jar": "",
        "java": "",
        "jl": "",
        "jpeg": "",
        "jpg": "",
        "js": "",
        "json": "",
        "jsx": "",
        "key": "",
        "ksh": "",
        "leex": "",
        "less": "",
        "lha": "",
        "lhs": "",
        "log": "",
        "lua": "",
        "lzh": "",
        "lzma": "",
        "m4a": "",
        "m4v": "",
        "markdown": "",
        "md": "",
        "mdx": "",
        "mjs": "",
        "mkv": "",
        "ml": "λ",
        "mli": "λ",
        "mov": "",
        "mp3": "",
        "mp4": "",
        "mpeg": "",
        "mpg": "",
        "msi": "",
        "mustache": "",
        "nix": "",
        "o": "",
        "ogg": "",
        "part": "",
        "pdf": "",
        "php": "",
        "pl": "",
        "pm": "",
        "png": "",
        "pp": "",
        "ppt": "",
        "pptx": "",
        "ps1": "",
        "psb": "",
        "psd": "",
        "pub": "",
        "py": "",
        "pyc": "",
        "pyd": "",
        "pyo": "",
        "r": "ﳒ",
        "rake": "",
        "rar": "",
        "rb": "",
        "rc": "",
        "rlib": "",
        "rmd": "",
        "rom": "",
        "rpm": "",
        "rproj": "鉶",
        "rs": "",
        "rss": "",
        "rtf": "",
        "s": "",
        "sass": "",
        "scala": "",
        "scss": "",
        "sh": "",
        "slim": "",
        "sln": "",
        "so": "",
        "sql": "",
        "styl": "",
        "suo": "",
        "swift": "",
        "t": "",
        "tar": "",
        "tex": "ﭨ",
        "tgz": "",
        "toml": "",
        "torrent": "",
        "ts": "",
        "tsx": "",
        "twig": "",
        "vim": "",
        "vimrc": "",
        "vue": "﵂",
        "wav": "",
        "webm": "",
        "webmanifest": "",
        "webp": "",
        "xbps": "",
        "xcplayground": "",
        "xhtml": "",
        "xls": "",
        "xlsx": "",
        "xml": "",
        "xul": "",
        "xz": "",
        "yaml": "",
        "yml": "",
        "zip": "",
        "zsh": "",
    }

    FILE_NODE_EXACT_MATCHES = {
        ".bash_aliases": "\u001b[32m\uf489\u001b[0m",
        ".bash_history": "\u001b[32m\uf489\u001b[0m",
        ".bash_logout": "\u001b[32m\uf489\u001b[0m",
        ".bash_profile": "\u001b[32m\uf489\u001b[0m",
        ".bashprofile": "\u001b[32m\uf489\u001b[0m",
        ".bashrc": "\u001b[32m\uf489\u001b[0m",
        ".dmrc": "\u001b[33m\uf43c\u001b[0m",
        ".DS_Store": "\u001b[35m\uf43c\u001b[0m",
        ".fasd": "\u001b[35m\uf43c\u001b[0m",
        ".fehbg": "\u001b[35m\uf43c\u001b[0m",
        ".gitattributes": "\u001b[31m\uf1d3\u001b[0m",
        ".gitconfig": "\u001b[31m\uf1d3\u001b[0m",
        ".gitignore": "\u001b[31m\uf1d3\u001b[0m",
        ".gitlab-ci.yml": "\u001b[33m\uf7d2\u001b[0m",
        ".gvimrc": "\u001b[32m\uf43c\u001b[0m",
        ".inputrc": "\u001b[35m\uf43c\u001b[0m",
        ".jack-settings": "\u001b[35m\uf43c\u001b[0m",
        ".mime.types": "\u001b[35m\uf43c\u001b[0m",
        ".ncmpcpp": "\u001b[35m\uf43c\u001b[0m",
        ".nvidia-settings-rc": "\u001b[35m\uf43c\u001b[0m",
        ".pam_environment": "\u001b[35m\uf43c\u001b[0m",
        ".profile": "\u001b[35m\uf43c\u001b[0m",
        ".recently-used": "\u001b[35m\uf43c\u001b[0m",
        ".selected_editor": "\u001b[35m\uf43c\u001b[0m",
        ".vim": "\u001b[32m\ue62b\u001b[0m",
        ".viminfo": "\u001b[32m\ue62b\u001b[0m",
        ".vimrc": "\u001b[32m\ue62b\u001b[0m",
        ".Xauthority": "\u001b[35m\uf43c\u001b[0m",
        ".Xdefaults": "\u001b[35m\uf43c\u001b[0m",
        ".xinitrc": "\u001b[35m\uf43c\u001b[0m",
        ".xinputrc": "\u001b[35m\uf43c\u001b[0m",
        ".Xresources": "\u001b[35m\uf43c\u001b[0m",
        ".zshrc": "\u001b[32m\uf489\u001b[0m",
        "_gvimrc": "\u001b[32m\ue62b\u001b[0m",
        "_vimrc": "\u001b[32m\ue62b\u001b[0m",
        "a.out": "\u001b[31m\uf471\u001b[0m",
        "authorized_keys": "\u001b[35m\uf43c\u001b[0m",
        "bspwmrc": "\u001b[35m\uf43c\u001b[0m",
        "cmakelists.txt": "\u001b[31m\ue20b\u001b[0m",
        "config": "\u001b[35m\uf43c\u001b[0m",
        "config.ac": "\u001b[35m\uf43c\u001b[0m",
        "config.m4": "\u001b[35m\uf43c\u001b[0m",
        "config.mk": "\u001b[35m\uf43c\u001b[0m",
        "config.ru": "\u001b[31m\ue21e\u001b[0m",
        "configure": "\u001b[35m\uf43c\u001b[0m",
        "docker-compose.yml": "\u001b[36m\uf308\u001b[0m",
        "dockerfile": "\u001b[36m\uf308\u001b[0m",
        "Dockerfile": "\u001b[36m\uf308\u001b[0m",
        "dropbox": "\u001b[34m\uf16b\u001b[0m",
        "exact-match-case-sensitive-1.txt": "\u001b[35mX1\u001b[0m",
        "exact-match-case-sensitive-2": "\u001b[35mX2\u001b[0m",
        "favicon.ico": "\u001b[32m\ue623\u001b[0m",
        "gemfile": "\u001b[31m\ue21e\u001b[0m",
        "gruntfile.coffee": "\u001b[33m\ue611\u001b[0m",
        "gruntfile.js": "\u001b[33m\ue611\u001b[0m",
        "gruntfile.ls": "\u001b[33m\ue611\u001b[0m",
        "gulpfile.coffee": "\u001b[31m\ue610\u001b[0m",
        "gulpfile.js": "\u001b[31m\ue610\u001b[0m",
        "gulpfile.ls": "\u001b[31m\ue610\u001b[0m",
        "ini": "\u001b[35m\uf43c\u001b[0m",
        "known_hosts": "\u001b[35m\uf43c\u001b[0m",
        "ledger": "\u001b[35m\uf43c\u001b[0m",
        "license": "\u001b[33m\uf2c2\u001b[0m",
        "LICENSE": "\u001b[33m\uf2c2\u001b[0m",
        "LICENSE.md": "\u001b[33m\uf2c2\u001b[0m",
        "LICENSE.txt": "\u001b[33m\uf2c2\u001b[0m",
        "Makefile": "\u001b[35m\uf489\u001b[0m",
        "makefile": "\u001b[35m\uf489\u001b[0m",
        "Makefile.ac": "\u001b[35m\uf489\u001b[0m",
        "Makefile.in": "\u001b[35m\uf489\u001b[0m",
        "mimeapps.list": "\u001b[35m\uf43c\u001b[0m",
        "mix.lock": "\u001b[35m\uf43c\u001b[0m",
        "node_modules": "\u001b[35m\uf43c\u001b[0m",
        "package-lock.json": "\u001b[33m\ue718\u001b[0m",
        "package.json": "\u001b[33m\ue718\u001b[0m",
        "playlists": "\u001b[35m\uf43c\u001b[0m",
        "procfile": "\u001b[35m\uf43c\u001b[0m",
        "Rakefile": "\u001b[31m\ue21e\u001b[0m",
        "rakefile": "\u001b[31m\ue21e\u001b[0m",
        "react.jsx": "\u001b[34m\ue7ba\u001b[0m",
        "README": "\u001b[33m\uf48d\u001b[0m",
        "README.markdown": "\u001b[33m\uf48d\u001b[0m",
        "README.md": "\u001b[33m\uf48d\u001b[0m",
        "README.rst": "\u001b[33m\uf48d\u001b[0m",
        "README.txt": "\u001b[33m\uf48d\u001b[0m",
        "sxhkdrc": "\u001b[35m\uf43c\u001b[0m",
        "user-dirs.dirs": "\u001b[35m\uf43c\u001b[0m",
        "webpack.config.js": "\u001b[33m\ue61f\u001b[0m",
    }

    FILE_NODE_EXACT_MATCHES_COLORLESS = {
        ".bash_aliases": "",
        ".bash_history": "",
        ".bash_logout": "",
        ".bash_profile": "",
        ".bashprofile": "",
        ".bashrc": "",
        ".dmrc": "",
        ".DS_Store": "",
        ".fasd": "",
        ".fehbg": "",
        ".gitattributes": "",
        ".gitconfig": "",
        ".gitignore": "",
        ".gitlab-ci.yml": "",
        ".gvimrc": "",
        ".inputrc": "",
        ".jack-settings": "",
        ".mime.types": "",
        ".ncmpcpp": "",
        ".nvidia-settings-rc": "",
        ".pam_environment": "",
        ".profile": "",
        ".recently-used": "",
        ".selected_editor": "",
        ".vim": "",
        ".viminfo": "",
        ".vimrc": "",
        ".Xauthority": "",
        ".Xdefaults": "",
        ".xinitrc": "",
        ".xinputrc": "",
        ".Xresources": "",
        ".zshrc": "",
        "_gvimrc": "",
        "_vimrc": "",
        "a.out": "",
        "authorized_keys": "",
        "bspwmrc": "",
        "cmakelists.txt": "",
        "config": "",
        "config.ac": "",
        "config.m4": "",
        "config.mk": "",
        "config.ru": "",
        "configure": "",
        "docker-compose.yml": "",
        "dockerfile": "",
        "Dockerfile": "",
        "dropbox": "",
        "exact-match-case-sensitive-1.txt": "X1",
        "exact-match-case-sensitive-2": "X2",
        "favicon.ico": "",
        "gemfile": "",
        "gruntfile.coffee": "",
        "gruntfile.js": "",
        "gruntfile.ls": "",
        "gulpfile.coffee": "",
        "gulpfile.js": "",
        "gulpfile.ls": "",
        "ini": "",
        "known_hosts": "",
        "ledger": "",
        "license": "",
        "LICENSE": "",
        "LICENSE.md": "",
        "LICENSE.txt": "",
        "Makefile": "",
        "makefile": "",
        "Makefile.ac": "",
        "Makefile.in": "",
        "mimeapps.list": "",
        "mix.lock": "",
        "node_modules": "",
        "package-lock.json": "",
        "package.json": "",
        "playlists": "",
        "procfile": "",
        "Rakefile": "",
        "rakefile": "",
        "react.jsx": "",
        "README": "",
        "README.markdown": "",
        "README.md": "",
        "README.rst": "",
        "README.txt": "",
        "sxhkdrc": "",
        "user-dirs.dirs": "",
        "webpack.config.js": "",
    }

    @classmethod
    def get_icon(cls, file_name):
        if file_name:
            if os.path.isdir(file_name) or file_name[-1] == "/":
                return "\u001b[34m  "

        extension = file_name[file_name.rfind(".") :]
        result = cls.FILE_NODE_EXACT_MATCHES.get(os.path.basename(file_name), None)
        if not result:
            result = cls.ICON_MAPPING.get(extension[1:].lower(), "\uF016")

        return " " + result + " "


class Cursor:
    def __init__(self):
        self.initial_position = self.get_initial_position()
        self.x = self.initial_position[0]
        self.y = self.initial_position[1]

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
        init_x, init_y = self.initial_position
        self.move_to(init_x, init_y)

    def get_initial_position(self):
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
        self.tree = ["."]
        self.expanded_folders = set()
        self.add_items(
            [
                f"{self.get_absolute_path(file)}"
                for file in os.listdir(self.root_directory)
            ]
        )
        self.selected_indices = []
        self.cursor = Cursor()
        self.text_input = ""
        self.marked_to_delete = []
        self.marked_to_copy = []
        self.marked_to_cut = []
        self.marked_as_new = []
        self.edit_mode = False
        self.rename_mode = False
        self.add_mode = False
        self.exit_signal = False
        self.term_height = get_terminal_height()
        self.term_width = get_terminal_width()
        self.search_query = ""
        self.display_start_line = self.cursor.y  # Store the starting line for display
        self.parent_stack = []

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
        depth = item_relative_path.count(os.sep)
        if depth == 1:
            return " "
        indent_chars = "\u001b[90m" + "▏ " * (depth - 1) + "\u001b[0m"
        if is_selected:
            return len(indent_chars[10:]) * " "
        return indent_chars.replace("▏", " ", 1)

    def change_root(self, directory):
        self.root_directory = directory
        self.tree = [self.root_directory]
        self.add_items(
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
            return "\033[1;32m  copy \033[0m"
        if self.is_marked_to_cut:
            return "\033[1;35m 󰆐 cut \033[0m"
        if self.is_marked_to_delete:
            return "\033[1;31m  delete\u001b[0m "
        if self.is_new or self.is_adding:
            return "\033[1;33m  new \u001b[0m "
        if self.is_renaming:
            return "\033[1;33m 󰙏 renaming \u001b[0m "
        return ""

    def display_files(self):
        self.update_parent_stack()

        # Display parent stack
        self.cursor.move_to(0, self.display_start_line)
        self.display_parent_stack()

        # Adjust display area for file list
        adjusted_start_line = self.display_start_line + len(self.parent_stack)
        terminal_height = self.term_height - len(self.parent_stack)
        page_size = min(terminal_height - adjusted_start_line - 2, len(self.tree))

        start_index = max(0, self.current_index - page_size // 2)
        end_index = min(len(self.tree), start_index + page_size)

        if self.current_index < start_index:
            self.current_index = start_index
        elif self.current_index >= end_index:
            self.current_index = end_index - 1

        # Move cursor to the starting position for file list
        self.cursor.move_to(0, adjusted_start_line)

        for index in range(start_index, end_index):
            item = self.tree[index]
            self.is_selected = index == self.current_index
            self.is_picked = index in self.selected_indices
            self.is_marked_to_copy = item in self.marked_to_copy
            self.is_marked_to_cut = item in self.marked_to_cut
            self.is_marked_to_delete = item in self.marked_to_delete
            self.is_new = item in self.marked_as_new
            self.is_renaming = self.rename_mode and self.is_selected
            self.is_adding = self.add_mode and self.is_selected

            indent = self.indent(item, self.is_selected, self.is_picked)

            item_icon = NerdFontIcons.get_icon(item)

            if item == ".":
                basename = os.path.basename(os.path.abspath(self.root_directory))
            else:
                basename = os.path.basename(os.path.abspath(item))

            display_string = item_icon + basename

            if self.is_marked_to_delete:
                display_string = f"\u001b[9m{display_string}\u001b"

            if self.is_renaming:
                display_string = (
                    NerdFontIcons.get_icon(self.text_input) + self.text_input
                )

            print("\033[K", end="", file=sys.stderr)  # Clear the current line

            if self.is_adding:
                new_file_display_string = (
                    NerdFontIcons.get_icon(self.text_input) + self.text_input
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

        # Clear any remaining lines from the previous display
        for _ in range(end_index - start_index, page_size):
            print("\033[K", file=sys.stderr)
            self.cursor.move_down()

        # Move the cursor back to the top of our display area
        self.cursor.move_up(page_size)

    def clean_display(self):
        self.term_height = get_terminal_height()
        self.cursor.move_to_initial_position()
        print(
            (self.term_height + len(self.parent_stack)) * "\33[2K\r\n", file=sys.stderr
        )
        self.cursor.move_to_initial_position()

    def add_items(self, files):
        self.tree.extend(files)
        self.tree = list(set(self.tree))
        self.tree.sort()
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
        if os.path.isdir(selected_path) and selected_path not in self.expanded_folders:
            new_files = [f"{selected}/{item}" for item in os.listdir(selected_path)]
            new_files = self.sort_tree(new_files)
            insert_index = self.current_index + 1
            for file in new_files:
                self.tree.insert(insert_index, file)
                insert_index += 1
            self.expanded_folders.add(selected_path)

    def remove_selected_folder_contents(self):
        selected = self.tree[self.current_index]
        selected_path = os.path.join(self.root_directory, selected)

        if os.path.isdir(selected_path):
            self.tree = [
                item for item in self.tree if not item.startswith(f"{selected}/")
            ]
            self.expanded_folders.discard(selected_path)
            self.clean_tree()

    def clean_tree(self):
        self.tree = self.sort_tree(list(set(self.tree)))
        self.current_index = min(self.current_index, len(self.tree) - 1)

    def return_dir(self):
        self.set_root(Path(self.root_directory).parent.absolute())

    def delete_items(self):
        for item in self.marked_to_delete:
            if os.path.isdir(item):
                shutil.rmtree(item, ignore_errors=True)
                self.tree = [x for x in self.tree if not x.startswith(item)]
            else:
                os.remove(item)
                self.tree.remove(item)

        self.marked_to_delete = []

    def set_root(self, path):
        if os.path.isdir(path):
            self.clean_display()
            self.root_directory = Path(path).absolute()
            self.tree = ["."]
            self.add_items(
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
            if src in self.tree:
                self.tree.remove(src)
            self.tree.insert(self.current_index + 1, dst)
            self.current_index += 1
            self.marked_as_new.append(dst)
        self.marked_to_copy = []

    def pre_exit(self):
        if self.mark_item_to_delete:
            self.delete_items()
        if self.selected_file == [self.root_directory]:
            return self.selected_file

    def update_parent_stack(self):
        current_path = self.get_relative_path(self.tree[self.current_index])
        if current_path == ".":
            self.parent_stack = []
            return

        parents = []
        while current_path != ".":
            parent = os.path.dirname(current_path)
            if parent == current_path:  # We've reached the root
                break
            parents.append(parent)
            current_path = parent

        self.parent_stack = list(reversed(parents))

    def display_parent_stack(self):
        for i, parent in enumerate(self.parent_stack):
            indent = " " * i
            item_icon = NerdFontIcons.get_icon(
                os.path.join(self.root_directory, parent)
            )
            basename = os.path.basename(parent)
            display_string = f"{indent}{item_icon}{basename}"
            print(f"\033[34m{display_string}\033[0m", file=sys.stderr)

    def run(self):
        self.current_index = -1
        self.selected_file = []
        if len(self.tree) == 1:
            print("", file=sys.stderr)
            return
        prev_tree = []
        while True:
            if self.tree != prev_tree:
                self.display_files()
                prev_tree = self.tree.copy()
            self.display_files()
            if self.exit_signal:
                return self.pre_exit()
            char = getch()

            if not self.edit_mode:
                if char == 106:  # j
                    if self.current_index == -1:
                        self.move_cursor_down()
                    self.move_cursor_down()
                elif char == 107:  # k
                    self.move_cursor_up()
                elif char == 108:  # l
                    self.add_selected_contents()
                elif char == 76:  # L
                    self.set_root(self.tree[self.current_index])
                elif char == 104:  # h
                    self.remove_selected_folder_contents()
                elif char == 100:  # d
                    self.mark_item_to_delete()
                elif char == 68:  # D
                    self.delete_items()
                elif char == 121:  # y
                    self.mark_item_to_copy()
                elif char == 120:  # x
                    self.mark_item_to_cut()
                elif char == 112:  # p
                    self.paste_items()
                elif char == 114:  # r
                    self.text_input = os.path.basename(self.current_item)
                    self.rename_mode = True
                    self.edit_mode = True
                    continue
                elif char == 97:  # a
                    self.edit_mode = True
                    self.add_mode = True
                    continue
                elif char == 72:  # H
                    self.return_dir()
                elif char == 32:  # Spacebar
                    self.toggle_file_selection()
                elif char == 113:  # q
                    self.current_index = -1
                    self.selected_file = [self.root_directory]
                    self.exit_signal = True
                elif char in {10, 13}:  # Enter key
                    break
                elif char == 47:  # /
                    self.edit_mode = True
                    self.search_mode = True
                    self.search_mode = True
                    self.display_search_input()
                    continue
                else:
                    pass

            if self.edit_mode:
                if char in {10, 13, 27}:  # Enter key or Escape key
                    self.exit_edit_mode()
                    continue
                if chr(char) in string.printable:
                    self.text_input += chr(char)
                if char == 127:  # Backspace
                    self.text_input = self.text_input[:-1]
                if char in {10, 13, 27}:  # Enter key or Escape key
                    self.display_search_input()
                    if self.search_mode:
                        if char == 27:  # Escape key
                            self.search_mode = False
                            self.search_query = ""
                        elif char in {10, 13}:  # Enter key
                            self.fuzzy_search()
                            self.search_mode = False
                        elif chr(char) in string.printable:
                            self.search_query += chr(char)
                            self.display_search_input()
                        elif char == 127:  # Backspace
                            self.search_query = self.search_query[:-1]
                            self.display_search_input()
                            # self.exit_edit_mode()
                            # continue
                if chr(char) in string.printable:
                    self.search_query += chr(char)
                if char == 127:  # Backspace
                    self.search_query = self.search_query[:-1]

        self.selected_file = [self.tree[index] for index in self.selected_indices]
        if not self.selected_file:
            self.selected_file = [self.current_item]
        return self.selected_file

    def sort_tree(self, paths):
        def sort_key(path):
            is_dir = os.path.isdir(path)
            base_name = os.path.basename(path).lower()
            return (not is_dir, base_name)

        sorted_paths = sorted(paths, key=sort_key)
        return sorted_paths

    def fuzzy_search(self):
        if self.search_query:
            matches = []
            for index, item in enumerate(self.tree):
                if self.fuzzy_match(self.search_query, os.path.basename(item)):
                    matches.append(index)

            if matches:
                self.current_index = matches[0]
                self.expand_to_current_item()

        self.search_query = ""
        self.search_mode = False

    def fuzzy_match(self, query, text):
        query = query.lower()
        text = text.lower()
        query_chars = list(query)
        text_chars = list(text)

        if len(query_chars) > len(text_chars):
            return False

        while query_chars and text_chars:
            if query_chars[0] == text_chars[0]:
                query_chars.pop(0)
            text_chars.pop(0)

        return len(query_chars) == 0

    def expand_to_current_item(self):
        current_item = self.tree[self.current_index]
        current_path = os.path.dirname(current_item)

        while current_path != self.root_directory:
            self.add_selected_contents()
            current_path = os.path.dirname(current_path)

    def display_search_input(self):
        # Move the cursor to the bottom of our display area
        self.cursor.move_to(0, self.display_start_line + self.term_height - 2)

        # Display the search input bar
        print(f"\033[K\033[7m Search: {self.search_query}\033[0m", end="", flush=True)

        # Clear the screen
        self.clean_display()

        # Calculate the middle position of the screen
        middle_y = self.term_height // 2
        middle_x = self.term_width // 2

        # Move the cursor to the middle of the screen
        self.cursor.move_to(middle_x - 20, middle_y)

        # Display the search input bar
        print(f"\033[7m Search: {self.search_query}\033[0m", end="", flush=True)


def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return ord(sys.stdin.read(1))
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


if __name__ == "__main__":
    print("\033[?25l", end="", file=sys.stderr)  # Hide cursor
    selector = FileSelector(directory=".")
    selected_files = selector.run()
    print("\033[?25h", end="", file=sys.stderr)  # Show cursor
    if selected_files:
        for file in selected_files:
            print(file, end="")
