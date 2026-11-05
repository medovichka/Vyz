import math, os, random, string, sys, threading, time
from PyQt6.QtCore import QObject, QPointF, QRectF, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen, QPolygonF
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


class LogSignaler(QObject):
    log = pyqtSignal(str)


# ==============================================================================
# Универсальный управляемый поток
# ==============================================================================
class TThread(threading.Thread):
    def __init__(self, name, delay_ms, step_fn):
        super().__init__(name=name, daemon=True)
        self.delay_ms, self.step_fn = delay_ms, step_fn
        self._pause, self._stop = threading.Event(), threading.Event()
        self._pause.set()
        self.state_str, self.error, self.started_once = "—", None, False

    stopped = property(lambda s: s._stop.is_set())
    running_active = property(
        lambda s: s.started_once and not s.stopped and s._pause.is_set()
    )

    @property
    def display_state(self):
        if self.error:
            return f"Ошибка: {self.error}"
        if self.stopped:
            return "Стоп"
        if not self.started_once:
            return "Не запущен"
        if not self._pause.is_set():
            return "Пауза"
        return self.state_str

    def start_thread(self):
        if self.stopped:
            return
        if self.started_once:
            self._pause.set()
            return
        self.started_once, self.state_str = True, "Работает"
        self.start()

    def pause_thread(self):
        if self.started_once and not self.stopped:
            self._pause.clear()

    def stop_thread(self):
        self._stop.set()
        self._pause.set()

    def wait_tick(self, sec=0.05):
        self._pause.wait()
        if self.stopped:
            return False
        time.sleep(sec)
        return not self.stopped

    def run(self):
        try:
            while not self.stopped:
                self._pause.wait()
                if self.stopped:
                    break
                self.step_fn(self)
                elapsed = 0.0
                while elapsed * 1000 < self.delay_ms:
                    if not self.wait_tick():
                        return
                    elapsed += 0.05
        except Exception as e:
            self.error = f"{type(e).__name__}: {e}"
            self._stop.set()
        finally:
            self.state_str = "Стоп"


# ==============================================================================
# Модели Заданий 1 и 2
# ==============================================================================
class FileShared:
    CHARS = string.ascii_uppercase + string.digits * 2

    def __init__(self, filepath="shared_buffer_var46.txt"):
        self.filepath = filepath
        self.mutex = threading.Lock()
        self.read_pos = self.written = self.reads = self.deleted = 0
        open(filepath, "w", encoding="utf-8").close()

    def write_step(self, t, sig):
        t.state_str = "Ждёт mutex"
        with self.mutex:
            if t.stopped:
                return
            t.state_str = "КС: запись"
            ch = random.choice(self.CHARS)
            open(self.filepath, "a", encoding="utf-8").write(ch)
            self.written += 1
            sig.log.emit(f"P[0]: → '{ch}'")
            time.sleep(0.15)
        t.state_str = "Работает"

    def read_step(self, t, sig):
        t.state_str = "Ждёт mutex"
        with self.mutex:
            if t.stopped:
                return
            t.state_str = "КС: чтение"
            content = (
                open(self.filepath, encoding="utf-8").read()
                if os.path.exists(self.filepath)
                else ""
            )
            if not content:
                sig.log.emit("P[1]: файл пуст")
            else:
                self.read_pos %= len(content)
                ch = content[self.read_pos]
                self.reads += 1
                if ch.isdigit():
                    content = content[: self.read_pos] + content[self.read_pos + 1 :]
                    open(self.filepath, "w", encoding="utf-8").write(content)
                    self.deleted += 1
                    self.read_pos = (
                        0 if self.read_pos >= len(content) else self.read_pos
                    )
                    sig.log.emit(f"P[1]: '{ch}' — цифра, удалено")
                else:
                    self.read_pos = (self.read_pos + 1) % len(content)
                    sig.log.emit(f"P[1]: '{ch}' — буква, оставлено")
            time.sleep(0.15)
        t.state_str = "Работает"


class RingBufferLockVars:
    def __init__(self, size=8):
        self.size = size
        self.buffer = [None] * size
        self.head = self.tail = self.count = 0
        self.lock_var = self.full_lock = 0
        self.empty_lock = 1
        self.produced = self.consumed = self.last_consumed = self.errors = 0
        self._atomic = threading.Lock()

    def _acquire(self, t):
        t.state_str = "Ждёт lock"
        while not t.stopped:
            t._pause.wait()
            with self._atomic:
                if self.lock_var == 0:
                    self.lock_var = 1
                    return True
            time.sleep(0.05)
        return False

    def _release(self, t):
        with self._atomic:
            self.lock_var = 0
        t.state_str = "Работает"

    def _update_flags(self):
        self.full_lock = int(self.count == self.size)
        self.empty_lock = int(self.count == 0)

    def produce_step(self, t, sig):
        while self.full_lock:
            t.state_str = "Блок (full)"
            if not t.wait_tick():
                return
        if not self._acquire(t):
            return
        try:
            if self.count < self.size:
                t.state_str = "КС: пишет"
                self.produced += 1
                idx = self.head
                self.buffer[idx] = self.produced
                self.head = (self.head + 1) % self.size
                self.count += 1
                self._update_flags()
                sig.log.emit(f"P[0]: → {self.produced} в [{idx}]")
                time.sleep(0.15)
        finally:
            self._release(t)

    def consume_step(self, t, sig):
        while self.empty_lock:
            t.state_str = "Блок (empty)"
            if not t.wait_tick():
                return
        if not self._acquire(t):
            return
        try:
            if self.count > 0:
                t.state_str = "КС: читает"
                idx = self.tail
                item, self.buffer[idx] = self.buffer[idx], None
                self.tail = (self.tail + 1) % self.size
                self.count -= 1
                self._update_flags()
                exp = self.last_consumed + 1
                if item != exp:
                    self.errors += 1
                    sig.log.emit(f"P[1]: ОШИБКА! взял {item}, ждал {exp}")
                else:
                    sig.log.emit(f"P[1]: ← {item} из [{idx}]")
                if item is not None:
                    self.last_consumed = item
                self.consumed += 1
                time.sleep(0.15)
        finally:
            self._release(t)


# ==============================================================================
# Визуализаторы
# ==============================================================================
class FileTapeView(QWidget):
    COLORS = {  # (фон, текст, рамка)
        "pos": ("#ffc107", "#000000", "#e67e22"),
        "digit": ("#f8d7da", "#c0392b", "#f5c2c7"),
        "letter": ("#e7f1ff", "#084298", "#b6d4fe"),
    }

    def __init__(self):
        super().__init__()
        self.chars, self.read_pos = "", 0
        self.setMinimumHeight(130)

    def set_data(self, chars, read_pos):
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
        start = 0 if n <= max_c else max(0, min(self.read_pos - max_c // 2, n - max_c))
        end = min(n, start + max_c)

        for idx, i in enumerate(range(start, end)):
            x = 10 + idx * (cw + gap)
            c = self.chars[i]
            key = (
                "pos" if i == self.read_pos else ("digit" if c.isdigit() else "letter")
            )
            bg, fg, brd = self.COLORS[key]
            p.setBrush(QColor(bg))
            p.setPen(QPen(QColor(brd), 2 if key == "pos" else 1))
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
    PEN = {  # (цвет, толщина)
        "both": ("#ff8c00", 3),
        "head": ("#0d6efd", 3),
        "tail": ("#dc3545", 3),
        "none": ("#adb5bd", 1.2),
    }

    def __init__(self, rb):
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
        R = min(self.width(), self.height()) / 2 - 20
        r = R * 0.52
        step = 360.0 / n
        o_rect, i_rect = QRectF(-R, -R, R * 2, R * 2), QRectF(-r, -r, r * 2, r * 2)

        for i in range(n):
            a0 = -90.0 + i * step
            outer = QPainterPath()
            outer.arcTo(o_rect, -a0, -step)
            outer.closeSubpath()
            inner = QPainterPath()
            inner.arcTo(i_rect, -a0, -step)
            inner.closeSubpath()
            val = rb.buffer[i]
            key = (
                "both"
                if i == rb.head == rb.tail
                else "head"
                if i == rb.head
                else "tail"
                if i == rb.tail
                else "none"
            )
            pen_c, pen_w = self.PEN[key]
            p.setBrush(QColor("#28a745" if val is not None else "#e9ecef"))
            p.setPen(QPen(QColor(pen_c), pen_w))
            p.drawPath(outer.subtracted(inner))

            mid = math.radians(a0 + step / 2)
            tr, nr = (R + r) / 2, r - 13
            p.setPen(QColor("#ffffff" if val is not None else "#6c757d"))
            p.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            p.drawText(
                QRectF(tr * math.cos(mid) - 22, tr * math.sin(mid) - 12, 44, 24),
                Qt.AlignmentFlag.AlignCenter,
                str(val) if val is not None else "—",
            )
            p.setPen(QColor("#495057"))
            p.setFont(QFont("Segoe UI", 8, QFont.Weight.DemiBold))
            p.drawText(
                QRectF(nr * math.cos(mid) - 12, nr * math.sin(mid) - 8, 24, 16),
                Qt.AlignmentFlag.AlignCenter,
                str(i),
            )

        cr = max(20.0, r - 22)
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

        off = 7.0 if rb.head == rb.tail else 0.0
        for idx, lbl, col, da in [
            (rb.head, "H", "#0d6efd", -off),
            (rb.tail, "T", "#dc3545", off),
        ]:
            ang = math.radians(-90.0 + (idx + 0.5) * step + da)
            x, y = (R + 16) * math.cos(ang), (R + 16) * math.sin(ang)
            p.setBrush(QColor(col))
            p.setPen(QPen(QColor("#ffffff"), 1.5))
            p.drawEllipse(QPointF(x, y), 11, 11)
            p.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
            p.drawText(
                QRectF(x - 11, y - 11, 22, 22), Qt.AlignmentFlag.AlignCenter, lbl
            )


# ==============================================================================
# Управление потоком
# ==============================================================================
class ThreadControlPanel(QGroupBox):
    def __init__(self, title, initial_ms, factory):
        super().__init__(title)
        self.factory = factory
        self.thread = factory(initial_ms)

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

    def _rebuild(self):
        self.stop_and_join()
        self.thread = self.factory(self.slider.value())

    def start(self):
        if self.thread.stopped:
            self._rebuild()
        self.thread.start_thread()
        self.sync()

    def pause(self):
        self.thread.pause_thread()
        self.sync()

    def stop(self):
        self.thread.stop_thread()
        self.sync()

    def _on_speed(self, val):
        self.lbl_spd.setText(f"{val} мс")
        self.thread.delay_ms = val

    def reset(self):
        self._rebuild()
        self.sync()

    def stop_and_join(self):
        self.thread.stop_thread()
        if self.thread.is_alive():
            self.thread.join(timeout=1)

    def sync(self):
        t = self.thread
        self.lbl_state.setText(t.display_state)
        self.btn_start.setEnabled(not t.running_active)
        self.btn_pause.setEnabled(t.running_active)
        self.btn_stop.setEnabled(t.started_once and not t.stopped)


# ==============================================================================
# Общая вкладка
# ==============================================================================
class BaseTaskTab(QWidget):
    def __init__(self, title_text, p0_cfg, p1_cfg):
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

        btn = QPushButton("Сбросить")
        btn.clicked.connect(self.reset_all)
        self.left.addWidget(btn)

        right = QVBoxLayout()
        right.addWidget(QLabel("События"))
        self.log_box = QTextEdit(readOnly=True)
        self.log_box.document().setMaximumBlockCount(1000)
        self.sig.log.connect(self.log_box.append)
        right.addWidget(self.log_box)

        main.addLayout(self.left, 3)
        main.addLayout(right, 2)
        self.timer = QTimer(self, timeout=self._tick)
        self.timer.start(100)

    def _tick(self):
        self.ctrl_p0.sync()
        self.ctrl_p1.sync()
        self.update_view()

    def stop_threads(self):
        self.ctrl_p0.stop_and_join()
        self.ctrl_p1.stop_and_join()

    def reset_all(self):
        self.stop_threads()
        self._reset_model()
        self.ctrl_p0.reset()
        self.ctrl_p1.reset()
        self.log_box.clear()
        self.update_view()

    def _reset_model(self):
        pass

    def update_view(self):
        pass


# ==============================================================================
# Задание 1
# ==============================================================================
class Task1Widget(BaseTaskTab):
    def __init__(self):
        self.shared = FileShared()
        super().__init__(
            "Задание 1 · Мьютекс + файл",
            (
                "P[0] · писатель",
                1000,
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
        sh = self.shared
        locked = sh.mutex.locked()
        self.mutex_lbl.setText("mutex: ЗАНЯТ" if locked else "mutex: свободен")
        self.mutex_lbl.setStyleSheet(
            f"padding:4px 10px; border-radius:6px; "
            f"background:{'#f8d7da' if locked else '#d4edda'}; "
            f"color:{'#842029' if locked else '#155724'}; "
            f"font-weight:{'bold' if locked else 'normal'};"
        )
        if sh.mutex.acquire(blocking=False):
            try:
                c = (
                    open(sh.filepath, encoding="utf-8").read()
                    if os.path.exists(sh.filepath)
                    else ""
                )
                self.tape.set_data(c, sh.read_pos)
                self.lbl_info.setText(
                    f"Длина: {len(c)} · Записано: {sh.written} · "
                    f"Считано: {sh.reads} · Удалено: {sh.deleted}"
                )
            finally:
                sh.mutex.release()

    def _reset_model(self):
        self.shared = FileShared()


# ==============================================================================
# Задание 2
# ==============================================================================
class Task2Widget(BaseTaskTab):
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
        self.lbl_flags = QLabel()
        self.lbl_flags.setAlignment(Qt.AlignmentFlag.AlignCenter)
        gl.addWidget(self.ring, 1)
        gl.addWidget(self.lbl_flags)
        self.body_slot.addWidget(grp, 1)
        self.update_view()

    def update_view(self):
        rb = self.rb
        self.lbl_flags.setText(
            f"lock_var={rb.lock_var} · full_lock={rb.full_lock} · "
            f"empty_lock={rb.empty_lock} · ошибок: {rb.errors}"
        )
        self.ring.update()

    def _reset_model(self):
        self.rb = RingBufferLockVars(8)
        self.ring.rb = self.rb


# ==============================================================================
# Главное окно
# ==============================================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Синхронизация процессов — Вариант 46")
        self.resize(1100, 740)
        tabs = QTabWidget()
        self.t1, self.t2 = Task1Widget(), Task2Widget()
        tabs.addTab(self.t1, "1 · Мьютекс и файл")
        tabs.addTab(self.t2, "2 · Кольцевой буфер")
        self.setCentralWidget(tabs)

    def closeEvent(self, event):
        self.t1.stop_threads()
        self.t2.stop_threads()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(
        "QWidget { background: #f8f9fa; color: #212529; } "
        "QTextEdit, QPushButton { background: #ffffff; }"
    )
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
