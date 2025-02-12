import tkinter as tk
import time
from tkinter import font
from tkinter import scrolledtext, simpledialog, messagebox
from datetime import datetime

from task_Sticker import Sticker

class Board:
    def __init__(self, master, x, y, title="Доска",
                 is_fixed=False, base_color=None, boards=None):
        self.board_spacing = 20
        self.original_column = None
        self.master = master

        # Ссылка на главное окно для вызова save_data
        self.main_window = None
        self.title = title
        self.stickers = []
        self.is_fixed = is_fixed  # Флаг для фиксированных досок
        self.boards = boards  # Список всех досок

        self.shadow = None  # Атрибут для хранения текущей тени

        # Список доступных цветов
        self.COLORS_ORIGINAL_BG = COLORS_HIGHLIGHT_BG.keys()

        # Устанавливаем базовый цвет
        if base_color and base_color in self.COLORS_ORIGINAL_BG:
            self.original_bg = base_color
        else:
            self.original_bg = 'lightblue'  # Цвет по умолчанию

        self.highlight_bg = COLORS_HIGHLIGHT_BG.get(self.original_bg, 'black')  # Выбираем соответствующий highlight цвет
        self.completed_bg = 'lightgreen'

        self.min_x = 10
        self.min_y = 10
        if x < self.min_x:
            x = self.min_x
        if y < self.min_y:
            y = self.min_y
        self.board_width = 220
        self.board_init_height = 75
        # Создаем фрейм доски с заданной шириной
        self.board_frame = tk.Frame(master, bg=self.original_bg, bd=2)
        #self.board_frame.place(x=x, y=y, width= self.board_width, height = self.board_init_height )
        # Добавляем доску в Canvas с помощью create_window
        self.canvas_window_id = master.create_window((x, y), window=self.board_frame, anchor="nw")
        # Title Text с выравниванием по центру и ограничением длины
        self.title_text = tk.Text(self.board_frame, height=1, width=23, relief=tk.RIDGE,
                                  font=('Consolas', 12, 'bold'), bg=self.highlight_bg)
        self.title_text.tag_configure("center", justify='center')
        self.title_text.insert("1.0", self.title)
        self.title_text.tag_add("center", "1.0", tk.END)
        self.title_text.config(state='disabled')  # Initially read-only
        self.title_text.pack(anchor='w', fill='x', padx=5, pady=5)  # Expand to full width

        # Обрабатываем событие, чтобы запретить ввод более 23 символов в заголовок.
        self.title_text.bind("<KeyRelease>", lambda event: self.validate_text_length(event, max_length=23))

        # Buttons Frame
        self.buttons_frame = tk.Frame(self.board_frame, bg=self.original_bg)
        self.buttons_frame.pack(side='top', fill='x', padx=5, pady=5)

        # Button Symbols (Unicode)
        add_symbol = "➕"
        edit_symbol = "✏️"
        info_symbol = "ℹ️"
        delete_symbol = "❌"

        # Buttons
        self.add_button = tk.Button(self.buttons_frame, text=add_symbol, command=self.add_new_sticker)
        self.edit_button = tk.Button(self.buttons_frame, text=edit_symbol, command=self.toggle_edit_board)
        self.info_button = tk.Button(self.buttons_frame, text=info_symbol, command=self.show_board_info)
        self.delete_button = tk.Button(self.buttons_frame, text=delete_symbol, command=self.confirm_delete_board)

        # Use grid for centering buttons
        self.buttons_frame.grid_columnconfigure(0, weight=1)
        self.buttons_frame.grid_columnconfigure(1, weight=1)
        self.buttons_frame.grid_columnconfigure(2, weight=1)
        self.buttons_frame.grid_columnconfigure(3, weight=1)
        self.add_button.grid(row=0, column=0, padx=2)
        self.edit_button.grid(row=0, column=1, padx=2)
        self.info_button.grid(row=0, column=2, padx=2)
        self.delete_button.grid(row=0, column=3, padx=2)

        # Drag and Drop functionality
        self.board_frame.bind("<ButtonPress-1>", self.start_move)
        self.board_frame.bind("<ButtonRelease-1>", self.stop_move)
        self.board_frame.bind("<B1-Motion>", self.on_motion)
        self.title_text.bind("<ButtonPress-1>", self.start_move)
        self.title_text.bind("<ButtonRelease-1>", self.stop_move)
        self.title_text.bind("<B1-Motion>", self.on_motion)
        self.buttons_frame.bind("<ButtonPress-1>", self.start_move)
        self.buttons_frame.bind("<ButtonRelease-1>", self.stop_move)
        self.buttons_frame.bind("<B1-Motion>", self.on_motion)

        self.last_scroll_time = time.time()

        # Editing state
        self.editing = False  # Флаг для отслеживания состояния редактирования
        self.response = None

    def start_move(self, event):
        if self.editing:
            return  # Если стикер в режиме редактирования, не начинаем перемещение
        # Получаем идентификатор окна доски в Canvas
        if hasattr(self, 'canvas_window_id'):
            # Получаем текущие координаты окна относительно Canvas
            self.start_x, self.start_y = self.master.coords(self.canvas_window_id)
        else:
            # Если canvas_window_id отсутствует, используем winfo_x и winfo_y
            self.start_x = self.board_frame.winfo_x()
            self.start_y = self.board_frame.winfo_y()

        # Сохраняем начальные координаты курсора
        self.drag_start_x = event.x_root
        self.drag_start_y = event.y_root

        # Индекс текущей доски в списке boards
        self.original_index = self.boards.index(self)

        # Подсветка при начале перемещения
        self.board_frame.config(bg=self.highlight_bg)
        self.buttons_frame.config(bg=self.highlight_bg)

    def on_motion(self, event):
        if self.editing:
            return  # Если стикер в режиме редактирования, не начинаем перемещение
        if not hasattr(self, 'start_x') or not hasattr(self, 'start_y'):
            return  # Если перемещение не начато, ничего не делаем

        # Вычисляем смещение курсора относительно начальной позиции
        delta_x = event.x_root - self.drag_start_x
        delta_y = event.y_root - self.drag_start_y

        # Вычисляем новые координаты доски
        new_x = self.start_x + delta_x
        new_y = self.start_y + delta_y

        # Ограничиваем перемещение за пределы слева и сверху
        if new_x < self.min_x:
            new_x = self.min_x
        if new_y < self.min_y:
            new_y = self.min_y

        # Проверяем, пересекает ли доска границы "колонки"
        target_index = self.find_target_column(event)
        if target_index != self.original_index:
            # Перемещаем доску в новую позицию в списке boards
            self.boards.pop(self.original_index)
            self.boards.insert(target_index, self)
            self.original_index = target_index

        # Обновляем позицию доски через Canvas.coords
        if hasattr(self, 'canvas_window_id'):
            self.master.coords(self.canvas_window_id, new_x, new_y)
            self.rearrange_other_boards()

        self.auto_scroll_canvas(event)

    def stop_move(self, event):
        if self.editing:
            return  # Если стикер в режиме редактирования, не начинаем перемещение
        # Удаляем временные атрибуты
        if hasattr(self, 'start_x'):
            del self.start_x
        if hasattr(self, 'start_y'):
            del self.start_y
        if hasattr(self, 'drag_start_x'):
            del self.drag_start_x
        if hasattr(self, 'drag_start_y'):
            del self.drag_start_y

        # Возвращаем исходный цвет
        self.board_frame.config(bg=self.original_bg)
        self.buttons_frame.config(bg=self.original_bg)

        # Перемещаем доску к верху окна (по минимальной координате y)
        if hasattr(self, 'canvas_window_id'):
            # Перемещаем доску в ближайшую доступную позицию
            self.rearrange_other_boards()
            target_index = self.find_target_column(event)
            x_position = target_index * (self.board_width + self.board_spacing) + 10
            self.master.coords(self.canvas_window_id, x_position, 10)

    def find_target_column(self, event):
        """Определяет целевую колонку для доски."""
        if hasattr(self, 'canvas_window_id'):
            # Получаем текущие координаты окна доски относительно Canvas
            x, y = self.master.coords(self.canvas_window_id)
            board_center_x = x + self.board_frame.winfo_width() // 2
        else:
            # Если canvas_window_id отсутствует, используем winfo_x как резервный вариант
            board_center_x = self.board_frame.winfo_x() + self.board_frame.winfo_width() // 2

        # Вычисляем индекс целевой колонки
        target_index = int(board_center_x // (self.board_width + self.board_spacing))  # Явное преобразование в int

        # Ограничиваем индекс, чтобы он не выходил за пределы списка досок
        if target_index > len(self.boards) - 1:
            target_index = len(self.boards) - 1

        return target_index

    def auto_scroll_canvas(self, event):
        """Автоматическая прокрутка Canvas, если стикер находится у края."""
        # Проверяем, прошло ли достаточно времени с момента последней прокрутки
        current_time = time.time()
        if hasattr(self, "last_scroll_time"):
            if current_time - self.last_scroll_time < 0.1:  # Задержка 0.1 секунды
                return

        self.last_scroll_time = current_time

        # Получаем координаты курсора относительно Canvas
        canvas = self.master
        # Задаем зону активации прокрутки (например, 20 пикселей от края)
        scroll_zone = 50

        # Прокрутка по горизонтали
        canvas_width = canvas.winfo_width()  # Получаем ширину
        cursor_x = event.x_root - canvas.winfo_rootx()
        current_x_scroll_position = canvas.xview()[0]

        # print(f"cursor_x:y: {cursor_x}:{cursor_y}")
        # Прокрутка влево
        if cursor_x < scroll_zone:
            if current_x_scroll_position > 0.0:
                canvas.xview_scroll(-1, "units")

        # Прокрутка вправо
        elif cursor_x > canvas_width - scroll_zone:
            if current_x_scroll_position < 1.0:
                canvas.xview_scroll(1, "units")

    def rearrange_other_boards(self):
        """Перераспределяет другие доски в списке boards."""

        # Обновляем позиции досок
        for i, board_current in enumerate(self.boards):
            if board_current != self:
                x_position = i * (self.board_width + self.board_spacing) + 10
                y_position = 10
                board_current.master.coords(board_current.canvas_window_id, x_position, y_position)

    def update_stickers_position(self, board_new_x, board_new_y):
        # Обновляем позиции всех стикеров относительно новой позиции доски

        for sticker in self.stickers:
            sticker_x = board_new_x + sticker.relative_x
            sticker_y = board_new_y + sticker.relative_y
            sticker.sticker_frame.place(x=sticker_x, y=sticker_y)


    def add_new_sticker(self):
        # Определяем начальную позицию для нового стикера относительно доски
        sticker_relative_x = 5
        sticker_relative_y = self.board_frame.winfo_height() + 10

        # Вычисляем абсолютные координаты стикера
        sticker_x = self.board_frame.winfo_x() + sticker_relative_x
        sticker_y = self.board_frame.winfo_y() + sticker_relative_y

        # Создаем новый стикер без названия и описания
        new_sticker = Sticker(
            self.master,
            sticker_x,
            sticker_y,
            title="",
            description="",
            on_delete=self.remove_sticker,  # Передаем коллбэк
            board = self,
            boards = self.boards
        )
        # Передаем ссылку на главное окно
        new_sticker.main_window = self.main_window
        # Сохраняем относительные координаты стикера
        new_sticker.relative_x = sticker_relative_x
        new_sticker.relative_y = sticker_relative_y

        # Добавляем стикер в список стикеров доски
        self.add_sticker(new_sticker)

        # Включаем режим редактирования для нового стикера
        new_sticker.toggle_edit_task()

    def get_insert_index(self, new_sticker_center_y):
        if new_sticker_center_y == -1:
            return len(self.stickers)
        for i, sticker in enumerate(self.stickers):
            if sticker.sticker_frame.winfo_exists():  # Проверяем, существует ли виджет
                sticker_y = sticker.sticker_frame.winfo_y()
                sticker_height = sticker.sticker_frame.winfo_height()
                if new_sticker_center_y < sticker_y + sticker_height // 2:
                    return i
        return len(self.stickers)

    def insert_sticker(self, sticker, sticker_center_y):
        if not sticker.sticker_frame.winfo_exists():
            self.rearrange_stickers()
            return  # Если стикер уже удален, ничего не делаем

        # Вставляем стикер в указанную позицию
        new_sticker_index = self.get_insert_index(sticker_center_y)

        # Проверяем есть ли стикер в списке, и ищем его индекс
        try:
            new_sticker_old_index = self.stickers.index(sticker)
        except ValueError:
            # стикера в списке нет.
            new_sticker_old_index = None

        if new_sticker_old_index is not None:
            if new_sticker_old_index != new_sticker_index:
                # Если стикер есть, и индекс не совпадает, удаляем из списка,
                self.stickers.pop (new_sticker_old_index)
                self.stickers.insert(new_sticker_index, sticker)
                self.update_height()
            else:
                # Если стикер есть, и индексы совпадает, ничего не делаем,
                pass
        else:
            self.stickers.insert(new_sticker_index, sticker)
            self.update_height()

        self.rearrange_stickers()


    def toggle_edit_board(self):

        if not self.editing:
            # Включаем режим редактирования
            self.editing = True
            self.edit_button.config(relief=tk.SUNKEN)  # Кнопка становится зажатой
            # Показываем палитру цветов
            self.show_color_palette()
            if self.is_fixed:
                # Если доска фиксированная, разрешаем только смену цвета
                return
            # Делаем поля редактируемыми
            self.title_text.config(state='normal')
            self.title_text.focus_set()
            self.title_text.see('1.0')  # Прокручиваем к началу текста

        else:
            # Выключаем режим редактирования и сохраняем изменения
            self.editing = False
            self.edit_button.config(relief=tk.RAISED)  # Кнопка становится обычной
            # Сохраняем новые значения
            new_title = self.title_text.get('1.0', 'end').strip()
            if new_title:
                self.title = new_title
                self.title_text.delete('1.0', tk.END)  # Удаляем весь текст
                self.title_text.insert("1.0", self.title)
                self.title_text.tag_add("center", "1.0", tk.END)
            else:
                self.title_text.delete('1.0', tk.END)  # Удаляем весь текст
                self.title_text.insert("1.0", self.title)
                self.title_text.tag_add("center", "1.0", tk.END)
            self.title_text.config(state='disabled')
            self.title_text.yview_moveto(0)  # Прокручиваем к началу текста
            # Закрываем палитру цветов
            if hasattr(self, 'color_palette') and self.color_palette:
                self.color_palette.destroy()
            if self.main_window:
                self.main_window.save_data()

    def show_color_palette(self):
        # Создаем Toplevel окно для палитры цветов
        self.color_palette = tk.Toplevel(self.master)
        self.color_palette.title("Выбор цвета")

        # Устанавливаем размер окна
        palette_width = 175
        palette_height = 75
        self.color_palette.geometry(
            f"{palette_width}x{palette_height}+{self.board_frame.winfo_rootx() + self.board_frame.winfo_width()}+{self.board_frame.winfo_rooty()}")


        # Блокируем возможность изменения размеров окна
        self.color_palette.resizable(False, False)

        # Создаем палитру цветов
        colors = COLORS_ORIGINAL_BG

        color_buttons_frame = tk.Frame(self.color_palette)
        color_buttons_frame.pack(pady=5)

        for i, color in enumerate(colors):
            button = tk.Button(color_buttons_frame, bg=color, width=2, height=1,
                               command=lambda c=color: self.change_board_color(c))
            button.grid(row=i // 5, column=i % 5, padx=2, pady=2)

    def change_board_color(self, color):
        self.original_bg = color
        self.highlight_bg = COLORS_HIGHLIGHT_BG[color]
        self.board_frame.config(bg = self.original_bg)
        self.title_text.config(bg = self.highlight_bg)
        self.buttons_frame.config(bg = self.original_bg)
        if self.main_window:
            self.main_window.save_data()


    def show_board_info(self):
        count_sticker = len (self.stickers)
        info = f"Задач на доске: {count_sticker}"
        self.rearrange_stickers()
        self.show_custom_messagebox("Информация о доске", info)

    def confirm_delete_board(self):
        if self.is_fixed:
            # Если доска фиксированная, нельзя её удалить
            self.show_custom_messagebox("Ошибка удаления", "Фиксированную доску нельзя удалить.")
            return

        response = self.custom_messagebox_askyesno("Подтверждение удаления",
                                                   f"Вы действительно хотите удалить доску '{self.title}'?")
        if response:
            self.delete_board()

    def delete_board(self):
        board_index = self.boards.index(self)
        self.boards.pop(board_index)
        self.board_frame.destroy()
        self.rearrange_other_boards()
        if self.main_window:
            self.main_window.save_data()


    def validate_text_length(self, event, max_length=100):
        text_widget = event.widget
        current_text = text_widget.get("1.0", tk.END)
        if len(current_text) > max_length:
            text_widget.delete(f"1.{len(current_text) - 1}", tk.END)
            self.title_text.tag_add("center", "1.0", tk.END)
        if '\n' in current_text:
            current_text = current_text.replace('\n', '')  # Удаляем символы переноса строки
            text_widget.delete("1.0", tk.END)  # Удаляем весь текст
            text_widget.insert("1.0", current_text[:max_length])  # Вставляем текст без переносов строк
            self.title_text.tag_add("center", "1.0", tk.END)

    def show_custom_messagebox(self, title, message):
        # Создаем Toplevel окно
        msg_box = tk.Toplevel(self.master)
        msg_box.title(title)

        # Устанавливаем размер окна
        board_width = self.board_frame.winfo_width()
        msg_box.geometry(
            f"{225}x{106}+{self.board_frame.winfo_rootx() + board_width}+{self.board_frame.winfo_rooty()}")

        # Делаем окно модальным
        msg_box.transient(self.master)
        msg_box.grab_set()

        # Блокируем возможность изменения размеров окна
        msg_box.resizable(False, False)

        # Создаем метку для сообщения с поддержкой многострочного текста
        label = tk.Label(msg_box, text=message, font=('Consolas', 10), justify='center', wraplength=board_width - 20)
        label.pack(padx=2, pady=2, expand=True, fill='both')

        # Создаем кнопку OK
        ok_button = tk.Button(msg_box, text="OK", command=msg_box.destroy, width=10)
        ok_button.pack(pady=5)

        # Центрируем кнопку OK
        ok_button.focus_set()
        ok_button.bind("<Return>", lambda event: msg_box.destroy())

        # Ждем закрытия окна
        msg_box.wait_window()

    def custom_messagebox_askyesno(self, title, message):
        # Создаем Toplevel окно
        msg_box = tk.Toplevel(self.master)
        msg_box.title(title)

        # Устанавливаем размер окна как размер доски
        board_width = self.board_frame.winfo_width()
        msg_box.geometry(
            f"{225}x{106}+{self.board_frame.winfo_rootx() + board_width}+{self.board_frame.winfo_rooty()}")

        # Делаем окно модальным
        msg_box.transient(self.master)
        msg_box.grab_set()

        # Блокируем возможность изменения размеров окна
        msg_box.resizable(False, False)

        # Создаем метку для сообщения с поддержкой многострочного текста
        label = tk.Label(msg_box, text=message, font=('Consolas', 10), justify='center', wraplength=board_width - 20)
        label.pack(padx=2, pady=2, expand=True, fill='both')

        # Создаем кнопки Yes и No
        button_frame = tk.Frame(msg_box)
        button_frame.pack(pady=5)

        yes_button = tk.Button(button_frame, text="Да", command=lambda: self.on_yes_no_response(msg_box, True),
                               width=10)
        yes_button.pack(side='left', padx=5)

        no_button = tk.Button(button_frame, text="Нет", command=lambda: self.on_yes_no_response(msg_box, False),
                              width=10)
        no_button.pack(side='right', padx=5)

        # Центрируем кнопки
        yes_button.focus_set()
        yes_button.bind("<Return>", lambda event: self.on_yes_no_response(msg_box, True))
        no_button.bind("<Return>", lambda event: self.on_yes_no_response(msg_box, False))

        # Ждем закрытия окна
        msg_box.wait_window()
        return self.response

    def on_yes_no_response(self, msg_box, response):
        self.response = response
        msg_box.destroy()

    def set_height(self, height):
        self.board_frame.config(height=height)

    def rearrange_stickers(self):
        # Перераспределяем стикеры по вертикали.
        # Фильтруем только существующие стикеры
        self.stickers = [sticker for sticker in self.stickers if sticker.sticker_frame.winfo_exists()]
        sticker_height = 140  # Высота каждого стикера
        spacing = 5  # Отступ между стикерами

        # Обновляем высоту доски после перераспределения
        self.update_height()

        for i, sticker in enumerate(self.stickers):
            # Вычисляем новую позицию для каждого стикера
            sticker_x = 5  # Отступ слева
            sticker_y = self.board_init_height + i * (sticker_height + spacing)

            # Обновляем относительные координаты стикера
            sticker.relative_x = sticker_x
            sticker.relative_y = sticker_y
            # Размещаем стикер на доске
            sticker.sticker_frame.place(in_=self.board_frame, x=sticker_x, y=sticker_y)
            # Поднимаем стикер на передний план
            sticker.sticker_frame.lift()


    def add_sticker(self, sticker):
        if sticker not in self.stickers:  # Проверяем, что стикер еще не добавлен
            self.stickers.append(sticker)
            self.update_height()
            # Размещаем стикер напрямую на board_frame
            self.rearrange_stickers()
            if self.main_window:
                self.main_window.save_data()

    def remove_sticker(self, sticker):
        if sticker in self.stickers:
            self.stickers.remove(sticker)
            self.update_height()
            self.rearrange_stickers()
            if self.main_window:
                self.main_window.save_data()

    def update_height(self):
        # return
        # Обновляем высоту доски в зависимости от количества стикеров
        num_stickers = len(self.stickers)
        new_height = self.board_init_height + num_stickers * 145  # Каждый стикер занимает примерно 150 пикселей

        # Обновляем размеры через Canvas
        self.master.itemconfig(self.canvas_window_id, height=new_height)
        # # Обновляем высоту через .place()
        # current_x = self.board_frame.winfo_x()
        # current_y = self.board_frame.winfo_y()
        # self.board_frame.place(x=current_x, y=current_y, width=self.board_width, height=new_height)

# Определение цветов

COLORS_HIGHLIGHT_BG = {
    'lightgreen': 'green',
    'lightblue': 'blue',
    'lightpink': 'pink',
    'lightcoral': 'coral',
    'lightseagreen': 'seagreen',
    'lightsteelblue': 'steelblue',
    'lightskyblue': 'skyblue',
    'lightcyan': 'cyan',
    'lavender': 'purple',
    'chocolate':'chocolate4',
}

COLORS_ORIGINAL_BG = COLORS_HIGHLIGHT_BG.keys()

