import ctypes
import sys
import os


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
    возможности пользоваться горячими клавишами при русской расскладке клавиатуры, нам необходимо проверять на
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