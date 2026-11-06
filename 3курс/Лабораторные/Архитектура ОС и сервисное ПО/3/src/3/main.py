import html
import os
import random
import string
import sys
import threading
import time

from PyQt6.QtCore import QObject, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSlider,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# Начальные задержки потоков (мс). Ползунки на панелях управления
# инициализируются именно этими значениями.
WRITER_DELAY = 1000
READER_DELAY = 1200
PRODUCER_DELAY = 900
CONSUMER_DELAY = 1300


# ==============================================================================
# Базовый класс TThread (согласно требованию задания)
# ==============================================================================
class TThread(threading.Thread):
    """
    Аналог класса TThread (из VCL/Delphi) с поддержкой:
    - запуска, паузы, остановки;
    - регулировки скорости работы через временные задержки;
    - отслеживания текущего состояния потока для визуализации.

    Поток Python нельзя запустить повторно, поэтому «Запуск» после «Останов»
    реализуется на уровне интерфейса: создаётся новый объект потока
    (см. ThreadControlPanel.on_start).
    """

    TICK = 0.05  # шаг опроса событий паузы/останова, с

    def __init__(self, name: str, delay_ms: int = 1000):
        super().__init__(name=name, daemon=True)
        self.delay_ms = delay_ms
        self._pause_event = threading.Event()
        self._pause_event.set()  # По умолчанию не на паузе
        self._stop_event = threading.Event()
        self.state_str = "Не запущен"
        self.error = None
        self._started_once = False

    # ------------------------------------------------------------------ состояние
    @property
    def stopped(self) -> bool:
        """True, если поток остановлен (кнопкой или из-за ошибки)."""
        return self._stop_event.is_set()

    @property
    def display_state(self) -> str:
        """Состояние для отображения: «Пауза»/«Остановлен» не затираются шагом."""
        if self.error:
            return f"Ошибка: {self.error}"
        if self._stop_event.is_set():
            return "Остановлен"
        if not self._started_once:
            return "Не запущен"
        if not self._pause_event.is_set():
            return "Пауза"
        return self.state_str

    # ------------------------------------------------------------------ управление
    def start_thread(self):
        if self.stopped:
            return  # остановленный поток возобновить нельзя — нужен новый объект
        if not self._started_once:
            self._started_once = True
            self.state_str = "Работает"
            self.start()
        else:
            self.resume_thread()

    def pause_thread(self):
        if self._started_once and not self._stop_event.is_set():
            self._pause_event.clear()

    def resume_thread(self):
        if self._started_once and not self._stop_event.is_set():
            self._pause_event.set()

    def stop_thread(self):
        self._stop_event.set()
        self._pause_event.set()  # Разблокируем, если висел на паузе

    def set_speed(self, delay_ms: int):
        self.delay_ms = delay_ms

    # ------------------------------------------------------------------ ожидание
    def sleep_step(self) -> bool:
        """
        Ожидание между шагами с учётом скорости работы. delay_ms читается на
        каждой итерации, поэтому ползунок действует сразу. Время паузы в
        задержку не засчитывается. Возвращает False, если поток остановлен.
        """
        elapsed = 0.0
        while elapsed * 1000 < self.delay_ms:
            if self._stop_event.is_set():
                return False
            self._pause_event.wait()
            if self._stop_event.is_set():
                return False
            time.sleep(self.TICK)
            elapsed += self.TICK
        return not self._stop_event.is_set()

    def wait_poll(self, interval: float = 0.05) -> bool:
        """Короткий опрос флага блокировки (не зависит от delay_ms потока)."""
        self._pause_event.wait()
        if self._stop_event.is_set():
            return False
        time.sleep(interval)
        return not self._stop_event.is_set()

    def run(self):
        try:
            while not self._stop_event.is_set():
                self._pause_event.wait()
                if self._stop_event.is_set():
                    break
                self.execute_step()
                if not self.sleep_step():
                    break
        except Exception as exc:  # поток не должен умирать молча
            self.error = f"{type(exc).__name__}: {exc}"
            self._stop_event.set()
        finally:
            self.state_str = "Остановлен"

    def execute_step(self):
        """Переопределяется в дочерних классах."""
        pass


# ==============================================================================
# Сигналы для потокобезопасного обновления GUI
# ==============================================================================
class LogSignaler(QObject):
    log_signal = pyqtSignal(str, str)  # (текущее событие, запись в лог)


# ==============================================================================
# ЗАДАНИЕ 1: Мьютексы и общий файл
# ==============================================================================
class FileShared:
    """
    Общие данные Задания 1: файл, защищающий его мьютекс и счётчики.
    Счётчики и read_pos изменяются только внутри критической секции (под mutex).
    """

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.mutex = threading.Lock()
        self.read_pos = 0
        self.written = 0  # сколько символов записано всего
        self.reads = 0  # сколько символов считано всего
        self.deleted = 0  # сколько цифр удалено
        with open(self.filepath, "w", encoding="utf-8"):
            pass  # создаём/очищаем файл


class FileWriterThread(TThread):
    """Первый поток: записывает в файл случайные символы."""

    def __init__(self, shared: FileShared, signaler: LogSignaler, delay_ms: int):
        super().__init__(name="P[0] (Писатель)", delay_ms=delay_ms)
        self.shared = shared
        self.signaler = signaler
        self.chars = (
            string.ascii_uppercase + string.digits + string.digits
        )  # Больше шанс цифр

    def execute_step(self):
        sh = self.shared
        self.state_str = "Ожидание мьютекса"
        with sh.mutex:
            self.state_str = "Критическая секция (Запись)"
            ch = random.choice(self.chars)
            with open(sh.filepath, "a", encoding="utf-8") as f:
                f.write(ch)
            sh.written += 1
            msg = f"P[0]: записан символ '{ch}' в файл"
            self.signaler.log_signal.emit(msg, msg)
            time.sleep(0.15)  # Небольшая задержка внутри КС для наглядности в UI
        self.state_str = "Работает (вне КС)"


class FileReaderThread(TThread):
    """
    Второй поток: считывает из файла символ и удаляет его, если это цифра.

    Трактовка: курсор чтения идёт по файлу слева направо; дойдя до конца,
    возвращается в начало (буквы никогда не удаляются, поэтому в файле
    остаются просмотренные символы, и цикл обхода продолжается).
    """

    def __init__(self, shared: FileShared, signaler: LogSignaler, delay_ms: int):
        super().__init__(name="P[1] (Читатель)", delay_ms=delay_ms)
        self.shared = shared
        self.signaler = signaler

    def execute_step(self):
        sh = self.shared
        self.state_str = "Ожидание мьютекса"
        with sh.mutex:
            self.state_str = "Критическая секция (Чтение)"
            if not os.path.exists(sh.filepath):
                content = ""
            else:
                with open(sh.filepath, "r", encoding="utf-8") as f:
                    content = f.read()

            if len(content) == 0:
                msg = "P[1]: файл пуст, нечего считывать"
                self.signaler.log_signal.emit(msg, msg)
            else:
                if sh.read_pos >= len(content):
                    sh.read_pos = 0

                pos = sh.read_pos
                ch = content[pos]
                sh.reads += 1
                if ch.isdigit():
                    # Удаляем цифру из файла
                    new_content = content[:pos] + content[pos + 1 :]
                    with open(sh.filepath, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    sh.deleted += 1
                    msg = f"P[1]: считан '{ch}' (индекс {pos}) -> ЦИФРА (Удалено)"
                    if sh.read_pos >= len(new_content):
                        sh.read_pos = 0
                else:
                    msg = f"P[1]: считан '{ch}' (индекс {pos}) -> БУКВА (Оставлено)"
                    sh.read_pos = (pos + 1) % len(content)

                self.signaler.log_signal.emit(msg, msg)
            time.sleep(0.15)
        self.state_str = "Работает (вне КС)"


# ==============================================================================
# ЗАДАНИЕ 2: Кольцевой буфер и блокирующие переменные
# ==============================================================================
class RingBufferLockVars:
    """
    Кольцевой буфер, синхронизируемый с помощью блокирующих переменных (флагов).
    - lock_var: блокирующая переменная входа в критическую секцию (0 - свободно, 1 - занято)
    - full_lock: блокирующая переменная переполнения (1 - буфер полон, запись заблокирована)
    - empty_lock: блокирующая переменная опустошения (1 - буфер пуст, чтение заблокировано)

    Для проверки корректности передачи данных производитель пишет в буфер
    возрастающую последовательность 1, 2, 3, ..., а потребитель проверяет,
    что извлекает числа строго по порядку и без потерь.
    """

    def __init__(self, size: int = 8):
        self.size = size
        self.buffer = [None] * size
        self.head = 0  # Индекс для записи (Производитель)
        self.tail = 0  # Индекс для чтения (Потребитель)
        self.count = 0

        # Блокирующие переменные (визуализируются в таблице параметров)
        self.lock_var = 0
        self.full_lock = 0
        self.empty_lock = 1

        # Статистика (изменяется только внутри критической секции)
        self.produced = 0
        self.consumed = 0
        self.last_consumed = 0
        self.errors = 0

        # Внутренний атомарный примитив для проверки и установки lock_var без гонок Python
        # (эмуляция команды TSL)
        self._atomic = threading.Lock()

    def acquire_lock_var(
        self, stop_event: threading.Event, pause_event: threading.Event
    ) -> bool:
        """Захват блокирующей переменной критической секции (активное ожидание)."""
        while not stop_event.is_set():
            pause_event.wait()
            with self._atomic:
                if self.lock_var == 0:
                    self.lock_var = 1
                    return True
            time.sleep(0.05)
        return False

    def release_lock_var(self):
        with self._atomic:
            self.lock_var = 0

    def update_flags(self):
        self.full_lock = 1 if self.count == self.size else 0
        self.empty_lock = 1 if self.count == 0 else 0


class ProducerThread(TThread):
    """Производитель: помещает элементы в кольцевой буфер."""

    def __init__(self, rb: RingBufferLockVars, signaler: LogSignaler, delay_ms: int):
        super().__init__(name="P[0] (Производитель)", delay_ms=delay_ms)
        self.rb = rb
        self.signaler = signaler

    def execute_step(self):
        rb = self.rb
        # 1. Проверяем блокирующую переменную переполнения буфера
        #    (короткий опрос, не зависящий от скорости потока)
        while rb.full_lock == 1:
            self.state_str = "Блокирован (full_lock = 1)"
            if not self.wait_poll():
                return

        # 2. Захватываем блокирующую переменную доступа к буферу (lock_var)
        self.state_str = "Ожидание lock_var (занят)"
        if not rb.acquire_lock_var(self._stop_event, self._pause_event):
            return

        try:
            if rb.count < rb.size:
                self.state_str = "Критическая секция (Запись)"
                rb.produced += 1
                item = rb.produced
                idx = rb.head
                rb.buffer[idx] = item
                rb.head = (rb.head + 1) % rb.size
                rb.count += 1
                rb.update_flags()

                msg = f"P[0]: записал '{item}' в ячейку [{idx}]"
                self.signaler.log_signal.emit(msg, msg)
                time.sleep(0.15)
        finally:
            rb.release_lock_var()
            self.state_str = "Работает (вне КС)"


class ConsumerThread(TThread):
    """Потребитель: извлекает элементы из кольцевого буфера."""

    def __init__(self, rb: RingBufferLockVars, signaler: LogSignaler, delay_ms: int):
        super().__init__(name="P[1] (Потребитель)", delay_ms=delay_ms)
        self.rb = rb
        self.signaler = signaler

    def execute_step(self):
        rb = self.rb
        # 1. Проверяем блокирующую переменную пустоты буфера
        while rb.empty_lock == 1:
            self.state_str = "Блокирован (empty_lock = 1)"
            if not self.wait_poll():
                return

        # 2. Захватываем блокирующую переменную доступа к буферу (lock_var)
        self.state_str = "Ожидание lock_var (занят)"
        if not rb.acquire_lock_var(self._stop_event, self._pause_event):
            return

        try:
            if rb.count > 0:
                self.state_str = "Критическая секция (Чтение)"
                idx = rb.tail
                item = rb.buffer[idx]
                rb.buffer[idx] = None
                rb.tail = (rb.tail + 1) % rb.size
                rb.count -= 1
                rb.update_flags()

                expected = rb.last_consumed + 1
                if item != expected:
                    rb.errors += 1
                    msg = (
                        f"P[1]: ОШИБКА порядка! из ячейки [{idx}] извлечено "
                        f"'{item}', ожидалось '{expected}'"
                    )
                else:
                    msg = f"P[1]: извлек '{item}' из ячейки [{idx}]"
                if item is not None:
                    rb.last_consumed = item
                rb.consumed += 1
                self.signaler.log_signal.emit(msg, msg)
                time.sleep(0.15)
        finally:
            rb.release_lock_var()
            self.state_str = "Работает (вне КС)"


# ==============================================================================
# Визуальный компонент управления одним потоком
# ==============================================================================
class ThreadControlPanel(QGroupBox):
    """
    thread_getter() -> текущий объект потока;
    thread_factory(delay_ms) -> создаёт новый поток, запоминает его в виджете
    задания и возвращает (нужно для «Запуск» после «Останов»).
    """

    def __init__(self, title: str, thread_getter, thread_factory):
        super().__init__(title)
        self.thread_getter = thread_getter
        self.thread_factory = thread_factory
        layout = QVBoxLayout()

        # Кнопки «Запуск», «Пауза», «Останов»
        btn_layout = QHBoxLayout()
        self.btn_start = QPushButton("Запуск")
        self.btn_pause = QPushButton("Пауза")
        self.btn_stop = QPushButton("Останов")

        self.btn_start.clicked.connect(self.on_start)
        self.btn_pause.clicked.connect(self.on_pause)
        self.btn_stop.clicked.connect(self.on_stop)

        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_pause)
        btn_layout.addWidget(self.btn_stop)
        layout.addLayout(btn_layout)

        # Регулировка скорости работы (ползунок задержки),
        # начальное значение берётся из самого потока
        initial = self.thread_getter().delay_ms
        speed_layout = QHBoxLayout()
        self.lbl_speed = QLabel(f"Задержка (мс): {initial}")
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(100, 3000)
        self.slider.setSingleStep(100)
        self.slider.setValue(initial)  # до connect(), чтобы не вызвать обработчик
        self.slider.valueChanged.connect(self.on_speed_changed)

        speed_layout.addWidget(self.lbl_speed)
        speed_layout.addWidget(self.slider)
        layout.addLayout(speed_layout)

        self.setLayout(layout)

    def on_start(self):
        t = self.thread_getter()
        if t is None or t.stopped:
            # Остановленный поток запустить повторно нельзя — создаём новый
            if t is not None and t.is_alive():
                t.join(timeout=1)  # дожидаемся выхода из критической секции
            t = self.thread_factory(self.slider.value())
        t.start_thread()

    def on_pause(self):
        t = self.thread_getter()
        if t:
            t.pause_thread()

    def on_stop(self):
        t = self.thread_getter()
        if t:
            t.stop_thread()

    def on_speed_changed(self, val: int):
        self.lbl_speed.setText(f"Задержка (мс): {val}")
        t = self.thread_getter()
        if t:
            t.set_speed(val)


def stop_and_join(threads):
    """Останавливает потоки и дожидается их завершения (без sleep-«на удачу»)."""
    for t in threads:
        t.stop_thread()
    for t in threads:
        if t.is_alive():
            t.join(timeout=1)


# ==============================================================================
# ВКЛАДКА 1: Виджет Задания 1 (Мьютексы и файл)
# ==============================================================================
class Task1Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.shared = FileShared("shared_buffer_var46.txt")
        self.signaler = LogSignaler()
        self.signaler.log_signal.connect(self.on_log)
        self._last_view = None

        self.writer_thread = None
        self.reader_thread = None
        self.create_writer(WRITER_DELAY)
        self.create_reader(READER_DELAY)
        self.init_ui()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_ui_state)
        self.timer.start(100)

    def create_writer(self, delay_ms: int):
        self.writer_thread = FileWriterThread(self.shared, self.signaler, delay_ms)
        return self.writer_thread

    def create_reader(self, delay_ms: int):
        self.reader_thread = FileReaderThread(self.shared, self.signaler, delay_ms)
        return self.reader_thread

    def init_ui(self):
        main_layout = QHBoxLayout(self)

        # Левая колонка: Таблицы параметров/состояний + Буфер + Управление
        left_layout = QVBoxLayout()

        title = QLabel("Задание 1: Мьютексы и общий файл")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        left_layout.addWidget(title)

        # Таблицы состояния потоков и мьютекса
        tables_layout = QHBoxLayout()

        self.proc_table = QTableWidget(2, 2)
        self.proc_table.setHorizontalHeaderLabels(["Поток", "Состояние"])
        self.proc_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.proc_table.verticalHeader().setVisible(False)
        self.proc_table.setFixedHeight(95)
        self.proc_table.setItem(0, 0, QTableWidgetItem("P[0] (Запись)"))
        self.proc_table.setItem(0, 1, QTableWidgetItem("Не запущен"))
        self.proc_table.setItem(1, 0, QTableWidgetItem("P[1] (Чтение/Удал.)"))
        self.proc_table.setItem(1, 1, QTableWidgetItem("Не запущен"))

        self.param_table = QTableWidget(2, 2)
        self.param_table.setHorizontalHeaderLabels(["Параметр", "Значение"])
        self.param_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.param_table.verticalHeader().setVisible(False)
        self.param_table.setFixedHeight(95)
        self.param_table.setItem(0, 0, QTableWidgetItem("mutex"))
        self.param_table.setItem(0, 1, QTableWidgetItem("0 (Свободен)"))
        self.param_table.setItem(1, 0, QTableWidgetItem("Позиция чтения P[1]"))
        self.param_table.setItem(1, 1, QTableWidgetItem("0"))

        tables_layout.addWidget(self.proc_table, 3)
        tables_layout.addWidget(self.param_table, 2)
        left_layout.addLayout(tables_layout)

        # Наглядное отображение содержимого буфера (файла)
        buf_group = QGroupBox(
            "Наглядное отображение текущего содержимого буфера (файла shared_buffer_var46.txt)"
        )
        buf_layout = QVBoxLayout()
        self.buf_text = QTextEdit()
        self.buf_text.setReadOnly(True)
        self.buf_text.setFont(QFont("Consolas", 13, QFont.Weight.Bold))
        self.buf_text.setPlaceholderText("Файл пуст...")
        self.buf_text.setMinimumHeight(80)
        buf_layout.addWidget(self.buf_text)

        self.lbl_file_info = QLabel("Длина файла: 0 символов")
        buf_layout.addWidget(self.lbl_file_info)
        self.lbl_stats = QLabel("Записано: 0 | Считано: 0 | Удалено цифр: 0")
        buf_layout.addWidget(self.lbl_stats)
        buf_group.setLayout(buf_layout)
        left_layout.addWidget(buf_group)

        # Панели управления потоками
        self.ctrl_p0 = ThreadControlPanel(
            "Поток 1 — P[0]: Запись случайных символов в файл",
            lambda: self.writer_thread,
            self.create_writer,
        )
        self.ctrl_p1 = ThreadControlPanel(
            "Поток 2 — P[1]: Чтение символа и удаление, если это цифра",
            lambda: self.reader_thread,
            self.create_reader,
        )
        left_layout.addWidget(self.ctrl_p0)
        left_layout.addWidget(self.ctrl_p1)

        btn_reset = QPushButton(
            "Сбросить: очистить файл и создать потоки заново (ждут «Запуск»)"
        )
        btn_reset.clicked.connect(self.reset_all)
        left_layout.addWidget(btn_reset)

        # Правая колонка: Текущее событие и Последние события
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Текущее событие"))
        self.curr_event = QLineEdit("Инициализация потоков")
        self.curr_event.setReadOnly(True)
        right_layout.addWidget(self.curr_event)

        right_layout.addWidget(QLabel("Последние события"))
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.document().setMaximumBlockCount(1000)
        right_layout.addWidget(self.log_box)

        main_layout.addLayout(left_layout, 3)
        main_layout.addLayout(right_layout, 2)

    def on_log(self, current: str, log_line: str):
        self.curr_event.setText(current)
        self.log_box.append(log_line)

    def update_ui_state(self):
        sh = self.shared
        # Обновление таблицы состояний
        self.proc_table.item(0, 1).setText(self.writer_thread.display_state)
        self.proc_table.item(1, 1).setText(self.reader_thread.display_state)

        self.param_table.item(0, 1).setText(
            "1 (Занят)" if sh.mutex.locked() else "0 (Свободен)"
        )
        self.param_table.item(1, 1).setText(str(sh.read_pos))

        # Файл читаем по тому же протоколу (под мьютексом), но не блокируя GUI:
        # если КС занята, оставляем прежнюю картинку.
        content = None
        if sh.mutex.acquire(blocking=False):
            try:
                if os.path.exists(sh.filepath):
                    with open(sh.filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                else:
                    content = ""
                pos = sh.read_pos
                written, reads, deleted = sh.written, sh.reads, sh.deleted
            except OSError:
                content = None
            finally:
                sh.mutex.release()
        if content is None:
            return

        # Целостность: символов в файле = записано - удалено
        ok = len(content) == written - deleted
        self.lbl_file_info.setText(
            f"Длина файла: {len(content)} симв. | Контроль (записано − удалено = "
            f"длина): {'OK' if ok else 'НАРУШЕНО'} | Подсвечена позиция P[1]; "
            f"цифры (красные) удаляются вторым потоком"
        )
        self.lbl_stats.setText(
            f"Записано: {written} | Считано: {reads} | Удалено цифр: {deleted}"
        )

        view_key = (content, pos)
        if view_key != self._last_view:
            self._last_view = view_key
            parts = []
            for i, ch in enumerate(content):
                s = html.escape(ch)
                if i == pos:
                    s = f'<span style="background-color:#ffc107; color:#000;">{s}</span>'
                elif ch.isdigit():
                    s = f'<span style="color:#c0392b;">{s}</span>'
                parts.append(s)
            self.buf_text.setHtml("".join(parts))

    def reset_all(self):
        stop_and_join((self.writer_thread, self.reader_thread))
        # Старые потоки завершены — можно безопасно очистить файл и счётчики
        self.shared = FileShared(self.shared.filepath)
        self.create_writer(self.ctrl_p0.slider.value())
        self.create_reader(self.ctrl_p1.slider.value())
        self._last_view = None
        self.log_box.clear()
        self.curr_event.setText("Инициализация потоков")


# ==============================================================================
# ВКЛАДКА 2: Виджет Задания 2 (Кольцевой буфер + блокирующие переменные)
# ==============================================================================
class Task2Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.rb = RingBufferLockVars(size=8)
        self.signaler = LogSignaler()
        self.signaler.log_signal.connect(self.on_log)

        self.producer_thread = None
        self.consumer_thread = None
        self.create_producer(PRODUCER_DELAY)
        self.create_consumer(CONSUMER_DELAY)
        self.init_ui()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_ui_state)
        self.timer.start(100)

    def create_producer(self, delay_ms: int):
        self.producer_thread = ProducerThread(self.rb, self.signaler, delay_ms)
        return self.producer_thread

    def create_consumer(self, delay_ms: int):
        self.consumer_thread = ConsumerThread(self.rb, self.signaler, delay_ms)
        return self.consumer_thread

    def init_ui(self):
        main_layout = QHBoxLayout(self)

        # Левая колонка
        left_layout = QVBoxLayout()

        title = QLabel("Задание 2: Производитель и потребитель (Кольцевой буфер)")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        left_layout.addWidget(title)

        tables_layout = QHBoxLayout()

        # Таблица состояний потоков
        self.proc_table = QTableWidget(2, 2)
        self.proc_table.setHorizontalHeaderLabels(["Процесс", "Состояние"])
        self.proc_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.proc_table.verticalHeader().setVisible(False)
        self.proc_table.setFixedHeight(105)
        self.proc_table.setItem(0, 0, QTableWidgetItem("P[0] (Производитель)"))
        self.proc_table.setItem(0, 1, QTableWidgetItem("Не запущен"))
        self.proc_table.setItem(1, 0, QTableWidgetItem("P[1] (Потребитель)"))
        self.proc_table.setItem(1, 1, QTableWidgetItem("Не запущен"))

        # Таблица блокирующих переменных
        self.param_table = QTableWidget(3, 2)
        self.param_table.setHorizontalHeaderLabels(["Блок. переменная", "Значение"])
        self.param_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.param_table.verticalHeader().setVisible(False)
        self.param_table.setFixedHeight(105)
        self.param_table.setItem(0, 0, QTableWidgetItem("lock_var (доступ к КС)"))
        self.param_table.setItem(0, 1, QTableWidgetItem("0"))
        self.param_table.setItem(1, 0, QTableWidgetItem("full_lock (буфер полон)"))
        self.param_table.setItem(1, 1, QTableWidgetItem("0"))
        self.param_table.setItem(2, 0, QTableWidgetItem("empty_lock (буфер пуст)"))
        self.param_table.setItem(2, 1, QTableWidgetItem("1"))

        tables_layout.addWidget(self.proc_table, 3)
        tables_layout.addWidget(self.param_table, 2)
        left_layout.addLayout(tables_layout)

        # Наглядное отображение кольцевого буфера
        buf_group = QGroupBox("Наглядное отображение кольцевого буфера (8 ячеек)")
        buf_layout = QVBoxLayout()
        cells_layout = QHBoxLayout()
        self.cell_labels = []
        for i in range(self.rb.size):
            cell = QLabel(f"[{i}]\nПусто")
            cell.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cell.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
            cell.setFrameShape(QLabel.Shape.Box)
            cell.setFixedHeight(60)
            self.cell_labels.append(cell)
            cells_layout.addWidget(cell)

        buf_layout.addLayout(cells_layout)
        self.lbl_pointers = QLabel(
            "Указатель записи (Head): 0 | Указатель чтения (Tail): 0 | Заполнено: 0/8"
        )
        buf_layout.addWidget(self.lbl_pointers)
        self.lbl_stats = QLabel(
            "Произведено: 0 | Потреблено: 0 | Ошибок порядка/потерь: 0"
        )
        buf_layout.addWidget(self.lbl_stats)
        buf_group.setLayout(buf_layout)
        left_layout.addWidget(buf_group)

        # Панели управления потоками
        self.ctrl_p0 = ThreadControlPanel(
            "Поток 1 — P[0]: Производитель (запись в кольцевой буфер)",
            lambda: self.producer_thread,
            self.create_producer,
        )
        self.ctrl_p1 = ThreadControlPanel(
            "Поток 2 — P[1]: Потребитель (чтение из кольцевого буфера)",
            lambda: self.consumer_thread,
            self.create_consumer,
        )
        left_layout.addWidget(self.ctrl_p0)
        left_layout.addWidget(self.ctrl_p1)

        btn_reset = QPushButton(
            "Сбросить: очистить буфер и создать потоки заново (ждут «Запуск»)"
        )
        btn_reset.clicked.connect(self.reset_all)
        left_layout.addWidget(btn_reset)

        # Правая колонка: События
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Текущее событие"))
        self.curr_event = QLineEdit("Инициализация процессов")
        self.curr_event.setReadOnly(True)
        right_layout.addWidget(self.curr_event)

        right_layout.addWidget(QLabel("Последние события"))
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.document().setMaximumBlockCount(1000)
        right_layout.addWidget(self.log_box)

        main_layout.addLayout(left_layout, 3)
        main_layout.addLayout(right_layout, 2)

    def on_log(self, current: str, log_line: str):
        self.curr_event.setText(current)
        self.log_box.append(log_line)

    def update_ui_state(self):
        rb = self.rb
        self.proc_table.item(0, 1).setText(self.producer_thread.display_state)
        self.proc_table.item(1, 1).setText(self.consumer_thread.display_state)

        self.param_table.item(0, 1).setText(str(rb.lock_var))
        self.param_table.item(1, 1).setText(str(rb.full_lock))
        self.param_table.item(2, 1).setText(str(rb.empty_lock))

        # Снимок для отображения (в отдельные мгновения возможна небольшая
        # рассогласованность значений — на работу потоков это не влияет)
        buffer = list(rb.buffer)
        head, tail, count = rb.head, rb.tail, rb.count

        # Обновление ячеек кольцевого буфера
        for i in range(rb.size):
            val = buffer[i]
            markers = []
            if i == head:
                markers.append("H")
            if i == tail:
                markers.append("T")
            marker_str = f" ({','.join(markers)})" if markers else ""

            if val is not None:
                self.cell_labels[i].setText(f"[{i}]{marker_str}\n{val}")
                self.cell_labels[i].setStyleSheet(
                    "background-color: #d4edda; color: #155724; border: 2px solid #28a745;"
                )
            else:
                self.cell_labels[i].setText(f"[{i}]{marker_str}\n—")
                if markers:
                    self.cell_labels[i].setStyleSheet(
                        "background-color: #fff3cd; color: #856404; border: 2px solid #ffc107;"
                    )
                else:
                    self.cell_labels[i].setStyleSheet(
                        "background-color: #f8f9fa; color: #6c757d; border: 1px solid #ced4da;"
                    )

        self.lbl_pointers.setText(
            f"Указатель записи (H - Head): {head} | "
            f"Указатель чтения (T - Tail): {tail} | "
            f"Заполнено: {count}/{rb.size}"
        )
        self.lbl_stats.setText(
            f"Произведено: {rb.produced} | Потреблено: {rb.consumed} | "
            f"Ошибок порядка/потерь: {rb.errors}"
        )

    def reset_all(self):
        stop_and_join((self.producer_thread, self.consumer_thread))
        self.rb = RingBufferLockVars(size=8)
        self.create_producer(self.ctrl_p0.slider.value())
        self.create_consumer(self.ctrl_p1.slider.value())
        self.log_box.clear()
        self.curr_event.setText("Инициализация процессов")


# ==============================================================================
# Главное окно приложения
# ==============================================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Синхронизация процессов — Вариант 46 (Архитектура ОС)")
        self.resize(1000, 700)

        tabs = QTabWidget()
        self.tab1 = Task1Widget()
        self.tab2 = Task2Widget()

        tabs.addTab(self.tab1, "Задание 1: Мьютексы и файл")
        tabs.addTab(self.tab2, "Задание 2: Кольцевой буфер (Блокирующие переменные)")

        self.setCentralWidget(tabs)

    def closeEvent(self, event):
        stop_and_join(
            (
                self.tab1.writer_thread,
                self.tab1.reader_thread,
                self.tab2.producer_thread,
                self.tab2.consumer_thread,
            )
        )
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
