import tkinter as tk
from task_Board import Board

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Таск-менеджер")
        self.root.geometry("900x600")
        self.root.configure(bg='white')

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
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar_y.grid(row=0, column=1, sticky="ns")
        self.scrollbar_x.grid(row=1, column=0, sticky="ew")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Список всех досок и их окон
        self.boards = []
        self.board_windows = []
        self.board_width = 220
        self.board_spacing = 20

        # Создаем фиксированные доски
        self.create_fixed_boards()

        # Кнопка "Добавить доску"
        self.add_board_button = tk.Button(
            self.canvas,
            text="➕ Добавить доску",
            command=self.add_new_board,
            bg="lightblue",
            fg="black",
            font=("Arial", 10),
            width=15
        )
        self.canvas.create_window((800, 10), window=self.add_board_button, anchor="ne")

        # Привязываем обработчик прокрутки
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        # Запускаем главный цикл
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    def create_fixed_boards(self):
        # Создаем фиксированные доски через add_new_board
        self.add_new_board(title="В очереди", is_fixed=True, base_color='lightcyan')
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

        # Привязываем события изменения размера

        new_board.board_frame.bind("<Configure>", self.on_board_resize)

        # Размещаем доску внутри Canvas
        self.board_windows.append(new_board.canvas_window_id)

        # Добавляем доску в список
        self.boards.append(new_board)

        # Обновляем scroll region
        self.schedule_update_scroll_region()

    def on_canvas_configure(self, _):  # type: ignore
        """Обновляет позиции досок при прокрутке Canvas."""
        for window_id in self.board_windows:
            # Получаем текущие координаты окна
            x, y = self.canvas.coords(window_id)

            # Обновляем координаты с учетом смещения прокрутки
            self.canvas.coords(window_id, x, y)

    def schedule_update_scroll_region(self):
        """
        Планирует обновление scrollregion Canvas через следующий цикл событий.
        """
        self.root.after(1, self.update_scroll_region) # type: ignore

    def on_board_resize(self, event):
        """
        Обработчик события изменения размера доски.
        """
        print(f"Доска изменена: {event.width}x{event.height}")
        self.schedule_update_scroll_region()

    def update_scroll_region(self):
        """Обновляет регион прокрутки Canvas."""
         # Устанавливаем scroll region
        bbox = self.canvas.bbox("all")
        _,_, new_width, new_height = bbox

        # вывод, для откладки
        print(bbox)
        print(f"self.canvas.configure(scrollregion=(0, 0, {new_width}, {new_height}))")
        self.canvas.configure(scrollregion=(0, 0, new_width+10, new_height+10))


    def on_close(self):
        if self.confirm_exit():
            self.root.destroy()

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