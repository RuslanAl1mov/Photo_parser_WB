from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from options import keys

from functools import partial
import pyperclip
import tkinter as tk

import os
import sys
import time


def copy_to_buffer(arguments):
    """
    Функция копирования найденной ссылки в Будфер обмена для последующего поиска ссылки в Браузере.
    :param answer_widgets: все найденные ссылки будут помещены в tk.Text виджеты и виджеты будут храниться в
    answer_widgets листе.
    :param widget_id: id виджета текста, которому принадлежит кнопка, для правильного копирования ссылки на фото.
    :return:
    """

    answer_widgets, widget_id = arguments
    pyperclip.copy(answer_widgets[widget_id].winfo_children()[0].get("1.0", "end-1c"))


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class ParseMachine:
    def __init__(self):
        driver_options = Options()
        driver_options.add_argument("--headless")
        self.driver = webdriver.Chrome(executable_path=resource_path("chromedriver.exe"),
                                       options=driver_options)

    def search_imgs(self, link_to_search: str, answer_widgets: list, answers_frame, loading_GIF_widget, main_search_bt):
        """
        Функция Парсинга страницы WB.
        1) Поиск и загрузка страницы.
        2) Раздробление найденной страницы по тегам.
        3) Поиск необходимого материала из страницы.
        4) Вывод на экран найденные варианты.
        """

        main_search_bt['state'] = tk.DISABLED
        loading_GIF_widget.pack(padx=250, pady=100)

        try:

            self.driver.get(link_to_search)

            time.sleep(6)
            page_src = self.driver.page_source

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
                    answer_widgets.append(tk.Frame(answers_frame, bg='white'))
                    text_widget_id = len(answer_widgets) - 1
                    widgets = (tk.Text(answer_widgets[-1], height=1, width=70),
                               tk.Button(answer_widgets[-1], height=1, width=9, text="Копировать",
                                         command=partial(copy_to_buffer, (answer_widgets, text_widget_id))))
                    widgets[0].bind("<Control-KeyPress>", keys)
                    widgets[0].insert('1.0', link)
                    widgets[0].pack(side=tk.LEFT, padx=10, pady=3)
                    widgets[1].pack(side=tk.LEFT, padx=10, pady=3)
                    answer_widgets[-1].pack(side=tk.TOP, anchor=tk.W)

            else:
                answer_widgets.append(tk.Text(answers_frame))
                answer_widgets[-1].pack()
                answer_widgets[-1].insert('1.0', "Ничего не найдено!")

            loading_GIF_widget.pack_forget()
            main_search_bt['state'] = tk.NORMAL

            self.close_driver()

        except Exception as d:
            answer_widgets.append(tk.Text(answers_frame))
            answer_widgets[-1].pack()
            answer_widgets[-1].insert('1.0', str("ОШИБКА!!!\n" + str(d) + "ОШИБКА!!!"))

            loading_GIF_widget.pack_forget()
            main_search_bt['state'] = tk.NORMAL

            self.close_driver()

    def close_driver(self):
        self.driver.close()
