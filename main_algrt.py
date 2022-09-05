import subprocess
import tkinter as tk
from tkinter import END
from tkinter import filedialog

from GIF_Animation_CLASS import ImageLabel
from Parsing_machine import ParseMachine
import options

import threading


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.iconbitmap(options.resource_path('Icon.ico'))
        self.title("Парсер Фотографий товара из WB")
        self.geometry('717x600+100+50')
        self.resizable(False, False)

        self.user_folder_path = ''
        self.answer_widgets = []

        window_header = tk.Label(self, height=2, text="Парсер WILDBERRIES", bg='purple', fg='white', font=("Arial", 15))
        window_header.pack(anchor=tk.NW, padx=8, fill=tk.X)

        choose_folder_label = tk.Label(self, height=1, text="Папка для сохранения фотографий:")
        choose_folder_label.pack(anchor=tk.NW, padx=8)

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

        f_search = tk.Frame(self)
        self.wb_link_entry = tk.Text(f_search, height=1, width=75)
        self.wb_link_entry.pack(side=tk.LEFT)
        self.wb_link_entry.bind("<Control-KeyPress>", options.keys)
        self.search_btn = tk.Button(f_search, width=9, text='Поиск', command=self.start_parsing)
        self.search_btn.pack(side=tk.LEFT, padx=10)
        f_search.pack(anchor=tk.NW, padx=10)

        self.last_link_label = tk.Label(self, height=3)
        self.last_link_label.pack(anchor=tk.W, padx=20)

        answers_links_listbox_canvas = tk.Canvas(self, borderwidth=0, background="#ffffff")
        self.answers_frame = tk.Frame(answers_links_listbox_canvas, background="#ffffff")
        self.answers_frame.bind("<Configure>",
                                lambda event, canvas=answers_links_listbox_canvas: canvas.configure(scrollregion=canvas.bbox("all")))
        vsb = tk.Scrollbar(answers_links_listbox_canvas, orient="vertical", command=answers_links_listbox_canvas.yview)
        answers_links_listbox_canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        answers_links_listbox_canvas.pack(anchor=tk.W, fill=tk.BOTH, expand=True, padx=10)
        answers_links_listbox_canvas.create_window((4, 4), window=self.answers_frame, anchor="nw")

        self.loading_gif_label = ImageLabel(self.answers_frame, bg='white')
        self.loading_gif_label.load(options.resource_path('loading.gif'))
        self.loading_gif_label.pack_forget()

        self.open_in_folder_btn = tk.Button(self, width=20, text='Открыть в папке', command=self.open_user_folder)
        self.open_in_folder_btn['state'] = tk.DISABLED
        self.open_in_folder_btn.pack(side=tk.LEFT, anchor=tk.SW, padx=15, pady=12)
        tk.Button(self, width=9, text='Выход', command=self.destroy).pack(side=tk.RIGHT, anchor=tk.SE, padx=15, pady=12)

    def start_parsing(self):
        self.remove_last_answers()
        last_link = self.wb_link_entry.get("1.0", "end-1c")
        self.last_link_label.config(text="Поиск по ссылке: " + last_link)

        parser = ParseMachine()
        th = threading.Thread(target=parser.search_imgs,
                              args=(last_link, self.answer_widgets, self.user_folder_path, self.answers_frame,
                                    self.loading_gif_label, self.search_btn), name="name")
        th.start()

        self.wb_link_entry.delete("1.0", END)  # очищаем запрос

    def remove_last_answers(self):
        """
        Функция удаляет все виджеты со старыми ответами на прошлые ссылки.
        :return:
        """
        for widg in self.answer_widgets:
            widg.destroy()

    def folder_browse_button(self):
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
        folder_path = self.user_folder_path.replace('/', '\\')
        subprocess.Popen(f'explorer /open, "{folder_path}"')


if __name__ == '__main__':
    main_window = MainWindow()
    main_window.mainloop()
