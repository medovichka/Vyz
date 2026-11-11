from math import log
import os
import random
import string
import threading
import time

LogFn = callable

class TThread(threading.Thread):

    TICK = 0.05

    def __init__(self, name: str, delay_ms: int, step_fn):
        daemon=True
        super().__init__(name=name, daemon=True)
        self.delay_ms = delay_ms   # пауза между шагами, мс (меняется ползунком)
        self.step_fn = step_fn     # одна итерация работы потока

        self._pause = threading.Event()
        self._pause.set()          # поток по умолчанию не на паузе
        self._stop = threading.Event()  # set() = запрошена остановка

        self.state_str = "—"       # текущее подробное состояние (КС, блокировка и т.п.)
        self.error = None          # текст исключения, если шаг упал
        self.started_once = False  # был ли поток вообще запущен

    @property
    def stopped(self) -> bool:

        return self._stop.is_set()

    @property
    def running_active(self) -> bool:

        return self.started_once and not self.stopped and self._pause.is_set()

    @property
    def display_state(self) -> str:
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
        self._pause.wait()          # стоять, пока поток на паузе
        if self.stopped:
            return False
        time.sleep(sec)
        return not self.stopped

    def run(self):

        try:
            while not self.stopped:
                self._pause.wait()          # ждём, пока нас не снимут с паузы
                if self.stopped:
                    break
                self.step_fn(self)          # одна итерация работы
                elapsed = 0.0               # выдерживаем задержку по TICK-кускам,
                while elapsed * 1000 < self.delay_ms:  # чтобы пауза/стоп реагировали сразу
                    if not self.wait_tick(self.TICK):
                        return
                    elapsed += self.TICK
        except Exception as e:
            self.error = f"{type(e).__name__}: {e}"
            self._stop.set()
        finally:
            self.state_str = "Стоп"

class FileShared:
    CHARS = string.ascii_uppercase + string.digits * 2

    def __init__(self, filepath="shared_buffer_var46.txt"):
        self.filepath = filepath
        self.mutex = threading.Lock()   # мьютекс критической секции
        self.read_pos = 0    # позиция «курсора» читателя в файле
        self.written = 0     # сколько символов записано
        self.reads = 0       # сколько символов прочитано
        self.deleted = 0     # сколько цифр удалено
        open(self.filepath, "w", encoding="utf-8").close()

    def read_content(self) -> str:

        if os.path.exists(self.filepath):
            return open(self.filepath, encoding="utf-8").read()
        return ""

    def write_step(self, t: TThread, log: LogFn):

        t.state_str = "Ждёт mutex"
        with self.mutex:
            if t.stopped:
                return                      # остановку проверяем уже под мьютексом
            t.state_str = "КС: запись"
            ch = random.choice(self.CHARS)
            with open(self.filepath, "a", encoding="utf-8") as f:
                f.write(ch)                 # режим "a" — дописать в конец
            self.written += 1
            log(f"P[0]: → '{ch}'")
            time.sleep(0.15)
        t.state_str = "Работает"

    def read_step(self, t: TThread, log: LogFn):

        t.state_str = "Ждёт mutex"
        with self.mutex:
            if t.stopped:
                return
            t.state_str = "КС: чтение"
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
        self.buffer = [None] * size # Кольцо, сколько элементов
        self.head = self.tail = self.count = 0
        self.lock_var = self.full_lock = 0 # Замок КС = 0 в начале
        self.empty_lock = 1  # Кольцо в начале пустое
        self.produced = 0  # сколько произведено
        self.consumed = 0  # сколько потребил
        self.last_consumed = 0 # последнее взятое значение
        self.errors = 0  # нарушений порядка выдачи
        self._atomic = threading.Lock()

    def _acquire(self, t: TThread) -> bool:
            t.state_str = "Ждёт lock"
            while not t.stopped: #активное ожидание блок.перем. = 0 (ждём пока переменная не станет доступной) пока поток не остановлен
                t._pause.wait()  # если поставили на паузу - ждём её окончания
                if self.lock_var == 0: # проверка возможности занять блокирующую переменную
                    self.lock_var = 1 # заняли бл.пер.
                    return True
                time.sleep(0.05)
            return False # иначе, если поток не остановлен, не на паузе и не сумел занять бл.пер., возвращаем FAlse

    def _release(self, t: TThread): # функция освобождения переменной
        self.lock_var = 0 # освобождаем переменную
        t.state_str = "Работает" # отображение статуса потока в интерфейсе

    def _update_flags(self): # обновление флагов full_lock и empty_lock

        self.full_lock = int(self.count == self.size) # если кольцо полное
        self.empty_lock = int(self.count == 0) # если кольцо пустое

    def produce_step(self, t: TThread, log: LogFn): # шаг производителя

        while self.full_lock: # активное ожидание если блок полон
            t.state_str = "Блок (full)" # выводим сообщение что полон
        if not self._acquire(t): # пытаемся получить замок, если не удалось, то выходим
            return
        try:  # если заняли замок
            t.state_str = "КС: пишет" # выводим сообщение что пишем
            self.produced += 1 # увеличиваем счетчик произведенных элементов
            idx = self.head # индекс куда будем писать
            self.buffer[idx] = self.produced # записываем в кольцо
            self.head = (self.head + 1) % self.size   # кольцевой сдвиг
            self.count += 1 # увеличиваем счетчик элементов в кольце
            self._update_flags() # обновляем флаги full_lock и empty_lock
            log(f"P[0]: → {self.produced} в [{idx}]") # в консоль запись события
            time.sleep(0.15) #задержка для интерфейса
        finally:
            self._release(t)                    # отпускаем замок

    def consume_step(self, t: TThread): # шаг потребителя

        while self.empty_lock: # если блок пуст
            t.state_str = "Блок (empty)" # выводим сообщение что пуст
        if not self._acquire(t): # пытаемся получить замок, если не удалось, то выходим
            return
        try: # если заняли замок
            t.state_str = "КС: читает" # выводим сообщение что читаем
            idx = self.tail # индекс откуда будем читать
            item, self.buffer[idx] = self.buffer[idx], None # читаем из кольца и обнуляем ячейку
            self.tail = (self.tail + 1) % self.size   # кольцевой сдвиг
            self.count -= 1 # уменьшаем счетчик элементов в кольце
            self._update_flags() # обновляем флаги
            log(f"P[1]: ← {item} из [{idx}]") # выводим в консоль событие
            self.last_consumed = item # схраняем последнее прочитанное значение
            self.consumed += 1 # увеличиваем счётчик прочитанных
            time.sleep(0.15) # ожидание для интерфейса
        finally:
            self._release(t) # освобождаем замок
