import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser

from settings import SettingsManager
from    data import MusicAPIClient, GENRES


class MusicApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Музыкальный справочник (iTunes API)")
        self.geometry("950x580")
        self.minsize(800, 500)

        # Инициализация менеджера настроек и клиента API
        self.settings = SettingsManager()
        self.api = MusicAPIClient()
        self.current_tracks = []

        self._setup_ui()
        # Выполняем стартовый поиск по последнему запросу
        self.perform_search(self.settings.get("last_query"))

    def _setup_ui(self):
        # --- Верхняя панель: Поиск и настройки ---
        top_frame = ttk.LabelFrame(self, text="Поиск песен и настройки", padding=10)
        top_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(top_frame, text="Исполнитель или трек:").pack(side=tk.LEFT, padx=(0, 5))

        self.search_var = tk.StringVar(value=self.settings.get("last_query"))
        self.search_entry = ttk.Entry(top_frame, textvariable=self.search_var, width=35, font=("Segoe UI", 10))
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<Return>", lambda event: self.on_search_click())

        search_btn = ttk.Button(top_frame, text="🔍 Найти", command=self.on_search_click)
        search_btn.pack(side=tk.LEFT, padx=5)

        # Выбор лимита
        ttk.Label(top_frame, text="Лимит:").pack(side=tk.LEFT, padx=(15, 5))
        self.limit_var = tk.IntVar(value=self.settings.get("limit"))
        limit_combo = ttk.Combobox(
            top_frame, textvariable=self.limit_var, values=[5, 10, 20, 50], width=5, state="readonly"
        )
        limit_combo.pack(side=tk.LEFT)
        limit_combo.bind("<<ComboboxSelected>>", self.on_settings_change)

        # Выбор региона
        ttk.Label(top_frame, text="Регион:").pack(side=tk.LEFT, padx=(15, 5))
        self.country_var = tk.StringVar(value=self.settings.get("country"))
        country_combo = ttk.Combobox(
            top_frame, textvariable=self.country_var, values=["US", "RU", "GB", "DE"], width=5, state="readonly"
        )
        country_combo.pack(side=tk.LEFT)
        country_combo.bind("<<ComboboxSelected>>", self.on_settings_change)

        # --- Панель быстрых жанров ---
        genre_frame = ttk.Frame(self, padding=(10, 5))
        genre_frame.pack(fill=tk.X)
        ttk.Label(genre_frame, text="Подборки по жанрам:").pack(side=tk.LEFT, padx=(0, 10))

        for label, query_val in GENRES.items():
            btn = ttk.Button(
                genre_frame,
                text=label,
                command=lambda q=query_val: self.on_genre_click(q)
            )
            btn.pack(side=tk.LEFT, padx=3)

        # --- Таблица результатов (Treeview) ---
        table_frame = ttk.Frame(self, padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("num", "artist", "title", "album", "genre", "year", "duration")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        # Заголовки столбцов
        self.tree.heading("num", text="№")
        self.tree.heading("artist", text="Исполнитель")
        self.tree.heading("title", text="Название трека")
        self.tree.heading("album", text="Альбом")
        self.tree.heading("genre", text="Жанр")
        self.tree.heading("year", text="Год")
        self.tree.heading("duration", text="Длит.")

        # Ширина столбцов
        self.tree.column("num", width=30, anchor=tk.CENTER)
        self.tree.column("artist", width=180)
        self.tree.column("title", width=220)
        self.tree.column("album", width=200)
        self.tree.column("genre", width=110)
        self.tree.column("year", width=60, anchor=tk.CENTER)
        self.tree.column("duration", width=60, anchor=tk.CENTER)

        # Скроллбар для таблицы
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Двойной клик по строке открывает страницу трека в браузере
        self.tree.bind("<Double-1>", self.on_row_double_click)

        # --- Нижняя строка статуса ---
        self.status_var = tk.StringVar(value="Готов к работе. Двойной клик по песне откроет её в Apple Music.")
        status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, padding=(10, 3))
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def on_settings_change(self, event=None):
        self.settings.set("limit", self.limit_var.get())
        self.settings.set("country", self.country_var.get())
        self.status_var.set(f"Настройки сохранены: лимит {self.limit_var.get()}, регион {self.country_var.get()}.")

    def on_search_click(self):
        query = self.search_var.get()
        self.perform_search(query)

    def on_genre_click(self, genre_query: str):
        self.search_var.set(genre_query)
        self.perform_search(genre_query)

    def perform_search(self, query: str):
        self.status_var.set("Загрузка данных из iTunes API...")
        self.update_idletasks()

        try:
            tracks = self.api.search_songs(
                query=query,
                limit=self.limit_var.get(),
                country=self.country_var.get()
            )
            self.current_tracks = tracks
            self.settings.set("last_query", query)
            self._update_table(tracks)
            self.status_var.set(f"Найдено треков: {len(tracks)}. Двойной клик по строке откроет трек в браузере.")

        except ValueError as ve:
            messagebox.showwarning("Некорректный ввод", str(ve))
            self.status_var.set("Ошибка ввода.")
        except Exception as e:
            messagebox.showerror("Ошибка API", str(e))
            self.status_var.set("Ошибка при получении данных.")

    def _update_table(self, tracks: list[dict]):
        # Очищаем старые записи
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Заполняем новыми
        for track in tracks:
            self.tree.insert("", tk.END, values=(
                track["num"],
                track["title"],
                track["artist"],
                track["album"],
                track["genre"],
                track["year"],
                track["duration"]
            ))

    def on_row_double_click(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected)
        track = self.current_tracks[index]
        if track.get("url"):
            webbrowser.open(track["url"])


if __name__ == "__main__":
    app = MusicApp()
    app.mainloop()
