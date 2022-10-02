import threading

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import options

from functools import partial
import pyperclip
import tkinter as tk
import httplib2

import time
import os


def copy_to_buffer(arguments):
    """
    Функция копирования найденной ссылки в Буфер обмена для последующего поиска ссылки в Браузере.
    :param arguments: Кортеж виджетов.
    :return:
    """

    answer_widgets, widget_id = arguments
    pyperclip.copy(answer_widgets[widget_id].winfo_children()[0].get("1.0", "end-1c"))


class ParseMachine:
    def __init__(self):
        driver_options = Options()
        driver_options.add_argument("--headless")
        self.driver = webdriver.Chrome(executable_path=options.resource_path("chromedriver.exe"),
                                       options=driver_options)

    def search_imgs(self, link_to_search: str, answer_widgets: list, folder_path_to_download_img: str, answers_frame,
                    loading_GIF_widget, main_search_bt, copy_loaded_imgs_btn):
        """
        Функция Парсинга страницы WB.
        1) Поиск и загрузка страницы.
        2) Раздробление найденной страницы по тегам.
        3) Поиск необходимого материала из страницы.
        4) Если имеется ссылка на папку для скачивания картинок("folder_path_to_download_img"), то скачивает картинки
        4) Вывод на экран найденных ссылок с возможностью скопировать каждую по-отдельности.
        """

        main_search_bt['state'] = tk.DISABLED
        copy_loaded_imgs_btn['state'] = tk.DISABLED
        loading_GIF_widget.pack(padx=250, pady=100)

        try:
            self.driver.get(link_to_search)

            time.sleep(6)
            page_src = self.driver.page_source

            page_src = page_src.split("\"")
            imgs_links = []
            for i in page_src:  # Поиск необходимых нам фото по общему параметру "/big/"
                if "/big/" in i:
                    img_link = "https:" + i
                    if img_link not in imgs_links:
                        imgs_links.append(img_link)

                        # Скачиваем фото, если указана папка для скачивания
                        if folder_path_to_download_img != '':
                            threading.Thread(target=self.download_image, name='download_img',
                                             args=(img_link, len(imgs_links), folder_path_to_download_img)).start()

            if folder_path_to_download_img != '':
                threading.Thread(target=self.activate_copy_images_btn, args=(folder_path_to_download_img,
                                                                             copy_loaded_imgs_btn)).start()

            if len(imgs_links) != 0:
                row_id = 6
                for link in imgs_links:  # Упаковываем найденные ссылки в виджеты
                    row_id += 1
                    answer_widgets.append(tk.Frame(answers_frame, bg='white'))
                    text_widget_id = len(answer_widgets) - 1
                    widgets = (tk.Text(answer_widgets[-1], height=1, width=70),
                               tk.Button(answer_widgets[-1], height=1, width=9, text="Копировать",
                                         command=partial(copy_to_buffer, (answer_widgets, text_widget_id))))
                    widgets[0].bind("<Control-KeyPress>", options.keys)
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

    def download_image(self, link, image_number, download_path):
        """
        Функция используется для скачивания фотографий/файлов по ссылке из интернета.
        :param link: Ссылка на фото/файл.
        :param image_number: Номер картинки по счету, чтобы не повторяться.
        :param download_path: Ссылка на папку, куда скачивать фото/файл(выбирается пользователем).
        :return:
        """

        h = httplib2.Http(options.resource_path('.cache'))
        response, content = h.request(link)
        out = open(f'{download_path}/wbimg {image_number}.jpg', 'wb')
        out.write(content)
        out.close()

    def activate_copy_images_btn(self, folder_path: str, button_to_activate: tk.Button):
        """
        Функция проверки скачаны ли фотографии из страницы, если скачаны, активирует кнопку "Копировать сохраненные
        картинки".
        :param folder_path: путь к папке в которой сохраняются файлы для копирования.
        :param button_to_activate: Кнопа, которую надо активировать после проверки условий.
        :return:
        """
        time.sleep(3)
        for i in range(7):
            folder_path = folder_path.replace("\\", "/")
            folder_list = os.listdir(folder_path)
            number_of_loaded_images = 0
            for file_name in folder_list:
                if 'wbimg' in file_name and '.jpg' in file_name:
                    number_of_loaded_images += 1
            if len(os.listdir(options.resource_path('.cache'))) == number_of_loaded_images:
                button_to_activate.config(command=partial(options.files_to_clipboard, folder_path),
                                          state=tk.NORMAL)
            else:
                time.sleep(3)

    def close_driver(self):
        """
        Функция для закрытия драйвера после завершения работы с ним.
        :return:
        """
        self.driver.close()
