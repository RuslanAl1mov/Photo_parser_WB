import tkinter as tk
from tkinter import END

from GIF_Animation_CLASS import ImageLabel
from Parsing_machine import ParseMachine
from options import keys


import os
import sys
import threading


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def remove_last_answers():
    """
    Функция удаляет все виджеты со старыми ответами на прошлые ссылки.
    :return:
    """
    for widg in answer_widgets:
        widg.destroy()


def start_parsing():
    remove_last_answers()
    parser = ParseMachine()
    th = threading.Thread(target=parser.search_imgs,
                          args=(e.get("1.0", "end-1c"), answer_widgets, master, loading_gif_label, search_btn),
                          name="name")
    th.start()
    e.delete("1.0", END)  # очищаем запрос


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

search_btn = tk.Button(master, width=9, text='Поиск', command=start_parsing)
search_btn.grid(row=2, column=1, sticky=tk.W, pady=4)
tk.Button(master, width=9, text='Выход', command=master.destroy).grid(row=1, column=1, sticky=tk.W, pady=4)


loading_gif_label = ImageLabel(master)
loading_gif_label.grid(row=4, column=0)
loading_gif_label.load('loading.gif')
loading_gif_label.grid_remove()

master.mainloop()
