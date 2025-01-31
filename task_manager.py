import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox
from datetime import datetime


class Sticker:
    def __init__(self, master, x, y, title="Задача", description="Описание задачи"):
        self.master = master
        self.title = title
        self.description = description
        self.creation_time = datetime.now()
        self.completion_time = None
        self.editing = False  # Флаг для отслеживания состояния редактирования

        # Создаем фрейм стикера с заданной шириной
        self.sticker_frame = tk.Frame(master, bg='lightyellow', bd=2)
        self.sticker_frame.config(width=200)  # Устанавливаем ширину стикера

        # Title Entry with max length validation
        vcmd = (self.sticker_frame.register(self.validate_title), '%P')
        self.title_entry = tk.Entry(self.sticker_frame, font=('Consolas', 12, 'bold'), bg='lightyellow', validate='key',
                                    validatecommand=vcmd)
        self.title_entry.insert(0, self.title)
        self.title_entry.config(state='readonly')  # Initially read-only
        self.title_entry.pack(anchor='w', fill='x', padx=5, pady=5)  # Expand to full width

        # Description Text with scrollbar
        self.desc_text = scrolledtext.ScrolledText(self.sticker_frame, wrap='word', height=4, width=23,
                                                   bg='lightyellow', relief='flat')
        self.desc_text.insert('1.0', self.description)
        self.desc_text.config(state='disabled')
        self.desc_text.pack(anchor='w', fill='x', padx=5, pady=0)  # More compact packing and expand to full width

        # Buttons Frame
        buttons_frame = tk.Frame(self.sticker_frame, bg='lightyellow')
        buttons_frame.pack(side='bottom', fill='x', padx=5, pady=5)

        # Button Symbols (Unicode)
        check_symbol = "✅"
        edit_symbol = "✏️"
        info_symbol = "ℹ️"
        delete_symbol = "❌"

        # Buttons
        self.check_button = tk.Button(buttons_frame, text=check_symbol, command=self.mark_completed)
        self.edit_button = tk.Button(buttons_frame, text=edit_symbol, command=self.toggle_edit_task)
        self.info_button = tk.Button(buttons_frame, text=info_symbol, command=self.show_info)
        self.delete_button = tk.Button(buttons_frame, text=delete_symbol, command=self.confirm_delete_task)

        # Use grid for centering buttons
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)
        buttons_frame.grid_columnconfigure(2, weight=1)
        buttons_frame.grid_columnconfigure(3, weight=1)

        self.check_button.grid(row=0, column=0, padx=2)
        self.edit_button.grid(row=0, column=1, padx=2)
        self.info_button.grid(row=0, column=2, padx=2)
        self.delete_button.grid(row=0, column=3, padx=2)

        # Drag and Drop functionality
        self.sticker_frame.bind("<ButtonPress-1>", self.start_move)
        self.sticker_frame.bind("<ButtonRelease-1>", self.stop_move)
        self.sticker_frame.bind("<B1-Motion>", self.on_motion)

        # Place the sticker
        self.sticker_frame.place(x=x, y=y)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def on_motion(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.sticker_frame.winfo_x() + deltax
        y = self.sticker_frame.winfo_y() + deltay
        self.sticker_frame.place(x=x, y=y)

    def mark_completed(self):
        if not self.completion_time:
            self.completion_time = datetime.now()
            self.title_entry.config(bg='lightgreen')
            messagebox.showinfo("Задача выполнена", "Задача отмечена как выполненная!")
        else:
            messagebox.showinfo("Задача уже выполнена", "Эта задача уже выполнена.")

    def toggle_edit_task(self):
        if not self.editing:
            # Включаем режим редактирования
            self.editing = True
            self.edit_button.config(relief=tk.SUNKEN)  # Кнопка становится зажатой

            # Делаем поля редактируемыми
            self.title_entry.config(state='normal')
            self.desc_text.config(state='normal')
            self.desc_text.focus_set()
            self.desc_text.see('1.0')  # Прокручиваем к началу текста
        else:
            # Выключаем режим редактирования и сохраняем изменения
            self.editing = False
            self.edit_button.config(relief=tk.RAISED)  # Кнопка становится обычной

            # Сохраняем новые значения
            new_title = self.title_entry.get()
            new_desc = self.desc_text.get('1.0', 'end').strip()
            if new_title:
                self.title = new_title
                self.title_entry.config(state='readonly')

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
        messagebox.showinfo("Информация о задаче", info)

    def confirm_delete_task(self):
        response = messagebox.askyesno("Подтверждение удаления",
                                       f"Вы действительно хотите удалить задачу '{self.title}'?")
        if response:
            self.delete_task()

    def delete_task(self):
        self.sticker_frame.destroy()

    def validate_title(self, new_value):
        # Проверяем длину нового значения
        return len(new_value) <= 20


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