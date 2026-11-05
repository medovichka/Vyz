import math
import os
import random
import string
import sys
import threading
import time

from PyQt6.QtCore import QObject, QPointF, QRectF, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QPainter,
    QPainterPath,
    QPalette,
    QPen,
    QPolygonF,
)
from PyQt6.QtWidgets import (
    QApplication,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSlider,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

WRITER_DELAY = 1000
READER_DELAY = 1200
PRODUCER_DELAY = 900
CONSUMER_DELAY = 1300


# ==============================================================================
# Базовый класс TThread
# ==============================================================================
class TThread(threading.Thread):
    TICK = 0.05

    def __init__(self, name: str, delay_ms: int = 1000):
        super().__init__(name=name, daemon=True)
        self.delay_ms = delay_ms
        self._pause_event = threading.Event()
        self._pause_event.set()
        self._stop_event = threading.Event()
        self.state_str = "—"
        self.error = None
        self._started_once = False

    @property
    def stopped(self) -> bool:
        return self._stop_event.is_set()

    @property
    def paused(self) -> bool:
        return (
            self._started_once
            and not self._stop_event.is_set()
            and not self._pause_event.is_set()
        )

    @property
    def running_active(self) -> bool:
        return (
            self._started_once
            and not self._stop_event.is_set()
            and self._pause_event.is_set()
        )

    @property
    def display_state(self) -> str:
        if self.error:
            return f"Ошибка: {self.error}"
        if self._stop_event.is_set():
            return "Стоп"
        if not self._started_once:
            return "Не запущен"
        if not self._pause_event.is_set():
            return "Пауза"
        return self.state_str

    def start_thread(self):
        if self.stopped:
            return
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
        self._pause_event.set()

    def set_speed(self, delay_ms: int):
        self.delay_ms = delay_ms

    def sleep_step(self) -> bool:
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
        except Exception as exc:
            self.error = f"{type(exc).__name__}: {exc}"
            self._stop_event.set()
        finally:
            self.state_str = "Стоп"

    def execute_step(self):
        pass


class LogSignaler(QObject):
    log_signal = pyqtSignal(str, str)


# ==============================================================================
# ЗАДАНИЕ 1
# ==============================================================================
class FileShared:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.mutex = threading.Lock()
        self.read_pos = 0
        self.written = 0
        self.reads = 0
        self.deleted = 0
        with open(self.filepath, "w", encoding="utf-8"):
            pass


class FileWriterThread(TThread):
    def __init__(self, shared: FileShared, signaler: LogSignaler, delay_ms: int):
        super().__init__(name="P[0]", delay_ms=delay_ms)
        self.shared = shared
        self.signaler = signaler
        self.chars = string.ascii_uppercase + string.digits + string.digits

    def execute_step(self):
        sh = self.shared
        self.state_str = "Ждёт mutex"
        with sh.mutex:
            if self.stopped:
                return
            self.state_str = "КС: запись"
            ch = random.choice(self.chars)
            with open(sh.filepath, "a", encoding="utf-8") as f:
                f.write(ch)
            sh.written += 1
            msg = f"P[0]: → '{ch}'"
            self.signaler.log_signal.emit(msg, msg)
            time.sleep(0.15)
        self.state_str = "Работает"


class FileReaderThread(TThread):
    def __init__(self, shared: FileShared, signaler: LogSignaler, delay_ms: int):
        super().__init__(name="P[1]", delay_ms=delay_ms)
        self.shared = shared
        self.signaler = signaler

    def execute_step(self):
        sh = self.shared
        self.state_str = "Ждёт mutex"
        with sh.mutex:
            if self.stopped:
                return
            self.state_str = "КС: чтение"
            if not os.path.exists(sh.filepath):
                content = ""
            else:
                with open(sh.filepath, "r", encoding="utf-8") as f:
                    content = f.read()

            if len(content) == 0:
                msg = "P[1]: файл пуст"
                self.signaler.log_signal.emit(msg, msg)
            else:
                if sh.read_pos >= len(content):
                    sh.read_pos = 0

                pos = sh.read_pos
                ch = content[pos]
                sh.reads += 1
                if ch.isdigit():
                    new_content = content[:pos] + content[pos + 1 :]
                    with open(sh.filepath, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    sh.deleted += 1
                    msg = f"P[1]: '{ch}' — цифра, удалено"
                    if sh.read_pos >= len(new_content):
                        sh.read_pos = 0
                else:
                    msg = f"P[1]: '{ch}' — буква, оставлено"
                    sh.read_pos = (pos + 1) % len(content)

                self.signaler.log_signal.emit(msg, msg)
            time.sleep(0.15)
        self.state_str = "Работает"


# ==============================================================================
# ЗАДАНИЕ 2
# ==============================================================================
class RingBufferLockVars:
    def __init__(self, size: int = 8):
        self.size = size
        self.buffer = [None] * size
        self.head = 0
        self.tail = 0
        self.count = 0

        self.lock_var = 0
        self.full_lock = 0
        self.empty_lock = 1

        self.produced = 0
        self.consumed = 0
        self.last_consumed = 0
        self.errors = 0

        self._atomic = threading.Lock()

    def acquire_lock_var(self, stop_event, pause_event) -> bool:
        while not stop_event.is_set():
            pause_event.wait()
            if stop_event.is_set():
                return False
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
    def __init__(self, rb: RingBufferLockVars, signaler: LogSignaler, delay_ms: int):
        super().__init__(name="P[0]", delay_ms=delay_ms)
        self.rb = rb
        self.signaler = signaler

    def execute_step(self):
        rb = self.rb
        while rb.full_lock == 1:
            self.state_str = "Блок (full)"
            if not self.wait_poll():
                return

        self.state_str = "Ждёт lock"
        if not rb.acquire_lock_var(self._stop_event, self._pause_event):
            return

        try:
            if rb.count < rb.size:
                self.state_str = "КС: пишет"
                rb.produced += 1
                item = rb.produced
                idx = rb.head
                rb.buffer[idx] = item
                rb.head = (rb.head + 1) % rb.size
                rb.count += 1
                rb.update_flags()
                msg = f"P[0]: → {item} в [{idx}]"
                self.signaler.log_signal.emit(msg, msg)
                time.sleep(0.15)
        finally:
            rb.release_lock_var()
            self.state_str = "Работает"


class ConsumerThread(TThread):
    def __init__(self, rb: RingBufferLockVars, signaler: LogSignaler, delay_ms: int):
        super().__init__(name="P[1]", delay_ms=delay_ms)
        self.rb = rb
        self.signaler = signaler

    def execute_step(self):
        rb = self.rb
        while rb.empty_lock == 1:
            self.state_str = "Блок (empty)"
            if not self.wait_poll():
                return

        self.state_str = "Ждёт lock"
        if not rb.acquire_lock_var(self._stop_event, self._pause_event):
            return

        try:
            if rb.count > 0:
                self.state_str = "КС: читает"
                idx = rb.tail
                item = rb.buffer[idx]
                rb.buffer[idx] = None
                rb.tail = (rb.tail + 1) % rb.size
                rb.count -= 1
                rb.update_flags()

                expected = rb.last_consumed + 1
                if item != expected:
                    rb.errors += 1
                    msg = f"P[1]: ОШИБКА! взял {item}, ждал {expected}"
                else:
                    msg = f"P[1]: ← {item} из [{idx}]"
                if item is not None:
                    rb.last_consumed = item
                rb.consumed += 1
                self.signaler.log_signal.emit(msg, msg)
                time.sleep(0.15)
        finally:
            rb.release_lock_var()
            self.state_str = "Работает"


# ==============================================================================
# Визуализатор кольцевого буфера — реальное кольцо
# ==============================================================================
class RingBufferView(QWidget):
    """Рисует кольцевой буфер как настоящее кольцо с секторами по часовой стрелке."""

    def __init__(self, rb: RingBufferLockVars):
        super().__init__()
        self.rb = rb
        self.setMinimumSize(360, 360)

    def set_buffer(self, rb: RingBufferLockVars):
        self.rb = rb
        self.update()

    def paintEvent(self, event):
        rb = self.rb
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        size = min(w, h)
        cx, cy = w / 2, h / 2
        outer_r = size / 2 - 34  # запас под маркеры H и T
        inner_r = outer_r * 0.52

        n = rb.size
        if n == 0:
            return

        angle_step = 360.0 / n
        # Экранные углы (для sin/cos): -90° — верхняя точка, рост по часовой стрелке
        start_base = -90.0

        painter.translate(cx, cy)
        path_rect = QRectF(-outer_r, -outer_r, outer_r * 2, outer_r * 2)
        inner_rect = QRectF(-inner_r, -inner_r, inner_r * 2, inner_r * 2)

        for i in range(n):
            # Угол в экранной системе координат (по часовой стрелке)
            screen_a0 = start_base + i * angle_step
            # Угол для QPainterPath.arcTo (против часовой стрелки: qt_angle = -screen_angle)
            qt_start_angle = -screen_a0
            qt_sweep_angle = -angle_step

            path = QPainterPath()
            path.moveTo(0, 0)
            path.arcTo(path_rect, qt_start_angle, qt_sweep_angle)
            path.closeSubpath()

            inner_path = QPainterPath()
            inner_path.moveTo(0, 0)
            inner_path.arcTo(inner_rect, qt_start_angle, qt_sweep_angle)
            inner_path.closeSubpath()

            sector = path.subtracted(inner_path)

            val = rb.buffer[i]
            if val is not None:
                color = QColor("#28a745")
                text_color = QColor("#ffffff")
            else:
                color = QColor("#e9ecef")
                text_color = QColor("#6c757d")

            is_head = i == rb.head
            is_tail = i == rb.tail

            painter.setBrush(QBrush(color))
            if is_head and is_tail:
                painter.setPen(QPen(QColor("#ff8c00"), 3))
            elif is_head:
                painter.setPen(QPen(QColor("#0d6efd"), 3))
            elif is_tail:
                painter.setPen(QPen(QColor("#dc3545"), 3))
            else:
                painter.setPen(QPen(QColor("#adb5bd"), 1.2))
            painter.drawPath(sector)

            # Текст значения в центре сектора
            mid_angle = math.radians(screen_a0 + angle_step / 2)
            tr = (outer_r + inner_r) / 2
            tx = tr * math.cos(mid_angle)
            ty = tr * math.sin(mid_angle)
            painter.setPen(QPen(text_color))
            painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            painter.drawText(
                QRectF(tx - 22, ty - 12, 44, 24),
                Qt.AlignmentFlag.AlignCenter,
                str(val) if val is not None else "—",
            )

            # Номер ячейки ближе к внутреннему кругу
            nr = inner_r - 13
            nx = nr * math.cos(mid_angle)
            ny = nr * math.sin(mid_angle)
            painter.setPen(QPen(QColor("#495057")))
            painter.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
            painter.drawText(
                QRectF(nx - 12, ny - 8, 24, 16),
                Qt.AlignmentFlag.AlignCenter,
                str(i),
            )

        # Центральный круг со статистикой
        center_r = max(20.0, inner_r - 22)
        painter.setBrush(QBrush(QColor("#ffffff")))
        painter.setPen(QPen(QColor("#ced4da"), 2))
        painter.drawEllipse(QPointF(0, 0), center_r, center_r)

        painter.setPen(QPen(QColor("#212529")))
        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        painter.drawText(
            QRectF(-center_r, -24, center_r * 2, 18),
            Qt.AlignmentFlag.AlignCenter,
            f"{rb.count}/{rb.size}",
        )
        painter.setFont(QFont("Segoe UI", 8))
        painter.setPen(QPen(QColor("#6c757d")))
        painter.drawText(
            QRectF(-center_r, -6, center_r * 2, 16),
            Qt.AlignmentFlag.AlignCenter,
            "заполнено",
        )
        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
        painter.setPen(QPen(QColor("#212529")))
        painter.drawText(
            QRectF(-center_r, 12, center_r * 2, 16),
            Qt.AlignmentFlag.AlignCenter,
            f"P:{rb.produced}  C:{rb.consumed}",
        )

        # Указатели Head (H) и Tail (T) — разводим по углу, если они в одной ячейке
        same_cell = rb.head == rb.tail
        h_offset = -7.0 if same_cell else 0.0
        t_offset = 7.0 if same_cell else 0.0
        self._draw_marker(
            painter, rb.head, n, outer_r + 16, "H", QColor("#0d6efd"), h_offset
        )
        self._draw_marker(
            painter, rb.tail, n, outer_r + 16, "T", QColor("#dc3545"), t_offset
        )

    def _draw_marker(
        self, painter, idx, n, r, label, color, angle_offset_deg: float = 0.0
    ):
        angle_step = 360.0 / n
        start_base = -90.0
        mid = math.radians(
            start_base + idx * angle_step + angle_step / 2 + angle_offset_deg
        )
        x = r * math.cos(mid)
        y = r * math.sin(mid)
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(QColor("#ffffff"), 1.5))
        painter.drawEllipse(QPointF(x, y), 11, 11)
        painter.setPen(QPen(QColor("#ffffff")))
        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        painter.drawText(
            QRectF(x - 11, y - 11, 22, 22),
            Qt.AlignmentFlag.AlignCenter,
            label,
        )


# ==============================================================================
# Визуализатор файла для Задания 1 — лента с подсветкой
# ==============================================================================
class FileTapeView(QWidget):
    """Рисует содержимое файла как ленту с подсветкой позиции чтения."""

    def __init__(self):
        super().__init__()
        self.chars = ""
        self.read_pos = 0
        self.setMinimumHeight(130)

    def set_data(self, chars: str, read_pos: int):
        self.chars = chars
        self.read_pos = read_pos
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        cell_w = 34
        cell_h = 44
        gap = 4
        y0 = (h - cell_h) / 2 + 6  # смещение вниз, чтобы стрелка сверху не обрезалась

        if not self.chars:
            painter.setPen(QPen(QColor("#adb5bd")))
            painter.setFont(QFont("Segoe UI", 11))
            painter.drawText(
                self.rect(),
                Qt.AlignmentFlag.AlignCenter,
                "(файл пуст)",
            )
            return

        max_cells = max(1, (w - 20) // (cell_w + gap))
        n = len(self.chars)
        if n <= max_cells:
            start = 0
        else:
            start = max(0, min(self.read_pos - max_cells // 2, n - max_cells))
        end = min(n, start + max_cells)

        x = 10
        for i in range(start, end):
            ch = self.chars[i]
            is_pos = i == self.read_pos
            is_digit = ch.isdigit()

            if is_pos:
                bg = QColor("#ffc107")
                fg = QColor("#000000")
                border = QColor("#e67e22")
            elif is_digit:
                bg = QColor("#f8d7da")
                fg = QColor("#c0392b")
                border = QColor("#f5c2c7")
            else:
                bg = QColor("#e7f1ff")
                fg = QColor("#084298")
                border = QColor("#b6d4fe")

            painter.setBrush(QBrush(bg))
            painter.setPen(QPen(border, 2 if is_pos else 1))
            painter.drawRoundedRect(QRectF(x, y0, cell_w, cell_h), 6, 6)

            painter.setPen(QPen(fg))
            painter.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
            painter.drawText(
                QRectF(x, y0, cell_w, cell_h),
                Qt.AlignmentFlag.AlignCenter,
                ch,
            )

            # Индекс ячейки сверху
            painter.setPen(QPen(QColor("#6c757d")))
            painter.setFont(QFont("Segoe UI", 7))
            painter.drawText(
                QRectF(x, y0 - 15, cell_w, 12),
                Qt.AlignmentFlag.AlignCenter,
                str(i),
            )

            x += cell_w + gap

        # Стрелка над позицией чтения
        if start <= self.read_pos < end:
            rx = 10 + (self.read_pos - start) * (cell_w + gap) + cell_w / 2
            painter.setPen(QPen(QColor("#e67e22"), 2))
            painter.setBrush(QBrush(QColor("#e67e22")))
            arrow = QPolygonF(
                [
                    QPointF(rx, y0 - 17),
                    QPointF(rx - 6, y0 - 27),
                    QPointF(rx + 6, y0 - 27),
                ]
            )
            painter.drawPolygon(arrow)


# ==============================================================================
# Панель управления потоком
# ==============================================================================
class ThreadControlPanel(QGroupBox):
    def __init__(self, title: str, thread_getter, thread_factory):
        super().__init__(title)
        self.thread_getter = thread_getter
        self.thread_factory = thread_factory
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        btn_layout = QHBoxLayout()
        self.btn_start = QPushButton("▶")
        self.btn_pause = QPushButton("⏸")
        self.btn_stop = QPushButton("⏹")
        self.btn_start.setFixedWidth(44)
        self.btn_pause.setFixedWidth(44)
        self.btn_stop.setFixedWidth(44)
        self.btn_start.setToolTip("Запуск / Продолжить")
        self.btn_pause.setToolTip("Пауза")
        self.btn_stop.setToolTip("Останов")

        self.btn_start.clicked.connect(self.on_start)
        self.btn_pause.clicked.connect(self.on_pause)
        self.btn_stop.clicked.connect(self.on_stop)

        self.lbl_state = QLabel("Не запущен")
        self.lbl_state.setStyleSheet(
            "padding: 4px 8px; background:#f1f3f5; color:#212529; border-radius:4px;"
        )

        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_pause)
        btn_layout.addWidget(self.btn_stop)
        btn_layout.addWidget(self.lbl_state, 1)
        layout.addLayout(btn_layout)

        initial = self.thread_getter().delay_ms
        speed_layout = QHBoxLayout()
        self.lbl_speed = QLabel(f"{initial} мс")
        self.lbl_speed.setFixedWidth(64)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(100, 3000)
        self.slider.setSingleStep(100)
        self.slider.setValue(initial)
        self.slider.valueChanged.connect(self.on_speed_changed)

        speed_layout.addWidget(self.lbl_speed)
        speed_layout.addWidget(self.slider)
        layout.addLayout(speed_layout)

        self.setLayout(layout)
        self.sync_controls()

    def on_start(self):
        t = self.thread_getter()
        if t is None or t.stopped:
            if t is not None and t.is_alive():
                t.join(timeout=1)
            t = self.thread_factory(self.slider.value())
        t.start_thread()
        self.sync_controls()

    def on_pause(self):
        t = self.thread_getter()
        if t:
            t.pause_thread()
        self.sync_controls()

    def on_stop(self):
        t = self.thread_getter()
        if t:
            t.stop_thread()
        self.sync_controls()

    def on_speed_changed(self, val: int):
        self.lbl_speed.setText(f"{val} мс")
        t = self.thread_getter()
        if t:
            t.set_speed(val)

    def sync_controls(self):
        t = self.thread_getter()
        if t is None:
            self.lbl_state.setText("—")
            self.btn_start.setEnabled(True)
            self.btn_pause.setEnabled(False)
            self.btn_stop.setEnabled(False)
            return

        self.lbl_state.setText(t.display_state)
        self.btn_start.setEnabled(not t.running_active)
        self.btn_pause.setEnabled(t.running_active)
        self.btn_stop.setEnabled(t._started_once and not t.stopped)


def stop_and_join(threads):
    for t in threads:
        if t is not None:
            t.stop_thread()
    for t in threads:
        if t is not None and t.is_alive():
            t.join(timeout=1)


# ==============================================================================
# Задание 1
# ==============================================================================
class Task1Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.shared = FileShared("shared_buffer_var46.txt")
        self.signaler = LogSignaler()
        self.signaler.log_signal.connect(self.on_log)
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
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(12)

        left = QVBoxLayout()
        left.setSpacing(8)

        header = QHBoxLayout()
        title = QLabel("Задание 1 · Мьютекс + файл")
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        header.addWidget(title)
        header.addStretch()
        self.mutex_label = QLabel("mutex: свободен")
        self.mutex_label.setStyleSheet(
            "padding:4px 10px; border-radius:6px; background:#d4edda; color:#155724;"
        )
        header.addWidget(self.mutex_label)
        left.addLayout(header)

        # Визуализация: файл-лента
        tape_group = QGroupBox("Содержимое файла")
        tape_layout = QVBoxLayout()
        self.tape = FileTapeView()
        tape_layout.addWidget(self.tape)
        self.lbl_file_info = QLabel("Длина: 0 · Записано: 0 · Считано: 0 · Удалено: 0")
        tape_layout.addWidget(self.lbl_file_info)
        tape_group.setLayout(tape_layout)
        left.addWidget(tape_group)

        # Две панели потоков рядом
        ctrl_row = QHBoxLayout()
        self.ctrl_p0 = ThreadControlPanel(
            "P[0] · писатель",
            lambda: self.writer_thread,
            self.create_writer,
        )
        self.ctrl_p1 = ThreadControlPanel(
            "P[1] · читатель",
            lambda: self.reader_thread,
            self.create_reader,
        )
        ctrl_row.addWidget(self.ctrl_p0)
        ctrl_row.addWidget(self.ctrl_p1)
        left.addLayout(ctrl_row)

        btn_reset = QPushButton("Сбросить")
        btn_reset.clicked.connect(self.reset_all)
        left.addWidget(btn_reset)
        left.addStretch()

        # Правая колонка — лог
        right = QVBoxLayout()
        right.setSpacing(4)
        right.addWidget(QLabel("События"))
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.document().setMaximumBlockCount(1000)
        right.addWidget(self.log_box)

        main_layout.addLayout(left, 3)
        main_layout.addLayout(right, 2)

    def on_log(self, current: str, log_line: str):
        self.log_box.append(log_line)

    def update_ui_state(self):
        sh = self.shared

        self.ctrl_p0.sync_controls()
        self.ctrl_p1.sync_controls()

        if sh.mutex.locked():
            self.mutex_label.setText("mutex: ЗАНЯТ")
            self.mutex_label.setStyleSheet(
                "padding:4px 10px; border-radius:6px; "
                "background:#f8d7da; color:#842029; font-weight:bold;"
            )
        else:
            self.mutex_label.setText("mutex: свободен")
            self.mutex_label.setStyleSheet(
                "padding:4px 10px; border-radius:6px; "
                "background:#d4edda; color:#155724;"
            )

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

        self.tape.set_data(content, pos)
        self.lbl_file_info.setText(
            f"Длина: {len(content)} · Записано: {written} · "
            f"Считано: {reads} · Удалено: {deleted}"
        )

    def reset_all(self):
        stop_and_join((self.writer_thread, self.reader_thread))
        self.shared = FileShared(self.shared.filepath)
        self.create_writer(self.ctrl_p0.slider.value())
        self.create_reader(self.ctrl_p1.slider.value())
        self.tape.set_data("", 0)
        self.lbl_file_info.setText("Длина: 0 · Записано: 0 · Считано: 0 · Удалено: 0")
        self.log_box.clear()
        self.update_ui_state()


# ==============================================================================
# Задание 2
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
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(12)

        left = QVBoxLayout()
        left.setSpacing(8)

        title = QLabel("Задание 2 · Кольцевой буфер")
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        left.addWidget(title)

        # Кольцо
        ring_group = QGroupBox("Буфер (H — запись, T — чтение)")
        ring_layout = QVBoxLayout()
        self.ring_view = RingBufferView(self.rb)
        ring_layout.addWidget(self.ring_view)
        self.lbl_flags = QLabel("lock_var=0 · full_lock=0 · empty_lock=1 · ошибок: 0")
        self.lbl_flags.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ring_layout.addWidget(self.lbl_flags)
        ring_group.setLayout(ring_layout)
        left.addWidget(ring_group, 1)

        ctrl_row = QHBoxLayout()
        self.ctrl_p0 = ThreadControlPanel(
            "P[0] · производитель",
            lambda: self.producer_thread,
            self.create_producer,
        )
        self.ctrl_p1 = ThreadControlPanel(
            "P[1] · потребитель",
            lambda: self.consumer_thread,
            self.create_consumer,
        )
        ctrl_row.addWidget(self.ctrl_p0)
        ctrl_row.addWidget(self.ctrl_p1)
        left.addLayout(ctrl_row)

        btn_reset = QPushButton("Сбросить")
        btn_reset.clicked.connect(self.reset_all)
        left.addWidget(btn_reset)

        right = QVBoxLayout()
        right.setSpacing(4)
        right.addWidget(QLabel("События"))
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.document().setMaximumBlockCount(1000)
        right.addWidget(self.log_box)

        main_layout.addLayout(left, 3)
        main_layout.addLayout(right, 2)

    def on_log(self, current: str, log_line: str):
        self.log_box.append(log_line)

    def update_ui_state(self):
        rb = self.rb
        self.ctrl_p0.sync_controls()
        self.ctrl_p1.sync_controls()

        self.lbl_flags.setText(
            f"lock_var={rb.lock_var} · full_lock={rb.full_lock} · "
            f"empty_lock={rb.empty_lock} · ошибок: {rb.errors}"
        )
        self.ring_view.update()

    def reset_all(self):
        stop_and_join((self.producer_thread, self.consumer_thread))
        self.rb = RingBufferLockVars(size=8)
        self.ring_view.set_buffer(self.rb)
        self.create_producer(self.ctrl_p0.slider.value())
        self.create_consumer(self.ctrl_p1.slider.value())
        self.log_box.clear()
        self.update_ui_state()


# ==============================================================================
# Главное окно
# ==============================================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Синхронизация процессов — Вариант 46")
        self.resize(1100, 740)

        tabs = QTabWidget()
        self.tab1 = Task1Widget()
        self.tab2 = Task2Widget()
        tabs.addTab(self.tab1, "1 · Мьютекс и файл")
        tabs.addTab(self.tab2, "2 · Кольцевой буфер")
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


def apply_light_palette(app: QApplication):
    """Фиксирует светлую палитру, чтобы кастомная отрисовка не конфликтовала с темной темой ОС."""
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#f8f9fa"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#212529"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#f1f3f5"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#212529"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#212529"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#0d6efd"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    app.setPalette(palette)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    apply_light_palette(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
