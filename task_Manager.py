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
        self.scrollbar_y = tk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollbar_x = tk.Scrollbar(self.root, orient="horizontal", command=self.canvas.xview)

        # Настройка Canvas
        self.canvas.configure(
            yscrollcommand=self.scrollbar_y.set,
            xscrollcommand=self.scrollbar_x.set
        )
        self.scrollbar_y.config(command=self.canvas.yview)
        self.scrollbar_x.config(command=self.canvas.xview)

        # Внутренний фрейм для досок и кнопки
        self.inner_frame = tk.Frame(self.canvas, bg="white")
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        # Размещаем элементы
        self.scrollbar_y.pack(side="right", fill="y")
        self.scrollbar_x.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Список всех досок
        self.boards = []
        self.board_width = 220
        self.board_spacing = 20

        # Создаем фиксированные доски
        self.create_fixed_boards()

        # Кнопка "Добавить доску"
        self.add_board_button = tk.Button(
            self.inner_frame,
            text="➕ Добавить доску",
            command=self.add_new_board,
            bg="lightblue",
            fg="black",
            font=("Arial", 10),
            width=15
        )
        self.add_board_button.pack(anchor="ne", padx=10, pady=10)

        # Запускаем автоматическое обновление прокрутки
        self.start_auto_update_scroll()

        # Запускаем главный цикл
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    def create_fixed_boards(self):
        board_queue = Board(self.inner_frame, x=10, y=10, title="В очереди", is_fixed=True, base_color='lightcyan', boards=self.boards)
        board_in_progress = Board(self.inner_frame, x=250, y=10, title="В работе", is_fixed=True, base_color='chocolate', boards=self.boards)
        board_done = Board(self.inner_frame, x=500, y=10, title="Выполнено", is_fixed=True, base_color='lightgreen', boards=self.boards)
        self.boards.extend([board_queue, board_in_progress, board_done])

    def add_new_board(self):
        if not self.boards:
            x_position = 10
        else:
            last_board = self.boards[-1]
            x_position = last_board.board_frame.winfo_x() + last_board.board_frame.winfo_width() + self.board_spacing

        new_board = Board(
            self.inner_frame,
            x=x_position,
            y=10,
            title=f"Доска {len(self.boards) + 1}",
            is_fixed=False,
            base_color='lightblue',
            boards=self.boards
        )
        self.boards.append(new_board)
        self.update_scroll_region()

    def update_scroll_region(self):
        self.inner_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def start_auto_update_scroll(self):
        """Запускает периодическое обновление области прокрутки."""
        self.update_scroll_region()  # Вызываем функцию обновления сразу
        self.after_id = self.root.after(100, self.auto_update_scroll)  # Планируем следующий вызов

    def auto_update_scroll(self):
        self.update_inner_frame_size()
        """Метод для периодического обновления области прокрутки."""
        self.update_scroll_region()  # Обновляем регион прокрутки
        print(f"Inner frame size: {self.inner_frame.winfo_width()}x{self.inner_frame.winfo_height()}")
        print(f"Board positions: {[b.board_frame.winfo_x() for b in self.boards]}")
        self.after_id = self.root.after(100, self.auto_update_scroll)  # Планируем следующий вызов

    def stop_auto_update_scroll(self):
        """Останавливает периодическое обновление области прокрутки."""
        if hasattr(self, 'after_id'):
            self.root.after_cancel(self.after_id)  # Отменяем запланированный вызов
            del self.after_id

    def update_inner_frame_size(self):
        """Обновляет размер inner_frame на основе позиций досок."""
        if self.boards:
            # Находим правую границу последней доски
            last_board = self.boards[-1]
            right_edge = last_board.board_frame.winfo_x() + last_board.board_width
            # Устанавливаем ширину inner_frame
            new_width = right_edge + 20  # Добавляем отступ
        else:
            # Если досок нет, устанавливаем минимальную ширину
            new_width = 900

        # Устанавливаем минимальную высоту
        min_height = 600  # Минимальная высота для inner_frame

        # Применяем новые размеры
        self.inner_frame.place(x=0, y=0, width=new_width, height=min_height)

        # Принудительно обновляем информацию о виджетах
        print(
            f"Inner frame size before update_idletasks: {self.inner_frame.winfo_width()}x{self.inner_frame.winfo_height()}")
        self.inner_frame.update_idletasks()
        print(
            f"Inner frame size after update_idletasks: {self.inner_frame.winfo_width()}x{self.inner_frame.winfo_height()}")

    def on_close(self):
        self.stop_auto_update_scroll()
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