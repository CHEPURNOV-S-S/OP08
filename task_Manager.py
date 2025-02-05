import tkinter as tk

from task_Board import Board


class MainWindow:
    def __init__(self):
        # Создаем главное окно
        self.root = tk.Tk()
        self.root.title("Таск-менеджер")
        self.root.geometry("900x600")  # Размер окна
        self.root.configure(bg='white')

        # Добавляем кнопку "Добавить доску"
        self.add_board_button = tk.Button(
            self.root,
            text="➕ Добавить доску",
            command=self.add_new_board,
            bg="lightblue",
            fg="black",
            font=("Arial", 10),
            width=15
        )

        # Список всех досок
        self.boards = []
        self.board_width = 220  # Ширина одной доски
        self.board_spacing = 20  # Пространство между досками

        # Создаем фиксированные доски
        self.create_fixed_boards()



        # Обновляем позицию кнопки "Добавить доску"
        self.update_add_button_position()

        # Запускаем главный цикл
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    def create_fixed_boards(self):
        # Создаем фиксированные доски
        board_queue = Board(self.root, x=10, y=10, title="В очереди", is_fixed=True, base_color='lightcyan', boards=self.boards)
        board_in_progress = Board(self.root, x=250, y=10, title="В работе", is_fixed=True, base_color='chocolate', boards=self.boards)
        board_done = Board(self.root, x=500, y=10, title="Выполнено", is_fixed=True, base_color='lightgreen', boards=self.boards)
        # Добавляем доски в список
        self.boards.extend([board_queue, board_in_progress, board_done])



    def add_new_board(self):
        # Определяем позицию для новой доски
        if not self.boards:
            x_position = 10
        else:
            last_board = self.boards[-1]
            x_position = last_board.board_frame.winfo_x() + last_board.board_frame.winfo_width() + self.board_spacing

        # Проверяем, достаточно ли места на экране
        if x_position + self.board_width > self.root.winfo_width():
            # Если нет места, увеличиваем размер окна
            new_width = x_position + self.board_width + 20  # Дополнительное пространство
            self.root.geometry(f"{new_width}x600")

        # Создаем новую доску
        new_board = Board(
            self.root,
            x=x_position,
            y=10,
            title=f"Доска {len(self.boards) + 1}",
            is_fixed=False,
            base_color='lightblue',
            boards=self.boards
        )
        self.boards.append(new_board)

        # Обновляем позицию кнопки "Добавить доску"
        self.update_add_button_position()

    def update_add_button_position(self):
        # обновляем позиции всех элементов.
        self.root.update_idletasks()
        # Перемещаем кнопку "Добавить доску" вправо
        if self.boards:
            last_board = self.boards[-1]
            button_x = last_board.board_frame.winfo_x() + last_board.board_frame.winfo_width() + 10
        else:
            button_x = 10
        self.add_board_button.place(x=button_x, y=10)

    def on_close(self):
        # Обработчик закрытия окна
        if self.confirm_exit():
            self.root.destroy()

    def confirm_exit(self):
        # Подтверждение выхода
        response = self.show_custom_messagebox("Подтверждение выхода", "Вы действительно хотите выйти?")
        return response

    def show_custom_messagebox(self, title, message):
        # Создаем Toplevel окно для подтверждения
        msg_box = tk.Toplevel(self.root)
        msg_box.title(title)
        msg_box.geometry("300x150")
        msg_box.transient(self.root)
        msg_box.grab_set()
        msg_box.resizable(False, False)
        # Создаем метку для сообщения
        label = tk.Label(msg_box, text=message, font=('Consolas', 10), justify='center')
        label.pack(padx=10, pady=10)
        # Создаем кнопки Yes и No
        button_frame = tk.Frame(msg_box)
        button_frame.pack(pady=10)
        yes_button = tk.Button(button_frame, text="Да", command=lambda: self.on_yes_no_response(msg_box, True), width=10)
        yes_button.pack(side='left', padx=10)
        no_button = tk.Button(button_frame, text="Нет", command=lambda: self.on_yes_no_response(msg_box, False), width=10)
        no_button.pack(side='right', padx=10)
        # Ждем закрытия окна
        msg_box.wait_window()
        return self.response

    def on_yes_no_response(self, msg_box, response):
        self.response = response
        msg_box.destroy()


if __name__ == "__main__":
    app = MainWindow()

if __name__ == "__main__":
    app = MainWindow()