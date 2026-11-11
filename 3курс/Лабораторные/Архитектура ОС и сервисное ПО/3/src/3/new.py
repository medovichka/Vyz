"""
Лабораторная работа «Синхронизация процессов», вариант 46 — интерфейс.

Здесь только окна, виджеты, отрисовка и управление потоками.
Вся предметная логика (TThread, общий файл с мьютексом, кольцевой буфер)
вынесена в модуль tasks_logic.py.
"""

import math
import sys

from PyQt6.QtCore import QObject, QPointF, QRectF, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPainterPath, QPen, QPolygonF
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

from tasks_logic import FileShared, RingBufferLockVars, TThread


# ==============================================================================
# Мост «логика -> интерфейс»
# ==============================================================================
class LogSignaler(QObject):
    """
    Логика работает в фоновых потоках и не может напрямую трогать виджеты.
    Шаги вызывают log(msg) — сигнал emit, а Qt сам доставит его в GUI-поток,
    где сообщение допишется в QTextEdit.
    """

    log = pyqtSignal(str)

    def __call__(self, msg: str):
        """Позволяет передавать объект в логику вместо функции-логгера."""
        self.log.emit(msg)


# ==============================================================================
# Визуализаторы (Лента файла и Кольцевой буфер)
# ==============================================================================
class FileTapeView(QWidget):
    """Лента символов файла: текущая позиция читателя отмечена стрелкой."""

    def __init__(self):
        super().__init__()
        self.chars, self.read_pos = "", 0
        self.setMinimumHeight(130)

    def set_data(self, chars: str, read_pos: int):
        self.chars, self.read_pos = chars, read_pos
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        if not self.chars:
            p.setPen(QColor("#adb5bd"))
            p.setFont(QFont("Segoe UI", 11))
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "(файл пуст)")
            return

        cw, ch, gap = 34, 44, 4
        y0 = (self.height() - ch) / 2 + 6
        max_c = max(1, (self.width() - 20) // (cw + gap))
        n = len(self.chars)
        # Показываем «окно» символов вокруг курсора, если файл длиннее виджета.
        start = 0 if n <= max_c else max(0, min(self.read_pos - max_c // 2, n - max_c))
        end = min(n, start + max_c)

        for idx, i in enumerate(range(start, end)):
            x = 10 + idx * (cw + gap)
            c = self.chars[i]
            is_pos = i == self.read_pos
            # Цвета: текущий символ — жёлтый, цифры — красные, буквы — синие.
            bg, fg, brd = (
                ("#ffc107", "#000000", "#e67e22")
                if is_pos
                else ("#f8d7da", "#c0392b", "#f5c2c7")
                if c.isdigit()
                else ("#e7f1ff", "#084298", "#b6d4fe")
            )
            p.setBrush(QColor(bg))
            p.setPen(QPen(QColor(brd), 2 if is_pos else 1))
            p.drawRoundedRect(QRectF(x, y0, cw, ch), 6, 6)

            p.setPen(QColor(fg))
            p.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
            p.drawText(QRectF(x, y0, cw, ch), Qt.AlignmentFlag.AlignCenter, c)

            p.setPen(QColor("#6c757d"))
            p.setFont(QFont("Segoe UI", 7))
            p.drawText(QRectF(x, y0 - 15, cw, 12), Qt.AlignmentFlag.AlignCenter, str(i))

        if start <= self.read_pos < end:
            rx = 10 + (self.read_pos - start) * (cw + gap) + cw / 2
            p.setPen(QPen(QColor("#e67e22"), 2))
            p.setBrush(QColor("#e67e22"))
            p.drawPolygon(
                QPolygonF(
                    [
                        QPointF(rx, y0 - 17),
                        QPointF(rx - 6, y0 - 27),
                        QPointF(rx + 6, y0 - 27),
                    ]
                )
            )


class RingBufferView(QWidget):
    """Кольцевой буфер в виде круга из секторов; H — head, T — tail."""

    def __init__(self, rb: RingBufferLockVars):
        super().__init__()
        self.rb = rb
        self.setMinimumSize(360, 360)

    def paintEvent(self, _):
        rb, n = self.rb, self.rb.size
        if not n:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.translate(self.width() / 2, self.height() / 2)

        outer_r = min(self.width(), self.height()) / 2 - 20
        inner_r = outer_r * 0.52
        step = 360.0 / n
        o_rect = QRectF(-outer_r, -outer_r, outer_r * 2, outer_r * 2)
        i_rect = QRectF(-inner_r, -inner_r, inner_r * 2, inner_r * 2)

        # Сектор для каждой ячейки буфера.
        for i in range(n):
            a0 = -90.0 + i * step
            path, ipath = QPainterPath(), QPainterPath()
            path.arcTo(o_rect, -a0, -step)
            path.closeSubpath()
            ipath.arcTo(i_rect, -a0, -step)
            ipath.closeSubpath()

            val = rb.buffer[i]
            p.setBrush(QColor("#28a745" if val is not None else "#e9ecef"))
            # Обводка: оранжевая при head == tail, синяя у head, красная у tail.
            pen_c, pen_w = (
                ("#ff8c00", 3)
                if i == rb.head == rb.tail
                else ("#0d6efd", 3)
                if i == rb.head
                else ("#dc3545", 3)
                if i == rb.tail
                else ("#adb5bd", 1.2)
            )
            p.setPen(QPen(QColor(pen_c), pen_w))
            p.drawPath(path.subtracted(ipath))

            mid = math.radians(a0 + step / 2)
            tr, nr = (outer_r + inner_r) / 2, inner_r - 13
            p.setPen(QColor("#ffffff" if val is not None else "#6c757d"))
            p.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            p.drawText(
                QRectF(tr * math.cos(mid) - 22, tr * math.sin(mid) - 12, 44, 24),
                Qt.AlignmentFlag.AlignCenter,
                str(val) if val is not None else "—",
            )

            # Номер ячейки во внутреннем кольце.
            p.setPen(QColor("#495057"))
            p.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
            p.drawText(
                QRectF(nr * math.cos(mid) - 12, nr * math.sin(mid) - 8, 24, 16),
                Qt.AlignmentFlag.AlignCenter,
                str(i),
            )

        # Центральный круг со сводкой (заполнение и счётчики).
        cr = max(20.0, inner_r - 22)
        p.setBrush(QColor("#ffffff"))
        p.setPen(QPen(QColor("#ced4da"), 2))
        p.drawEllipse(QPointF(0, 0), cr, cr)

        for y, txt, sz, bold, col in [
            (-24, f"{rb.count}/{rb.size}", 10, True, "#212529"),
            (-6, "заполнено", 8, False, "#6c757d"),
            (12, f"P:{rb.produced}  C:{rb.consumed}", 8, True, "#212529"),
        ]:
            p.setPen(QColor(col))
            p.setFont(
                QFont(
                    "Segoe UI", sz, QFont.Weight.Bold if bold else QFont.Weight.Normal
                )
            )
            p.drawText(QRectF(-cr, y, cr * 2, 18), Qt.AlignmentFlag.AlignCenter, txt)

        # Маркеры H и T (раздвигаются, если указывают на одну ячейку).
        off = 7.0 if rb.head == rb.tail else 0.0
        for idx, lbl, col, da in [
            (rb.head, "H", "#0d6efd", -off),
            (rb.tail, "T", "#dc3545", off),
        ]:
            ang = math.radians(-90.0 + (idx + 0.5) * step + da)
            x, y = (outer_r + 16) * math.cos(ang), (outer_r + 16) * math.sin(ang)
            p.setBrush(QColor(col))
            p.setPen(QPen(QColor("#ffffff"), 1.5))
            p.drawEllipse(QPointF(x, y), 11, 11)
            p.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
            p.drawText(
                QRectF(x - 11, y - 11, 22, 22), Qt.AlignmentFlag.AlignCenter, lbl
            )


# ==============================================================================
# Панель управления и Базовая вкладка
# ==============================================================================
class ThreadControlPanel(QGroupBox):
    """Кнопки ▶ ⏸ ⏹, состояние потока и ползунок скорости для одного потока."""

    def __init__(self, title: str, initial_ms: int, factory):
        super().__init__(title)
        self.factory = factory  # фабрика логики: delay_ms -> TThread
        self.thread: TThread = self.factory(initial_ms)

        v = QVBoxLayout(self)
        h_btn = QHBoxLayout()
        self.btn_start, self.btn_pause, self.btn_stop = (
            QPushButton("▶"),
            QPushButton("⏸"),
            QPushButton("⏹"),
        )
        for b, fn in [
            (self.btn_start, self.start),
            (self.btn_pause, self.pause),
            (self.btn_stop, self.stop),
        ]:
            b.setFixedWidth(44)
            b.clicked.connect(fn)
            h_btn.addWidget(b)

        self.lbl_state = QLabel("Не запущен")
        self.lbl_state.setStyleSheet(
            "padding:4px 8px; background:#f1f3f5; border-radius:4px;"
        )
        h_btn.addWidget(self.lbl_state, 1)
        v.addLayout(h_btn)

        h_spd = QHBoxLayout()
        self.lbl_spd = QLabel(f"{initial_ms} мс")
        self.lbl_spd.setFixedWidth(64)
        self.slider = QSlider(
            Qt.Orientation.Horizontal,
            minimum=100,
            maximum=3000,
            singleStep=100,
            value=initial_ms,
        )
        self.slider.valueChanged.connect(self._on_speed)
        h_spd.addWidget(self.lbl_spd)
        h_spd.addWidget(self.slider)
        v.addLayout(h_spd)
        self.sync()

    def start(self):
        # Поток Python не перезапускается, поэтому после останова
        # создаём новый объект TThread через фабрику.
        if self.thread.stopped:
            if self.thread.is_alive():
                self.thread.join(timeout=1)
            self.thread = self.factory(self.slider.value())
        self.thread.start_thread()
        self.sync()

    def pause(self):
        self.thread.pause_thread()
        self.sync()

    def stop(self):
        self.thread.stop_thread()
        self.sync()

    def _on_speed(self, val: int):
        self.lbl_spd.setText(f"{val} мс")
        self.thread.delay_ms = val

    def reset(self):
        self.stop_and_join()
        self.thread = self.factory(self.slider.value())
        self.sync()

    def stop_and_join(self):
        self.thread.stop_thread()
        if self.thread.is_alive():
            self.thread.join(timeout=1)

    def sync(self):
        """Обновить подпись состояния и доступность кнопок по состоянию потока."""
        t = self.thread
        self.lbl_state.setText(t.display_state)
        self.btn_start.setEnabled(not t.running_active)
        self.btn_pause.setEnabled(t.running_active)
        self.btn_stop.setEnabled(t.started_once and not t.stopped)


class BaseTaskTab(QWidget):
    """Общая раскладка вкладки: визуализация + панели потоков + журнал событий."""

    def __init__(self, title_text: str, p0_cfg: tuple, p1_cfg: tuple):
        super().__init__()
        self.sig = LogSignaler()
        main = QHBoxLayout(self)
        self.left = QVBoxLayout()

        self.header = QHBoxLayout()
        lbl = QLabel(title_text)
        lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.header.addWidget(lbl)
        self.header.addStretch()
        self.left.addLayout(self.header)

        self.body_slot = QVBoxLayout()
        self.left.addLayout(self.body_slot, 1)

        ctrl_row = QHBoxLayout()
        self.ctrl_p0 = ThreadControlPanel(*p0_cfg)
        self.ctrl_p1 = ThreadControlPanel(*p1_cfg)
        ctrl_row.addWidget(self.ctrl_p0)
        ctrl_row.addWidget(self.ctrl_p1)
        self.left.addLayout(ctrl_row)
        btn_rst = QPushButton("Сбросить")
        btn_rst.clicked.connect(self.reset_all)
        self.left.addWidget(btn_rst)

        right = QVBoxLayout()
        right.addWidget(QLabel("События"))
        self.log_box = QTextEdit(readOnly=True)
        self.log_box.document().setMaximumBlockCount(1000)
        self.sig.log.connect(self.log_box.append)
        right.addWidget(self.log_box)

        main.addLayout(self.left, 3)
        main.addLayout(right, 2)

        # Периодическое обновление подписей и визуализации (GUI-поток).
        self.timer = QTimer(self, timeout=self._tick)
        self.timer.start(100)

    def _tick(self):
        self.ctrl_p0.sync()
        self.ctrl_p1.sync()
        self.update_view()

    def stop_threads(self):
        self.ctrl_p0.stop_and_join()
        self.ctrl_p1.stop_and_join()

    def update_view(self):
        pass

    def reset_all(self):
        pass


# ==============================================================================
# Вкладки Заданий 1 и 2 + Главное окно
# ==============================================================================
class Task1Widget(BaseTaskTab):
    """Вкладка «Мьютекс + файл»."""

    def __init__(self):
        self.shared = FileShared()
        super().__init__(
            "Задание 1 · Мьютекс + файл",
            (
                "P[0] · писатель",
                1000,
                # Шаг потока — метод логики; sig передаётся как логгер.
                lambda d: TThread(
                    "P[0]", d, lambda t: self.shared.write_step(t, self.sig)
                ),
            ),
            (
                "P[1] · читатель",
                1200,
                lambda d: TThread(
                    "P[1]", d, lambda t: self.shared.read_step(t, self.sig)
                ),
            ),
        )
        self.mutex_lbl = QLabel()
        self.header.addWidget(self.mutex_lbl)

        grp = QGroupBox("Содержимое файла")
        gl = QVBoxLayout(grp)
        self.tape = FileTapeView()
        self.lbl_info = QLabel()
        gl.addWidget(self.tape)
        gl.addWidget(self.lbl_info)
        self.body_slot.addWidget(grp)
        self.body_slot.addStretch()
        self.update_view()

    def update_view(self):
        snap = self.shared.snapshot()
        locked = snap["locked"]
        self.mutex_lbl.setText("mutex: ЗАНЯТ" if locked else "mutex: свободен")
        self.mutex_lbl.setStyleSheet(
            f"padding:4px 10px; border-radius:6px; background:{'#f8d7da' if locked else '#d4edda'}; "
            f"color:{'#842029' if locked else '#155724'}; font-weight:{'bold' if locked else 'normal'};"
        )
        self.tape.set_data(snap["content"], snap["read_pos"])
        self.lbl_info.setText(
            f"Длина: {len(snap['content'])} · Записано: {snap['written']} · "
            f"Считано: {snap['reads']} · Удалено: {snap['deleted']}"
        )

    def reset_all(self):
        self.stop_threads()
        self.shared = FileShared()
        self.ctrl_p0.reset()
        self.ctrl_p1.reset()
        self.log_box.clear()
        self.update_view()


class Task2Widget(BaseTaskTab):
    """Вкладка «Кольцевой буфер»."""

    def __init__(self):
        self.rb = RingBufferLockVars(8)
        super().__init__(
            "Задание 2 · Кольцевой буфер",
            (
                "P[0] · производитель",
                900,
                lambda d: TThread(
                    "P[0]", d, lambda t: self.rb.produce_step(t, self.sig)
                ),
            ),
            (
                "P[1] · потребитель",
                1300,
                lambda d: TThread(
                    "P[1]", d, lambda t: self.rb.consume_step(t, self.sig)
                ),
            ),
        )
        grp = QGroupBox("Буфер (H — запись, T — чтение)")
        gl = QVBoxLayout(grp)
        self.ring = RingBufferView(self.rb)
        self.lbl_flags = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        gl.addWidget(self.ring, 1)
        gl.addWidget(self.lbl_flags)
        self.body_slot.addWidget(grp, 1)
        self.update_view()

    def update_view(self):
        snap = self.rb.snapshot()
        self.lbl_flags.setText(
            f"lock_var={snap['lock_var']} · full_lock={snap['full_lock']} · "
            f"empty_lock={snap['empty_lock']} · ошибок: {snap['errors']}"
        )
        self.ring.update()

    def reset_all(self):
        self.stop_threads()
        self.rb = RingBufferLockVars(8)
        self.ring.rb = self.rb
        self.ctrl_p0.reset()
        self.ctrl_p1.reset()
        self.log_box.clear()
        self.update_view()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(windowTitle="Синхронизация процессов — Вариант 46")
        self.resize(1100, 740)
        tabs = QTabWidget()
        self.t1, self.t2 = Task1Widget(), Task2Widget()
        tabs.addTab(self.t1, "1 · Мьютекс и файл")
        tabs.addTab(self.t2, "2 · Кольцевой буфер")
        self.setCentralWidget(tabs)

    def closeEvent(self, event):
        # Корректно останавливаем фоновые потоки перед выходом.
        self.t1.stop_threads()
        self.t2.stop_threads()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(
        "QWidget { background: #f8f9fa; color: #212529; } QTextEdit, QPushButton { background: #ffffff; }"
    )
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
