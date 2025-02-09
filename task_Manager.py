import tkinter as tk
from tkinter import font
import json
import os

from task_Board import Board
from task_Sticker import Sticker

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Таск-менеджер")
        self.root.geometry("900x600")
        self.root.configure(bg='white')

        # Список всех досок и их окон
        self.boards = []
        self.board_windows = []
        self.board_width = 220
        self.board_spacing = 20

        # Создание фиксированной левой колонки
        self.create_fixed_sidebar()

        # Создание области для досок
        self.create_main_area()

        # Настройка прокрутки колесом мыши
        self.setup_mousewheel_scroll()

        # Настройка основного layout
        self.setup_layout()

        self.data_file = "task_manager_data.json"  # Файл для хранения данных
        # Загружаем данные при запуске
        if self.load_data() is False:
            # создаём фиксированные доски, если данные не загружены
            self.create_fixed_boards()

        # Запускаем главный цикл
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    def setup_layout(self):
        """Настройка основного layout с использованием grid."""
        # Фиксируем первую колонку
        self.root.grid_columnconfigure(0, weight = 0, minsize=50)

        self.root.grid_columnconfigure(1, weight = 2)

    def create_fixed_sidebar(self):
        """Создание фиксированной левой колонки."""
        sidebar_width = 50  # Ширина фиксированной колонки
        sidebar_bg = "#f0f0f0"  # Цвет фона

        # Создаем фрейм для левой колонки
        self.sidebar = tk.Frame(self.root, width=sidebar_width, bg=sidebar_bg, bd=2, relief=tk.RIDGE)
        self.sidebar.grid(row=0, column=0, rowspan = 2, sticky="ns")
        self.sidebar.grid_propagate(False)  # Запрещаем изменение размера

        # Добавляем кнопку добавления новой доски
        add_board_button_font = font.Font(size=18, weight="bold")  # Увеличенный шрифт
        self.add_board_button = tk.Button(
            self.sidebar,
            text="+",
            font=add_board_button_font,
            command=self.add_new_board,
            bg="#4CAF50",  # Цвет фона кнопки
            fg="white",  # Цвет текста
            relief=tk.FLAT,
            width=3,  # Ширина кнопки
            height=1  # Высота кнопки
        )
        self.add_board_button.pack(pady=10)

    def create_main_area(self):
        """Создание основной области для досок."""
        # Создаем Canvas для прокрутки
        self.canvas = tk.Canvas(self.root, bg="white")
        # Убираем рамку Canvas
        self.canvas.config(highlightthickness=0)

        self.scrollbar_y = tk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollbar_x = tk.Scrollbar(self.root, orient="horizontal", command=self.canvas.xview)

        # Настройка Canvas
        self.canvas.configure(
            yscrollcommand=self.scrollbar_y.set,
            xscrollcommand=self.scrollbar_x.set
        )

        # Размещаем элементы с использованием grid
        self.canvas.grid(row=0, column=1, sticky="nsew")
        self.scrollbar_y.grid(row=0, column=2, sticky="ns")
        self.scrollbar_x.grid(row=1, column=1, sticky="ew")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        # Привязываем обработчик прокрутки
        self.canvas.bind("<Configure>", self.on_canvas_configure)

    def setup_mousewheel_scroll(self):
        """Настройка прокрутки колесом мыши."""
        # Привязываем событие колеса мыши к Canvas
        if self.canvas:
            self.canvas.bind("<MouseWheel>", self.on_mousewheel)  # Для Windows
            self.canvas.bind("<Button-4>", self.on_mousewheel)  # Для Linux (прокрутка вверх)
            self.canvas.bind("<Button-5>", self.on_mousewheel)  # Для Linux (прокрутка вниз)

            # Перехватываем события колеса мыши на дочерних виджетах
            self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
            self.canvas.bind_all("<Button-4>", self.on_mousewheel)
            self.canvas.bind_all("<Button-5>", self.on_mousewheel)

    def on_mousewheel(self, event):
        """Обработчик прокрутки колесом мыши."""
        # Получаем текущую позицию прокрутки (от 0 до 1)
        current_scroll_position = self.canvas.yview()[0]

        # Определяем направление прокрутки
        if event.num == 5 or event.delta < 0:  # Прокрутка вниз
            if current_scroll_position < 1.0:  # Проверяем, что можно прокручивать дальше
                self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:  # Прокрутка вверх
            if current_scroll_position > 0.0:  # Проверяем, что можно прокручивать вверх
                self.canvas.yview_scroll(-1, "units")


    def create_fixed_boards(self):
        # Создаем фиксированные доски через add_new_board
        board = self.add_new_board(title="В очереди", is_fixed=True, base_color='lightcyan')
        first_task_desc = "Создай список задач в доске \"В очереди\". \
Перенеси те за которые взялся на доску \"В работе\".\
После выполнения перенеси в доску \"выполнено\" или удали задачу.\
Если нужны ещё доски создай новую"
        sticker = Sticker(
            master=self.canvas,
            x=0,
            y=0,
            title="Список задач",
            description=first_task_desc,
            on_delete=board.remove_sticker,
            board=board,
            boards=self.boards
        )
        board.add_sticker(sticker)
        self.add_new_board(title="В работе", is_fixed=True, base_color='chocolate')
        self.add_new_board(title="Выполнено", is_fixed=True, base_color='lightgreen')

    def add_new_board(self, title="Доска", is_fixed=False, base_color='lightblue'):
        # Находим первую свободную позицию для новой доски
        if not self.boards:
            x_position = 10
        else:
            x_position = 10+ (self.board_width + self.board_spacing)*len(self.boards)

        # Создание новой доски
        new_board = Board(
            self.canvas,
            x=x_position,
            y=10,
            title=title,
            is_fixed=is_fixed,
            base_color=base_color,
            boards=self.boards
        )
        # Передаем ссылку на главное окно
        new_board.main_window = self
        # Привязываем события изменения размера

        new_board.board_frame.bind("<Configure>", self.on_board_resize)

        # Размещаем доску внутри Canvas
        self.board_windows.append(new_board.canvas_window_id)

        # Добавляем доску в список
        self.boards.append(new_board)

        # Обновляем scroll region
        self.schedule_update_scroll_region(scroll_to_end_x = True)

        return new_board

    def on_canvas_configure(self, _):  # type: ignore
        """Обновляет позиции досок при прокрутке Canvas."""
        for window_id in self.board_windows:
            # Получаем текущие координаты окна
            x, y = self.canvas.coords(window_id)

            # Обновляем координаты с учетом смещения прокрутки
            self.canvas.coords(window_id, x, y)

    def schedule_update_scroll_region(self,
                                      scroll_to_end_x = False):
        """
        Планирует обновление scrollregion Canvas через следующий цикл событий.
        """
        self.root.after(1, self.update_scroll_region) # type: ignore

        # Смещаем прокрутку так, чтобы новая доска была видна
        if scroll_to_end_x is True:
            self.root.after(2, self.canvas.xview_moveto, 1.0)

        # Смещаем прокрутку так, чтобы был виден последний добавленный стикер


    def on_board_resize(self, event):
        """
        Обработчик события изменения размера доски.
        """
        # print(f"Доска изменена: {event.width}x{event.height}")
        self.schedule_update_scroll_region()

    def update_scroll_region(self):
        """Обновляет регион прокрутки Canvas."""
         # Устанавливаем scroll region
        for board in self.boards:
            board.rearrange_stickers()

        bbox = self.canvas.bbox("all")
        _,_, new_width, new_height = bbox

        # вывод, для откладки
        # print(bbox)
        # print(f"self.canvas.configure(scrollregion=(0, 0, {new_width}, {new_height}))")
        self.canvas.configure(scrollregion=(0, 0, new_width+10, new_height+10))


    def on_close(self):
        # if self.confirm_exit(): # Отключил подтверждение о закрытии программы
        self.save_data()
        self.root.destroy()

    def save_data(self):
        """Сохраняет текущее состояние досок и задач в JSON-файл."""
        data = []
        for board in self.boards:
            board_data = {
                "title": board.title,
                "is_fixed": board.is_fixed,
                "base_color": board.original_bg,
                "x": board.master.coords(board.canvas_window_id)[0],
                "y": board.master.coords(board.canvas_window_id)[1],
                "stickers": [
                    {
                        "title": sticker.title,
                        "description": sticker.description,
                        "completed": bool(sticker.completion_time),
                        "relative_x": sticker.relative_x,
                        "relative_y": sticker.relative_y
                    }
                    for sticker in board.stickers
                ]
            }
            data.append(board_data)

        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def load_data(self):
        """Загружает данные из JSON-файла и восстанавливает состояние досок и задач."""
        if not os.path.exists(self.data_file):
            return  False# Если файл не существует, ничего не делаем

        with open(self.data_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        for board_data in data:
            board = self.add_new_board(
                title=board_data["title"],
                is_fixed=board_data["is_fixed"],
                base_color=board_data["base_color"]
            )
            x, y = board_data["x"], board_data["y"]

            # self.master.coords(board.canvas_window_id, x, y)

            for sticker_data in board_data["stickers"]:
                sticker = Sticker(
                    master=self.canvas,
                    x=sticker_data["relative_x"],
                    y=sticker_data["relative_y"],
                    title=sticker_data["title"],
                    description=sticker_data["description"],
                    on_delete=board.remove_sticker,
                    board=board,
                    boards=self.boards
                )
                if sticker_data["completed"]:
                    sticker.mark_completed(silent=True)
                board.add_sticker(sticker)
        # сообщаем, что данные загружены
        return True

    def confirm_exit(self):
        response = self.show_custom_messagebox("Подтверждение выхода", "Вы действительно хотите выйти?")
        return response

    def show_custom_messagebox(self, title, message):
        msg_box = tk.Toplevel(self.root)
        msg_box.title(title)
        msg_box.geometry("300x150")
        msg_box.transient(self.root)
        msg_box.grab_set()
        msg_box.resizable(False, False)
        label = tk.Label(msg_box, text=message, font=('Consolas', 10), justify='center')
        label.pack(padx=10, pady=10)
        button_frame = tk.Frame(msg_box)
        button_frame.pack(pady=10)
        yes_button = tk.Button(button_frame, text="Да", command=lambda: self.on_yes_no_response(msg_box, True), width=10)
        no_button = tk.Button(button_frame, text="Нет", command=lambda: self.on_yes_no_response(msg_box, False), width=10)
        yes_button.pack(side='left', padx=10)
        no_button.pack(side='right', padx=10)
        msg_box.wait_window()
        return self.response

    def on_yes_no_response(self, msg_box, response):
        self.response = response
        msg_box.destroy()

if __name__ == "__main__":
    app = MainWindow()