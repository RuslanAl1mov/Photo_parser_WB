import ctypes

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import tkinter as tk

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
    u = ctypes.windll.LoadLibrary("user32.dll")
    pf = getattr(u, "GetKeyboardLayout")
    return hex(pf(0)) == '0x4190419'


def keys(event):
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


def download_img():
    try:
        driver = webdriver.Chrome(executable_path=resource_path("chromedriver.exe"),
                                  options=driver_options)
        driver.get(e.get("1.0", "end-1c"))
        time.sleep(6)
        page_src = driver.page_source

        page_src = page_src.split("\"")
        img_link = "Ничего не найдено!"

        for i in page_src:
            if "images/big/1.jpg" in i:
                img_link = "https:" + i
        answer.insert(1.0, img_link)
        driver.close()
    except Exception as d:
        answer.insert(1.0, "Ошибка!")


driver_options = Options()
driver_options.add_argument("--headless")

master = tk.Tk()

tk.Label(master, text="Ссылка на страницу WB").grid(row=0)

e = tk.Text(master, height=1, width=50)
e.grid(row=0, column=0)
e.bind("<Control-KeyPress>", keys)

answer = tk.Text(master, height=1, width=50)
tk.Button(master, text='Поиск', command=download_img).grid(row=3, column=0, sticky=tk.W, pady=4)
answer.grid(row=4, column=0)
answer.bind("<Control-KeyPress>", keys)
tk.Button(master, text='Выход', command=master.destroy).grid(row=5, column=0, sticky=tk.W, pady=4)

master.mainloop()
