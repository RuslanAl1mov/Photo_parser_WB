import ctypes


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