"""
Логика лабораторной работы (вариант 46).

Этот модуль НЕ зависит от PyQt и не знает о существовании интерфейса.
Интерфейс (new.py) только создаёт объекты отсюда, запускает/останавливает
потоки и читает их состояние для отрисовки.

Состав:
  - TThread               — универсальный управляемый поток (аналог TThread из VCL):
                            запуск, пауза, остановка, регулировка темпа, состояние;
  - FileShared            — Задание 1: общий файл + мьютекс (Lock) на доступ к нему;
  - RingBufferLockVars    — Задание 2: кольцевой буфер, синхронизация через
                            переменную-замок lock_var и флаги full/empty.

Как логика сообщает о событиях наружу:
  вместо прямых вызовов виджетов шаги принимают функцию-логгер
  `log(msg: str) -> None` (её имплементирует интерфейс). Это позволяет
  запускать и тестировать логику без GUI.
"""

import os
import random
import string
import threading
import time


LogFn = callable


class TThread(threading.Thread):
    """
    Поток, который в цикле повторяет переданную функцию-шаг step_fn.

    Жизненный цикл:  не запущен -> работает <-> пауза -> стоп.
    Повторно запустить остановленный поток нельзя (так устроен threading.Thread),
    поэтому интерфейс при повторном «Запуске» создаёт новый объект TThread.

    Шаг (step_fn) получает сам поток, чтобы иметь доступ к wait_tick()
    и к строке состояния state_str.
    """

    TICK = 0.05

    def __init__(self, name: str, delay_ms: int, step_fn):

        super().__init__(name=name, daemon=True)
        self.delay_ms = delay_ms
        self.step_fn = step_fn

        self._pause = threading.Event()
        self._pause.set()
        self._stop = threading.Event()

        self.state_str = "—"
        self.error = None
        self.started_once = False

    @property
    def stopped(self) -> bool:

        return self._stop.is_set()

    @property
    def running_active(self) -> bool:

        return self.started_once and not self.stopped and self._pause.is_set()

    @property
    def display_state(self) -> str:
        """
        Человекочитаемое состояние для интерфейса.
        Ошибка важнее всего, затем «Стоп», «Не запущен» и «Пауза».
        """
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

        if not self.stopped:
            if not self.started_once:
                self.started_once = True
                self.state_str = "Работает"
                self.start()
            else:
                self._pause.set()

    def pause_thread(self):

        if self.started_once and not self.stopped:
            self._pause.clear()

    def stop_thread(self):

        self._stop.set()
        self._pause.set()

    def wait_tick(self, sec: float = 0.05) -> bool:
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
                    if not self.wait_tick(self.TICK):
                        return
                    elapsed += self.TICK
        except Exception as e:
            self.error = f"{type(e).__name__}: {e}"
            self._stop.set()
        finally:
            self.state_str = "Стоп"


class FileShared:
    """
    Разделяемый файл — «критическая секция» двух процессов:
      P[0] пишет в него случайный символ;
      P[1] читает символ по указателю read_pos и удаляет его, если это цифра.

    Мьютекс (threading.Lock) не даёт обоим потокам одновременно оказаться
    в критической секции, иначе чтение и перезапись файла испортят данные.
    """

    CHARS = string.ascii_uppercase + string.digits * 2

    def __init__(self, filepath="shared_buffer_var46.txt"):
        self.filepath = filepath
        self.mutex = threading.Lock()

        self.read_pos = 0
        self.written = 0
        self.reads = 0
        self.deleted = 0

        open(self.filepath, "w", encoding="utf-8").close()

    def read_content(self) -> str:

        if os.path.exists(self.filepath):
            return open(self.filepath, encoding="utf-8").read()
        return ""

    def write_step(self, t: TThread, log: LogFn):

        t.state_str = "Ждёт mutex"

        with self.mutex:
            if t.stopped:
                return
            t.state_str = "запись"
            ch = random.choice(self.CHARS)
            with open(self.filepath, "a", encoding="utf-8") as f:
                f.write(ch)
            self.written += 1
            log(f"P[0]: → '{ch}'")

            time.sleep(0.15)
        t.state_str = "Работает"

    def read_step(self, t: TThread, log: LogFn):

        t.state_str = "Ждёт mutex"
        with self.mutex:
            if t.stopped:
                return
            t.state_str = "чтение"
            content = self.read_content()
            if not content:
                log("P[1]: файл пуст")
            else:
                self.read_pos %= len(content)
                ch = content[self.read_pos]
                self.reads += 1
                if ch.isdigit():
                    content = content[: self.read_pos] + content[self.read_pos + 1 :]
                    with open(self.filepath, "w", encoding="utf-8") as f:
                        f.write(content)
                    self.deleted += 1

                    self.read_pos = (
                        0 if self.read_pos >= len(content) else self.read_pos
                    )
                    log(f"P[1]: '{ch}' — цифра, удалено")
                else:
                    self.read_pos = (self.read_pos + 1) % len(content)
                    log(f"P[1]: '{ch}' — буква, оставлено")
            time.sleep(0.15)
        t.state_str = "Работает"

    def snapshot(self):
        """
        Безопасный снимок состояния для интерфейса: захватывает мьютекс
        на время чтения файла, чтобы не увидеть «полузаписанное» состояние.
        Возвращает словарь: locked, content, read_pos и счётчики.
        """
        locked = self.mutex.locked()
        with self.mutex:
            return {
                "locked": locked,
                "content": self.read_content(),
                "read_pos": self.read_pos,
                "written": self.written,
                "reads": self.reads,
                "deleted": self.deleted,
            }


class RingBufferLockVars:
    def __init__(self, size: int = 8):
        self.size = size
        self.buffer = [None] * size
        self.head = self.tail = self.count = 0
        self.lock_var = self.full_lock = 0
        self.empty_lock = 1

        self.produced = 0
        self.consumed = 0
        self.last_consumed = 0

    def _acquire(self, t: TThread) -> bool:
        t.state_str = "Ждёт lock"
        while not t.stopped:  # активное ожидание блокирующей переменной
            if self.lock_var == 0:  # проверка возможности занять блокирующую переменную
                self.lock_var = 1
                return True  # заняли бл.пер.
        return False  # не получилось занять

    def _update_flags(self):
        self.full_lock = int(self.count == self.size) # буфер полон
        self.empty_lock = int(self.count == 0) # буфер пуст

    def produce_step(self, t: TThread, log: LogFn):
        while self.full_lock:  ##активное ожидание пока блок полон
            t.state_str = "Блок полон"
        if not self._acquire(t):  # пытаемся занять бл.пер
            return
        try:  # заняли бл.пер
            t.state_str = "пишет"
            self.produced += 1
            idx = self.head
            self.buffer[idx] = self.produced
            self.head = (self.head + 1) % self.size
            self.count += 1
            self._update_flags()
            log(f"P[0]: → {self.produced} в [{idx}]")
        finally:
            t.state_str = "Работает"
            self.lock_var = 0  # освобождаем бл.пер

    def consume_step(self, t: TThread, log: LogFn):

        while self.empty_lock:  ##активное ожидание пока блок пуст
            t.state_str = "Блок пуст"
        if not self._acquire(t):  # если не удалось занять бл.пер, то выходим
            return
        try:  # заняли бл.пер
            t.state_str = "читает"
            idx = self.tail
            item, self.buffer[idx] = self.buffer[idx], None
            self.tail = (self.tail + 1) % self.size
            self.count -= 1
            self._update_flags()
            log(f"P[1]: ← {item} из [{idx}]")
            self.consumed += 1
        finally:
            t.state_str = "Работает"
            self.lock_var = 0  # освобождаем бл.пер

    def snapshot(self) -> dict:

        return {
            "size": self.size,
            "buffer": list(self.buffer),
            "head": self.head,
            "tail": self.tail,
            "count": self.count,
            "lock_var": self.lock_var,
            "full_lock": self.full_lock,
            "empty_lock": self.empty_lock,
            "produced": self.produced,
            "consumed": self.consumed,
            "errors": self.errors,
        }
