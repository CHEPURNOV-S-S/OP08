import tkinter as tk
from tkinter import scrolledtext
import datetime

from task_Board import Board

class MainWindow:
    def __init__(self):
        # Создаем главное окно
        self.root = tk.Tk()
        self.root.title("Таск-менеджер")
        self.root.geometry("800x600")  # Размер окна
        self.root.configure(bg='white')

        # Список всех досок
        self.boards = []

        # Создаем фиксированные доски
        self.create_fixed_boards()

        # Запускаем главный цикл
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    def create_fixed_boards(self):
        # Создаем фиксированные доски
        board_queue = Board(self.root, x=10, y=10, title="В очереди", is_fixed=True,
                            base_color='lightcyan', boards=self.boards)
        board_in_progress = Board(self.root, x=250, y=10, title="В работе", is_fixed=True,
                                  base_color='chocolate', boards=self.boards)
        board_done = Board(self.root, x=500, y=10, title="Выполнено", is_fixed=True,
                           base_color='lightgreen', boards=self.boards)

        # Добавляем доски в список
        self.boards.extend([board_queue, board_in_progress, board_done])

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