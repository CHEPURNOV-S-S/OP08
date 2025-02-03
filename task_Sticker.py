import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox
from datetime import datetime


class Sticker:
    def __init__(self, master, x, y, title="Задача", description="Описание задачи",
                 on_delete=None, board=None, boards=None):
        self.master = master
        self.title = title
        self.description = description
        self.on_delete = on_delete  # Коллбэк для уведомления о удалении
        self.creation_time = datetime.now()
        self.completion_time = None
        self.editing = False  # Флаг для отслеживания состояния редактирования
        self.original_bg = 'lightyellow'
        self.highlight_bg = 'yellow'
        self.completed_bg = 'lightgreen'
        self.width = 210
        self.height = 140

        # Относительные координаты стикера относительно доски
        self.relative_x = x
        self.relative_y = y

        # Текущая доска
        self.current_board = board

        # Текущая доска
        self.previous_board = None

        # Список всех досок
        self.boards = boards

        # Создаем фрейм стикера
        self.sticker_frame = tk.Frame(master, bg=self.original_bg, bd=2)
        self.sticker_frame.place(x=x, y=y, width=self.width, height=self.height)

        # Title Entry with max length validation
        self.title_text = tk.Text(self.sticker_frame,height=1, width=23, relief=tk.RIDGE,
                                  font=('Consolas', 12, 'bold'), bg=self.highlight_bg)
        self.title_text.tag_configure("center", justify='center')
        self.title_text.insert("1.0", self.title)
        self.title_text.tag_add("center", "1.0", tk.END)

        self.title_text.config(state='disabled')  # Initially read-only
        self.title_text.pack(anchor='w', fill='x', padx=5, pady=5)  # Expand to full width
        #Обрабатываем событие, чтобы запретить ввод более 23 символов в заголовок.
        self.title_text.bind("<KeyRelease>", lambda event: self.validate_text_length(event, max_length=23))

        # Description Text with scrollbar
        self.desc_text = scrolledtext.ScrolledText(self.sticker_frame, wrap='word', height=4, width=23,
                                                   bg=self.original_bg, relief='flat')
        self.desc_text.insert('1.0', self.description)
        self.desc_text.config(state='disabled')
        self.desc_text.pack(anchor='w', fill='x', padx=5, pady=0)  # More compact packing and expand to full width

        # Buttons Frame
        self.buttons_frame = tk.Frame(self.sticker_frame, bg=self.original_bg)
        self.buttons_frame.pack(side='bottom', fill='x', padx=5, pady=5)

        # Button Symbols (Unicode)
        check_symbol = "✅"
        edit_symbol = "✏️"
        info_symbol = "ℹ️"
        delete_symbol = "❌"

        # Buttons
        self.check_button = tk.Button(self.buttons_frame, text=check_symbol, command=self.mark_completed)
        self.edit_button = tk.Button(self.buttons_frame, text=edit_symbol, command=self.toggle_edit_task)
        self.info_button = tk.Button(self.buttons_frame, text=info_symbol, command=self.show_info)
        self.delete_button = tk.Button(self.buttons_frame, text=delete_symbol, command=self.confirm_delete_task)

        # Use grid for centering buttons
        self.buttons_frame.grid_columnconfigure(0, weight=1)
        self.buttons_frame.grid_columnconfigure(1, weight=1)
        self.buttons_frame.grid_columnconfigure(2, weight=1)
        self.buttons_frame.grid_columnconfigure(3, weight=1)

        self.check_button.grid(row=0, column=0, padx=2)
        self.edit_button.grid(row=0, column=1, padx=2)
        self.info_button.grid(row=0, column=2, padx=2)
        self.delete_button.grid(row=0, column=3, padx=2)

        # Добавляем функционал перетаскивания
        self.sticker_frame.bind("<ButtonPress-1>", self.start_move)
        self.sticker_frame.bind("<ButtonRelease-1>", self.stop_move)
        self.sticker_frame.bind("<B1-Motion>", self.on_motion)

        self.title_text.bind("<ButtonPress-1>", self.start_move)
        self.title_text.bind("<ButtonRelease-1>", self.stop_move)
        self.title_text.bind("<B1-Motion>", self.on_motion)

        self.desc_text.bind("<ButtonPress-1>", self.start_move)
        self.desc_text.bind("<ButtonRelease-1>", self.stop_move)
        self.desc_text.bind("<B1-Motion>", self.on_motion)

        self.buttons_frame.bind("<ButtonPress-1>", self.start_move)
        self.buttons_frame.bind("<ButtonRelease-1>", self.stop_move)
        self.buttons_frame.bind("<B1-Motion>", self.on_motion)


    def start_move(self, event):
        self.x = event.x
        self.y = event.y

        # Если стикер находится на доске, открепляем его
        if self.current_board:
            self.previous_board = self.current_board

            self.current_board.remove_sticker(self)  # Удаляем стикер из списка текущей доски
            self.sticker_frame.place(in_=self.master,
                                     x=self.sticker_frame.winfo_x(),
                                     y=self.sticker_frame.winfo_y())
            self.current_board = None
        self.sticker_frame.config(bg=self.highlight_bg)  # Подсветка при начале перемещения

    def stop_move(self, event):
        target_board = self.find_target_board(event)
        if target_board:
            # Перемещаем стикер на новую доску
            self.relative_x = event.x_root - target_board.board_frame.winfo_rootx()
            self.relative_y = event.y_root - target_board.board_frame.winfo_rooty()
            self.sticker_frame.place(in_=target_board.board_frame, x=self.relative_x, y=self.relative_y)
            self.current_board = target_board
            self.previous_board = None
            target_board.add_sticker(self)
            # Перераспределяем стикеры на новой доске
            target_board.rearrange_stickers()
        else:
            # Возвращаем стикер на исходную позицию
            if self.previous_board:
                self.sticker_frame.place(in_=self.previous_board.board_frame, x=self.relative_x, y=self.relative_y)
                self.current_board = self.previous_board
                self.previous_board = None
                self.current_board.add_sticker(self)
                self.current_board.rearrange_stickers()  # Перераспределяем стикеры на исходной доске

        self.sticker_frame.config(bg=self.original_bg)  # Возвращаем исходный цвет

    def find_target_board(self, event):
        # Находим доску под курсором по координате x
        sticker_center_x = self.sticker_frame.winfo_x() + self.sticker_frame.winfo_width() // 2

        for board in self.boards:  # Используем переданный список досок
            board_x = board.board_frame.winfo_x()
            board_width = board.board_frame.winfo_width()

            # Проверяем, находится ли центр стикера в пределах доски по x
            if board_x <= sticker_center_x <= board_x + board_width:
                return board

        return None

    def on_motion(self, event):
        if self.x is None or self.y is None:
            return
        delta_x = event.x - self.x
        delta_y = event.y - self.y
        x = self.sticker_frame.winfo_x() + delta_x
        y = self.sticker_frame.winfo_y() + delta_y

        # Ограничиваем перемещение за пределы слева и сверху
        if x < 0:
            x = 0
        if y < 0:
            y = 0

        self.sticker_frame.place(x=x, y=y)

    def mark_completed(self):
        if self.completion_time:
            # Если задача уже выполнена, спрашиваем пользователя, хочет ли он отменить выполнение
            response = self.custom_messagebox_askyesno("Отмена выполнения", "Пометить задачу не выполненной?")
            if response:
                self.completion_time = None
                self.title_text.config(bg=self.highlight_bg)  # Возвращаем исходный цвет
                x = self.sticker_frame.winfo_rootx()
                y = self.sticker_frame.winfo_rooty() + self.sticker_frame.winfo_height()
                self.show_custom_messagebox("Задача не выполнена", "Пометка о выполнении задачи отменена.")
        else:
            # Если задача не выполнена, помечаем её как выполненную
            self.completion_time = datetime.now()
            self.title_text.config(bg=self.completed_bg)  # Изменяем фон на lightgreen
            self.show_custom_messagebox("Задача выполнена", "Задача отмечена как выполненная!")

    def toggle_edit_task(self):
        if not self.editing:
            # Включаем режим редактирования
            self.editing = True
            self.edit_button.config(relief=tk.SUNKEN)  # Кнопка становится зажатой

            # Делаем поля редактируемыми
            self.title_text.config(state='normal')
            self.desc_text.config(state='normal')
            self.desc_text.focus_set()
            self.desc_text.see('1.0')  # Прокручиваем к началу текста
        else:
            # Выключаем режим редактирования и сохраняем изменения
            self.editing = False
            self.edit_button.config(relief=tk.RAISED)  # Кнопка становится обычной

            # Сохраняем новые значения
            new_title = self.title_text.get('1.0', 'end')
            new_desc = self.desc_text.get('1.0', 'end').strip()
            if new_title and len(new_title) > 6:
                self.title = new_title
            else:
                self.title_text.delete('1.0', tk.END)  # Удаляем весь текст
                self.title_text.insert("1.0", self.title)
                self.title_text.tag_add("center", "1.0", tk.END)
            self.title_text.config(state='disabled')
            self.title_text.yview_moveto(0)  # Прокручиваем к началу текста
            if new_desc:
                self.description = new_desc
            self.desc_text.config(state='disabled')
            self.desc_text.yview_moveto(0)  # Прокручиваем к началу текста

    def show_info(self):
        info = f"Время создания: {self.creation_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        if self.completion_time:
            info += f"Время завершения: {self.completion_time.strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            info += "Время завершения: Задача не завершена"
        self.show_custom_messagebox("Информация о задаче", info)

    def confirm_delete_task(self):
        response = self.custom_messagebox_askyesno("Подтверждение удаления",
                                       f"Вы действительно хотите удалить задачу '{self.title}'?")
        if response:
            self.delete_task()

    def delete_task(self):
        if self.on_delete:
            self.on_delete(self)  # Уведомляем об удалении
        self.sticker_frame.destroy()

    def validate_text_length(self, event, max_length=100):
        text_widget = event.widget
        current_text = text_widget.get("1.0", tk.END)
        if len(current_text) > max_length:
            text_widget.delete(f"1.{len(current_text)-1}", tk.END)
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

        # Устанавливаем размер окна как размер стикера
        sticker_width = self.sticker_frame.winfo_width()
        sticker_height = self.sticker_frame.winfo_height()
        msg_box.geometry(
            f"{sticker_width}x{sticker_height-35}+{self.sticker_frame.winfo_rootx()-7}+{self.sticker_frame.winfo_rooty() + self.sticker_frame.winfo_height()}")

        # Делаем окно модальным
        msg_box.transient(self.master)
        msg_box.grab_set()

        # Блокируем возможность изменения размеров окна
        msg_box.resizable(False, False)

        # Создаем метку для сообщения с поддержкой многострочного текста
        label = tk.Label(msg_box, text=message, font=('Consolas', 10), justify='center', wraplength=sticker_width - 20)
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

        # Устанавливаем размер окна как размер стикера
        sticker_width = self.sticker_frame.winfo_width()
        sticker_height = self.sticker_frame.winfo_height()
        msg_box.geometry(
            f"{sticker_width}x{sticker_height-35}+{self.sticker_frame.winfo_rootx()-7}+{self.sticker_frame.winfo_rooty() + self.sticker_frame.winfo_height()}")

        # Делаем окно модальным
        msg_box.transient(self.master)
        msg_box.grab_set()

        # Блокируем возможность изменения размеров окна
        msg_box.resizable(False, False)

        # Создаем метку для сообщения с поддержкой многострочного текста
        label = tk.Label(msg_box, text=message, font=('Consolas', 10), justify='center', wraplength=sticker_width - 20)
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


def create_stickers(root, num_stickers=4):
    for i in range(num_stickers):
        x = 50 + (i * 100) % 300  # Adjust positions to avoid overlap
        y = 50 + (i // 3) * 150
        Sticker(root, x, y, f"Задача {i + 1}", f"Описание задачи {i + 1}")


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")
    root.title("Менеджер задач")
    create_stickers(root)
    root.mainloop()