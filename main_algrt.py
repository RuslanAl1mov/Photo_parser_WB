import ctypes
from tkinter import END

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import tkinter as tk

import pyperclip
from functools import partial

import os
import sys
import time


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def is_ru_lang_keyboard(self):
    """
    Функция проверяет, какая раскладка стоит при Копипасте из(в) строку
    :param self:
    :return: Вариант раскладки на данный момент времени
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


def remove_last_answers():
    """
    Функция удаляет все виджеты со старыми ответами на прошлые ссылки.
    :return:
    """
    for widg in answer_widgets:
        widg.destroy()


def copy_to_buffer(widget_id):
    """
    Функция копирования найденной ссылки в Будфер обмена для последующего поиска ссылки в Браузере.
    :param widget_id: id виджета текста, которому принадлежит кнопка, для правильного копирования ссылки на фото.
    :return:
    """
    pyperclip.copy(answer_widgets[widget_id].get("1.0", "end-1c"))


def download_img():
    """
    Функция Парсинга страницы WB.
    1) Поиск и загрузка старницы.
    2) Раздробление найденной страницы по тегам.
    3) Поиск необходимого материала из страницы.
    4) Вывод на экран найденные варианты.
    :return:
    """

    remove_last_answers()

    try:
        driver = webdriver.Chrome(executable_path=resource_path("chromedriver.exe"),
                                  options=driver_options)
        driver.get(e.get("1.0", "end-1c"))
        e.delete("1.0", END)  # очищаем запрос
        time.sleep(6)
        page_src = driver.page_source

        page_src = page_src.split("\"")
        imgs_links = []
        for i in page_src:  # Поиск необходимых нам фото по общему параметру "images/big/"
            if "images/big/" in i:
                img_link = "https:" + i
                if img_link not in imgs_links:
                    imgs_links.append(img_link)

        if len(imgs_links) != 0:
            row_id = 6
            for link in imgs_links:  # Вывод найденных ответов в окно приложения.
                row_id += 1
                answer_widgets.append(tk.Text(master, height=1, width=70))
                text_widget_id = len(answer_widgets)-1
                answer_widgets.append(tk.Button(master, height=1, width=9, text="Копировать",
                                                command=partial(copy_to_buffer, text_widget_id)))

                answer_widgets[-1].grid(row=row_id, column=1)
                answer_widgets[-2].grid(row=row_id, column=0)
                answer_widgets[-2].bind("<Control-KeyPress>", keys)
                answer_widgets[-2].insert('1.0', link)

        else:
            answer_widgets.append(tk.Text(master, height=1, width=70))
            answer_widgets[-1].grid(row=6, column=0)
            answer_widgets[-1].insert('1.0', "Ничего не найдено!")

        driver.close()
    except Exception as d:
        answer_widgets.append(tk.Text(master, height=17, width=70))
        answer_widgets[-1].grid(row=6, column=0)
        answer_widgets[-1].insert('1.0', str("ОШИБКА!!!\n" + str(d) + "ОШИБКА!!!"))


driver_options = Options()
driver_options.add_argument("--headless")

answer_widgets = []

master = tk.Tk()
master.iconbitmap(resource_path('Icon.ico'))
master.title("Парсер Фотографий товара из WB")
master.geometry('717x400+100+50')
master.resizable(False, False)

tk.Label(master, height=2, text="Ссылка на страницу товара WB").grid(row=1, column=0)

e = tk.Text(master, height=1, width=80)
e.grid(row=2, column=0)
e.bind("<Control-KeyPress>", keys)

tk.Label(master, height=2).grid(row=3, column=0)

tk.Button(master, width=9, text='Поиск', command=download_img).grid(row=2, column=1, sticky=tk.W, pady=4)
tk.Button(master, width=9, text='Выход', command=master.destroy).grid(row=1, column=1, sticky=tk.W, pady=4)

master.mainloop()
