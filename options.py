import ctypes
import sys
import os
from ctypes import wintypes
import win32clipboard
import win32gui
import win32con

import pythoncom


def is_ru_lang_keyboard(a):
    """
    Функция проверяет, какая раскладка стоит при Копипасте из(в) строку
    return: Вариант раскладки на данный момент времени
    """

    u = ctypes.windll.LoadLibrary("user32.dll")
    pf = getattr(u, "GetKeyboardLayout")
    return hex(pf(0)) == '0x4190419'


def keys(event):
    """
    Варианты нажатия на кнопки Копировать, Вставить, Вырезать, Очистить и Выбрать всё. Так как Tkinter не дает
    возможности пользоваться горячими клавишами при русской раскладке клавиатуры, нам необходимо проверять на
    "НИЗКОМ" уровне какие кнопки были нажаты. И в зависимости от вида кнопки, выполнять определенные функции.
    :param event:
    :return:
    """
    if is_ru_lang_keyboard(event):
        if event.keycode == 86:
            event.widget.event_generate("<<Paste>>")
        elif event.keycode == 67:
            event.widget.event_generate("<<Copy>>")
        elif event.keycode == 88:
            event.widget.event_generate("<<Cut>>")
        elif event.keycode == 65535:
            event.widget.event_generate("<<Clear>>")
        elif event.keycode == 65:
            event.widget.event_generate("<<SelectAll>>")


def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller
    Функция для получения абсолютного пути к файлам, необходима при работе с Dev и PyInstaller
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def clear_last_images(folder_path: str):
    """
    Функция очистки последних скаченных картинок в папку указанную пользователем. Функция выделяет фотографии с фразой
    "wbimg" и разрешением ".jpg", выделяет и удаляет фотографии.
    :param folder_path: Путь к папке указанный пользователем.
    :return:
    """
    folder_path = folder_path.replace("\\", "/")
    folder_list = os.listdir(folder_path)
    for file_name in folder_list:
        if 'wbimg' in file_name and '.jpg' in file_name:
            path = os.path.join(folder_path, file_name)
            try:
                os.remove(path)
            except FileNotFoundError as e:
                print("clear_last_images ==> " + repr(e))


def clear_cache_folder(folder_path: str):
    """
    Функция очищения файлов из кеш-папки. Программа очищает все что есть в папке указанной в "folder_path"
    :param folder_path: Путь к кеш-папке.
    :return:
    """
    folder_path = folder_path.replace("\\", "/")
    folder_list = os.listdir(folder_path)
    for file_name in folder_list:
        path = os.path.join(folder_path, file_name)
        try:
            os.remove(path)
        except FileNotFoundError as e:
            print("clear_cache_folder ==> " + repr(e))


class DROPFILES(ctypes.Structure):
    _fields_ = (('pFiles', wintypes.DWORD),
                ('pt', wintypes.POINT),
                ('fNC', wintypes.BOOL),
                ('fWide', wintypes.BOOL))


def files_to_clipboard(files_path: str):
    """
    Функция для добавления файлов в Буфер обмена. Функция копирует скаченные фотографии в Буфер обмена,
    для последующего их использования.  Функция копирует фотографии с фразой "wbimg" и разрешением ".jpg".
    :param files_path: Путь к папке, откуда требуется копировать файлы.
    :return:
    """
    files_list = []
    for file in os.listdir(files_path):
        if 'wbimg' in file and '.jpg' in file:
            files_list.append(os.path.join(files_path, file))

    offset = ctypes.sizeof(DROPFILES)
    length = sum(len(p) + 1 for p in files_list) + 1
    size = offset + length * ctypes.sizeof(ctypes.c_wchar)
    buf = (ctypes.c_char * size)()

    df = DROPFILES.from_buffer(buf)
    df.pFiles, df.fWide = offset, True
    for path in files_list:
        array_t = ctypes.c_wchar * (len(path) + 1)
        path_buf = array_t.from_buffer(buf, offset)
        path_buf.value = path
        offset += ctypes.sizeof(path_buf)
    stg = pythoncom.STGMEDIUM()
    stg.set(pythoncom.TYMED_HGLOBAL, buf)
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    try:
        win32clipboard.SetClipboardData(win32clipboard.CF_HDROP, stg.data)
    finally:
        win32clipboard.CloseClipboard()


def hide_window_by_name(window_name: str):

    """
    Функция для закрытия (СКРЫТИЯ) ненужных окон. Функция выводит все имеющиеся
    окна и выбирает окно с определённым названием.
    :param window_name: Названия окна которое необходимо скрыть.
    :return:
    """

    toplist = []
    winlist = []

    def enum_callback(hwnd, results):
        winlist.append((hwnd, win32gui.GetWindowText(hwnd)))

    win32gui.EnumWindows(enum_callback, toplist)

    for window in winlist:
        if window_name in window[1]:
            win32gui.ShowWindow(window[0], win32con.SW_HIDE)

