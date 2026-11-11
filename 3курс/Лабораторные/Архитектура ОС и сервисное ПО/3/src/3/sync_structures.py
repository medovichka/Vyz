"""


Задание 1: «С помощью мьютексов организовать работу параллельных вычислительных
           потоков. Первый поток записывает в файл случайные символы. Второй поток
           считывает из файла символ и удаляет его, если это цифра.»
Задание 2: «Задачу о производителе и потребителе с кольцевым буфером решить
           с помощью блокирующих переменных.»





Задание 1 — мьютекс (threading.Lock):
  * Объект:   FileShared.mutex  («взаимное исключение» доступа к файлу).
  * Где:      FileShared.write_step  — писатель держит мьютекс, пока дописывает
              символ в файл (иначе две записи слились бы в одно слово).
              FileShared.read_step   — читатель держит мьютекс, пока читает файл
              и, возможно, перезаписывает его без удалённой цифры
              (иначе запись писателя и перезапись читателя потеряют данные).
              FileShared.snapshot    — интерфейс читает файл тоже под мьютексом.
  * Как:      `with self.mutex:` — вход в критическую секцию;
              другой поток внутри секции одновременно быть не может и ждёт.
              Открытие/чтение/запись файла — это и есть критическая секция,
              поэтому мьютекс берётся ДО первой операции с файлом
              и отпускается ПОСЛЕ последней.

Задание 2 — блокирующие переменные (для каждой ячейки / для состояния буфера):
  * lock_var   — «замок» критической секции: 0 = свободен, 1 = занят.
                 Где: RingBufferLockVars._acquire (проверка+захват) и
                 RingBufferLockVars._release (освобождение). Захват одной
                 переменной заменяет мьютекс Задания 1.
  * full_lock  — блокирующая переменная производителя: 1 → буфер полон,
                 производитель стоит в цикле `while self.full_lock`.
  * empty_lock — блокирующая переменная потребителя: 1 → буфер пуст,
                 потребитель стоит в цикле `while self.empty_lock`.
                 Флаги пересчитываются в _update_flags() после каждого
                 изменения count и проверяются ДО входа в критическую секцию
                 и ещё раз внутри неё (повторная проверка).

  * Пояснение по терминологии: в классической задаче о производителе и
    потребителе «умные» блокирующие переменные переходят в состояние
    «заблокирован»/операция блокируется через защищённую операцию над
    самим флагом — здесь эту роль играет _acquire: проверка lock_var и запись
    lock_var = 1 выполняются как одна (атомарная) операция под служебным
    threading.Lock _atomic, а ожидание делается активным опросом флага.
    Полноценные механизмы объектов «блокирующая переменная» — condition variable
    (threading.Condition) и семафор (threading.Semaphore) — показаны в
    конце файла как эквивалент, чтобы ответить на вопрос преподавателя.
"""

import os
import random
import string
import threading
import time

# ==============================================================================
# Структура 1. МЮТЕКС — threading.Lock (используется в Задании 1)
# ==============================================================================
# Где/как:
#   FileShared.mutex создаётся ОДИН раз на весь файл — это общий ресурс
#   («критическая секция» = файл), к которому обращаются оба потока.
#   Вход в секцию — `with self.mutex:`; выход — автоматически на выходе из блока
#   (или в finally). Мьютекс-объект должен быть один на пару потоков, иначе
#   потоки не будут исключать друг друга.
# ==============================================================================
class FileShared:
    CHARS = string.ascii_uppercase + string.digits * 2  # алфавит случайных символов

    def __init__(self, filepath="shared_buffer_var46.txt"):
        self.filepath = filepath
        # <<< МЮТЕКС: защищает доступ к файлу при записи и чтении.
        self.mutex = threading.Lock()
        self.read_pos = self.written = self.reads = self.deleted = 0
        open(self.filepath, "w", encoding="utf-8").close()

    def write_step(self, t, log):
        """Поток P[0]: записать в файл один случайный символ."""
        t.state_str = "Ждёт mutex"
        # <<< ГДЕ: вход в критическую секцию. Если P[1] сейчас внутри
        #     секции, P[0] здесь заблокируется и будет ждать освобождения.
        with self.mutex:
            if t.stopped:
                return
            t.state_str = "КС: запись"
            ch = random.choice(self.CHARS)
            # <<< КАК используется: операция с файлом (общий ресурс)
            #     выполняется строго внутри мьютекса, чтобы две записи
            #     не «перемешались» друг с другом.
            with open(self.filepath, "a", encoding="utf-8") as f:
                f.write(ch)
            self.written += 1
            log(f"P[0]: → '{ch}'")
            time.sleep(0.15)          # искусственная работа в критической секции
        # <<< КОНЕЦ критической секции: мьютекс освобождён автоматически.
        t.state_str = "Работает"

    def read_step(self, t, log):
        """Поток P[1]: прочитать символ и удалить его, если это цифра."""
        t.state_str = "Ждёт mutex"
        # <<< ГДЕ: тот же мьютекс, что у писателя. Внутри секции P[1]
        #     читает файл и может перезаписать его (удаление цифры) —
        #     без мьютекса писатель дописал бы символ между
        #     «прочитал» и «записал» и его символ бы потерялся.
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
                log("P[1]: файл пуст")
            else:
                self.read_pos %= len(content)
                ch = content[self.read_pos]
                self.reads += 1
                if ch.isdigit():
                    # <<< КАК: чтение-изменение-запись файла — цельная операция,
                    #     поэтому она целиком в мьютексе.
                    content = content[: self.read_pos] + content[self.read_pos + 1 :]
                    with open(self.filepath, "w", encoding="utf-8") as f:
                        f.write(content)
                    self.deleted += 1
                    self.read_pos = 0 if self.read_pos >= len(content) else self.read_pos
                    log(f"P[1]: '{ch}' — цифра, удалено")
                else:
                    self.read_pos = (self.read_pos + 1) % len(content)
                    log(f"P[1]: '{ch}' — буква, оставлено")
            time.sleep(0.15)
        t.state_str = "Работает"

    def snapshot(self):
        """Интерфейс тоже читает файл — значит, тоже должен взять мьютекс."""
        # <<< ГДЕ: неблокирующая проверка занятости мьютекса (только для подписи в UI).
        locked = self.mutex.locked()
        with self.mutex:
            content = (
                open(self.filepath, encoding="utf-8").read()
                if os.path.exists(self.filepath)
                else ""
            )
            return {"locked": locked, "content": content, "read_pos": self.read_pos}


# ==============================================================================
# Структура 2. БЛОКИРУЮЩИЕ ПЕРЕМЕННЫЕ (используются в Задании 2)
# ==============================================================================
# Где/как:
#   lock_var   — бинарный «замок» (критическая секция буфера).
#                Где: _acquire / _release — замена мьютекса в стиле
#                учебного кода lock(lv) / unlock(lv).
#   full_lock  — блокирующая переменная: «буфер полон». Производитель
#                не может войти в КС, пока она = 1.
#   empty_lock — блокирующая переменная: «буфер пуст». Потребитель
#                не может войти в КС, пока она = 1.
#   _atomic    — служебный threading.Lock, который делает проверку и
#                установку lock_var одной атомарной операцией (test-and-set).
#                Без него два потока могли бы одновременно увидеть lock_var == 0.
#   _update_flags() — после каждой смены count пересчитывает
#                full_lock/empty_lock, т.е. «включает/выключает» блокировку.
# ==============================================================================
class RingBufferLockVars:
    def __init__(self, size=8):
        self.size = size
        self.buffer = [None] * size
        self.head = self.tail = self.count = 0
        # <<< БЛОКИРУЮЩИЕ ПЕРЕМЕННЫЕ: замок свободен, буфер не полон и пуст.
        self.lock_var = 0
        self.full_lock = 0
        self.empty_lock = 1
        self.produced = self.consumed = self.last_consumed = self.errors = 0
        # <<< Служебный атомарный доступ к lock_var (см. пояснение выше).
        self._atomic = threading.Lock()

    def _acquire(self, t):
        """Взять замок: пока lock_var == 1, ждать (аналог lock(lv))."""
        t.state_str = "Ждёт lock"
        while not t.stopped:
            t._pause.wait()               # пауза потока считается ожиданием
            # <<< ГДЕ используется lock_var: проверка + установка под _atomic
            #     — это неделимая операция «занять критическую секцию».
            with self._atomic:
                if self.lock_var == 0:
                    self.lock_var = 1
                    return True
            time.sleep(0.05)
        return False

    def _release(self, t):
        """Освободить замок: lock_var = 0 (аналог unlock(lv))."""
        # <<< ГДЕ: выход из критической секции — вручную, в finally шага.
        with self._atomic:
            self.lock_var = 0
        t.state_str = "Работает"

    def _update_flags(self):
        """<<< КАК: блокирующие переменные переключаются здесь."""
        self.full_lock = int(self.count == self.size)  # 1 → производитель блокируется
        self.empty_lock = int(self.count == 0)         # 1 → потребитель блокируется

    def produce_step(self, t, log):
        """Производитель: если буфер полон — стоять; иначе записать и сдвинуть head."""
        # <<< ГДЕ: такая блокирующая переменная, как full_lock, удерживает
        #     производителя ВНЕ критической секции, поэтому замок не «залипает».
        while self.full_lock:
            t.state_str = "Блок (full)"
            if not t.wait_tick():
                return
        if not self._acquire(t):
            return
        try:
            # <<< КАК: повторная проверка внутри КС — между циклом и захватом
            #     замка состояние могло измениться.
            if self.count < self.size:
                t.state_str = "КС: пишет"
                self.produced += 1
                idx = self.head
                self.buffer[idx] = self.produced
                self.head = (self.head + 1) % self.size
                self.count += 1
                self._update_flags()      # <<< переключить блокирующие переменные
                log(f"P[0]: → {self.produced} в [{idx}]")
                time.sleep(0.15)
        finally:
            self._release(t)              # <<< замок отпускается всегда

    def consume_step(self, t, log):
        """Потребитель: если буфер пуст — стоять; иначе забрать элемент из tail."""
        # <<< ГДЕ: empty_lock блокирует потребителя, пока в буфере нет данных.
        while self.empty_lock:
            t.state_str = "Блок (empty)"
            if not t.wait_tick():
                return
        if not self._acquire(t):
            return
        try:
            if self.count > 0:            # <<< повторная проверка внутри КС
                t.state_str = "КС: читает"
                idx = self.tail
                item, self.buffer[idx] = self.buffer[idx], None
                self.tail = (self.tail + 1) % self.size
                self.count -= 1
                self._update_flags()      # <<< переключить блокирующие переменные
                exp = self.last_consumed + 1
                if item != exp:
                    self.errors += 1
                    log(f"P[1]: ОШИБКА! взял {item}, ждал {exp}")
                else:
                    log(f"P[1]: ← {item} из [{idx}]")
                if item is not None:
                    self.last_consumed = item
                self.consumed += 1
                time.sleep(0.15)
        finally:
            self._release(t)