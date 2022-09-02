import tkinter as tk
from tkinter import END
from tkinter import filedialog

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
    last_link = e.get("1.0", "end-1c")
    last_link_label.config(text="Поиск по ссылке: " + last_link)
    parser = ParseMachine()
    th = threading.Thread(target=parser.search_imgs,
                          args=(last_link, answer_widgets, answers_frame, loading_gif_label, search_btn),
                          name="name")
    th.start()
    e.delete("1.0", END)  # очищаем запрос


answer_widgets = []

master = tk.Tk()
master.iconbitmap(resource_path('Icon.ico'))
master.title("Парсер Фотографий товара из WB")
master.geometry('717x600+100+50')
master.resizable(False, False)


tk.Label(master, height=2, text="Парсер WILDBERRIES", bg='purple', fg='white', font=("Arial", 15)).pack(anchor=tk.NW, padx=8, fill=tk.X)


def browse_button():
    # Allow user to select a directory and store it in global var
    # called folder_path
    global folder_path
    filename = filedialog.askdirectory()
    folder_path.set(filename)
    print(filename)


tk.Label(master, height=1, text="Папка для сохранения фотографий:").pack(anchor=tk.NW, padx=8)

folder_browser_frame = tk.Frame(master)
folder_path = tk.StringVar()
folder_path_label = tk.Label(folder_browser_frame, width=86, height=1, textvariable=folder_path, justify=tk.LEFT,
                             bg='white', borderwidth=1, relief=tk.SUNKEN)
folder_path_label.pack(side=tk.LEFT, padx=7)
button2 = tk.Button(folder_browser_frame, text="Выбрать ...", width=9, command=browse_button)
button2.pack(side=tk.LEFT)
folder_browser_frame.pack(anchor=tk.W, padx=5)

tk.Label(master, height=1, text="Ссылка на страницу товара WB:").pack(anchor=tk.NW, padx=8)


f_search = tk.Frame(master)
e = tk.Text(f_search, height=1, width=75)
e.pack(side=tk.LEFT)
e.bind("<Control-KeyPress>", keys)

search_btn = tk.Button(f_search, width=9, text='Поиск', command=start_parsing)
search_btn.pack(side=tk.LEFT, padx=10)
f_search.pack(anchor=tk.NW, padx=10)

last_link_label = tk.Label(master, height=3)
last_link_label.pack(anchor=tk.W, padx=20)

canvas = tk.Canvas(master, borderwidth=0, background="#ffffff")
answers_frame = tk.Frame(canvas, background="#ffffff")
vsb = tk.Scrollbar(canvas, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=vsb.set)
vsb.pack(side="right", fill="y")
canvas.pack(anchor=tk.W, fill=tk.BOTH, expand=True, padx=10)
canvas.create_window((4, 4), window=answers_frame, anchor="nw")
answers_frame.bind("<Configure>", lambda event, canvas=canvas: canvas.configure(scrollregion=canvas.bbox("all")))

loading_gif_label = ImageLabel(answers_frame, bg='white')
loading_gif_label.pack()
loading_gif_label.load(resource_path('loading.gif'))
loading_gif_label.pack_forget()

open_in_folder_btn = tk.Button(master, width=20, text='Открыть в папке', command=None)
open_in_folder_btn['state'] = tk.DISABLED
open_in_folder_btn.pack(side=tk.LEFT, anchor=tk.SW, padx=15, pady=12)
tk.Button(master, width=9, text='Выход', command=master.destroy).pack(side=tk.RIGHT, anchor=tk.SE, padx=15, pady=12)


master.mainloop()
