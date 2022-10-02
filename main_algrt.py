import subprocess
import tkinter as tk
from tkinter import END
from tkinter import filedialog

from GIF_Animation_CLASS import ImageLabel
from Parsing_machine import ParseMachine
import options

import threading


"""
Модуль с классом главного окна приложения.
"""


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.iconbitmap(options.resource_path('Icon.ico'))
        self.title("Парсер Фотографий товара из WB")
        self.geometry('717x600+100+50')
        self.resizable(False, False)

        self.user_folder_path = ''
        self.answer_widgets = []

        # Заголовок окна
        window_header = tk.Label(self, height=2, text="Парсер WILDBRS", bg='purple', fg='white', font=("Arial", 15))
        window_header.pack(anchor=tk.NW, padx=8, fill=tk.X)

        choose_folder_label = tk.Label(self, height=1, text="Папка для сохранения фотографий:")
        choose_folder_label.pack(anchor=tk.NW, padx=8)

        # Форма для выбора папки для сохранения фотографий
        folder_browser_frame = tk.Frame(self)
        self.new_folder_path = tk.StringVar()
        self.folder_path_label = tk.Label(folder_browser_frame, justify=tk.LEFT, width=86, height=1,
                                          text="Не указано...", bg='white',  borderwidth=1, relief=tk.SUNKEN)
        self.folder_path_label.pack(side=tk.LEFT, padx=7)
        choose_folder_btn = tk.Button(folder_browser_frame, text="Выбрать ...", width=9,
                                      command=self.folder_browse_button)
        choose_folder_btn.pack(side=tk.LEFT)
        folder_browser_frame.pack(anchor=tk.W, padx=5)

        insert_web_link_label = tk.Label(self, height=1, text="Ссылка на страницу товара WB:")
        insert_web_link_label.pack(anchor=tk.NW, padx=8)

        # Форма ввода ссылки страницы товара для парсинга
        f_search = tk.Frame(self)
        self.wb_link_entry = tk.Text(f_search, height=1, width=75)
        self.wb_link_entry.pack(side=tk.LEFT)
        self.wb_link_entry.bind("<Control-KeyPress>", options.keys)
        self.search_btn = tk.Button(f_search, width=9, text='Поиск', command=self.start_parsing)
        self.search_btn.pack(side=tk.LEFT, padx=10)
        f_search.pack(anchor=tk.NW, padx=10)

        # Виджет показывающий последнюю используемую ссылку
        self.last_link_label = tk.Label(self, height=3)
        self.last_link_label.pack(anchor=tk.W, padx=20)

        # Форма Canvas для вывода в нее форм найденных картинок товара
        answers_links_listbox_canvas = tk.Canvas(self, borderwidth=0, background="#ffffff")
        self.answers_frame = tk.Frame(answers_links_listbox_canvas, background="#ffffff")
        self.answers_frame.bind("<Configure>",
                                lambda event, canvas=answers_links_listbox_canvas: canvas.configure(scrollregion=canvas.bbox("all")))
        vsb = tk.Scrollbar(answers_links_listbox_canvas, orient="vertical", command=answers_links_listbox_canvas.yview)
        answers_links_listbox_canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        answers_links_listbox_canvas.pack(anchor=tk.W, fill=tk.BOTH, expand=True, padx=10)
        answers_links_listbox_canvas.create_window((4, 4), window=self.answers_frame, anchor="nw")

        # Виджет хранящий Анимацию загрузки парсера в виде GIF.
        self.loading_gif_label = ImageLabel(self.answers_frame, bg='white')
        self.loading_gif_label.load(options.resource_path('loading.gif'))
        self.loading_gif_label.pack_forget()

        # Кнопка открытия выбранной пользователем папки с сохраненными фотографиями
        self.open_in_folder_btn = tk.Button(self, width=20, text='Открыть в папке', command=self.open_user_folder)
        self.open_in_folder_btn['state'] = tk.DISABLED
        self.open_in_folder_btn.pack(side=tk.LEFT, anchor=tk.SW, padx=15, pady=12)

        # Кнопка для копирования в буфер сохраненных картинок
        self.copy_imgs_from_folder_btn = tk.Button(self, text='Копировать сохраненные картинки', state=tk.DISABLED)
        self.copy_imgs_from_folder_btn.pack(side=tk.LEFT, anchor=tk.S, pady=12)

        # Кнопка выхода и закрытия приложения
        exit_btn = tk.Button(self, width=9, text='Выход', command=self.destroy)
        exit_btn.pack(side=tk.RIGHT, anchor=tk.SE, padx=15, pady=12)

    def start_parsing(self):
        """
        Функция старта парсинга страницы.
        - Запуск 3-х параллельных потоков:
            1. Очистка кеша скачанных фотографий (.cache).
            2. Очистка/удалений старых, скачанных файлов.
            3. Запуск потока с парсером.
        - Очистка строки ввода ссылки страницы для парсинга.
        :return:
        """
        self.remove_last_answers()

        last_link = self.wb_link_entry.get("1.0", "end-1c")
        if last_link != '':
            self.last_link_label.config(text="Поиск по ссылке: " + last_link)

            # Поток 1.
            try:
                cache_cleaner_thread = threading.Thread(target=options.clear_cache_folder,
                                                        args=(options.resource_path('.cache'),))
                cache_cleaner_thread.start()
            except Exception as e:
                print(repr(e))

            # Поток 2.
            try:
                last_dwnld_imgs_cleaner_thread = threading.Thread(target=options.clear_last_images,
                                                                  args=(self.user_folder_path,))
                last_dwnld_imgs_cleaner_thread.start()
            except Exception as e:
                print(repr(e))

            # Поток 3.
            try:
                parser = ParseMachine()
                th = threading.Thread(target=parser.search_imgs,
                                      args=(last_link, self.answer_widgets, self.user_folder_path, self.answers_frame,
                                            self.loading_gif_label, self.search_btn, self.copy_imgs_from_folder_btn),
                                      name="name")
                th.start()
            except Exception as e:
                print(repr(e))

            self.wb_link_entry.delete("1.0", END)  # очищаем запрос

    def remove_last_answers(self):
        """
        Функция удаляет все виджеты со старыми ответами на прошлые ссылки.
        :return:
        """
        for widg in self.answer_widgets:
            widg.destroy()

    def folder_browse_button(self):
        """
        Функция открывает Проводник для выбора папки для сохранения фотографий.
        - Если папка выбрана, активируется кнопка "Открыть в папке".
        :return:
        """
        # Allow user to select a directory and store it in global var
        # called folder_path
        filename = filedialog.askdirectory()
        self.new_folder_path.set(filename)
        if filename != '':
            self.folder_path_label.config(text=filename)
            self.user_folder_path = filename
            # Разблокируем кнопку "Показать в папке" если указан путь к файлу.
            self.open_in_folder_btn['state'] = tk.NORMAL

    def open_user_folder(self):
        """
        Функция открывает папку, выбранную пользователем для сохранения скачанных картинок.
        :return:
        """
        folder_path = self.user_folder_path.replace('/', '\\')
        subprocess.Popen(f'explorer /open, "{folder_path}"')


if __name__ == '__main__':
    main_window = MainWindow()
    main_window.mainloop()
