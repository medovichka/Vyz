import numpy as np

class DualSimplex:
    def __init__(self, c, A, b, is_max=True):
        """
        c: коэффициенты целевой функции
        A: матрица ограничений
        b: правые части ограничений
        is_max: максимизация (True) или минимизация (False)
        """
        self.c = np.array(c, dtype=float)
        self.A = np.array(A, dtype=float)
        self.b = np.array(b, dtype=float)
        self.is_max = is_max

        # Приводим к стандартной форме для двойственного метода
        self._prepare_table()
        self.iterations = []

    def _prepare_table(self):
        """Подготовка симплекс-таблицы"""
        m, n = self.A.shape

        # Для двойственного метода нужны ограничения типа ≤
        # Преобразуем ≥ в ≤ умножением на -1
        for i in range(m):
            if self.b[i] < 0:  # Если правая часть отрицательная
                self.A[i] = -self.A[i]
                self.b[i] = -self.b[i]
                # Меняем знак в исходной системе

        # Добавляем базисные переменные (x_{n+1}, ..., x_{n+m})
        self.table = np.zeros((m + 1, n + m + 1))

        # Коэффициенты ограничений
        self.table[:m, :n] = self.A
        # Базисные переменные
        self.table[:m, n:n+m] = np.eye(m)
        # Свободные члены
        self.table[:m, -1] = self.b

        # Целевая функция (последняя строка)
        if self.is_max:
            self.table[m, :n] = -self.c
        else:
            self.table[m, :n] = self.c

        # Последний столбец для целевой функции
        self.table[m, -1] = 0

        # Базисные переменные (индексы)
        self.basis = list(range(n, n + m))
        self.n_vars = n + m
        self.m = m
        self.n = n

    def _print_table(self, iteration):
        """Вывод симплекс-таблицы"""
        print(f"\n{'='*60}")
        print(f"Итерация {iteration}")
        print(f"{'='*60}")

        # Заголовки
        headers = [f"x{i+1}" for i in range(self.n_vars)] + ["Своб. член"]
        print(f"{'Базис':<8}", end="")
        for h in headers:
            print(f"{h:>10}", end="")
        print()

        # Строки таблицы
        for i in range(self.m + 1):
            if i < self.m:
                print(f"x{self.basis[i]+1:<7}", end="")
            else:
                print(f"{'F':<8}", end="")

            for j in range(self.n_vars + 1):
                val = self.table[i, j]
                print(f"{val:10.2f}", end="")
            print()

        # Проверка на допустимость и оптимальность
        rhs = self.table[:self.m, -1]
        if np.all(rhs >= 0):
            print("✓ Решение допустимо")
        else:
            print("✗ Решение недопустимо (есть отрицательные свободные члены)")

        coefs = self.table[self.m, :self.n_vars]
        if self.is_max:
            if np.all(coefs >= 0):
                print("✓ Решение оптимально")
            else:
                print("✗ Решение не оптимально")
        else:
            if np.all(coefs <= 0):
                print("✓ Решение оптимально")
            else:
                print("✗ Решение не оптимально")

    def solve(self):
        """Решение задачи двойственным симплекс-методом"""
        iteration = 0
        self._print_table(iteration)

        while True:
            # Проверяем на допустимость (нет отрицательных свободных членов)
            rhs = self.table[:self.m, -1]
            min_rhs = np.min(rhs)

            # Если все rhs >= 0, решение допустимо
            if min_rhs >= 0:
                # Проверяем на оптимальность
                coefs = self.table[self.m, :self.n_vars]
                if self.is_max:
                    is_optimal = np.all(coefs >= 0)
                else:
                    is_optimal = np.all(coefs <= 0)

                if is_optimal:
                    return self._get_solution()
                else:
                    # Переход к обычному симплекс-методу
                    return self._primal_simplex()

            # Выбираем разрешающую строку (наиболее отрицательный свободный член)
            row = np.argmin(rhs)

            # Проверяем на отсутствие решений
            if np.all(self.table[row, :self.n_vars] >= 0):
                print("\n❌ Решения нет! Система ограничений несовместна.")
                return None

            # Выбираем разрешающий столбец
            # Для двойственного метода: min |coef/negative_elem|
            row_coefs = self.table[row, :self.n_vars]
            target_coefs = self.table[self.m, :self.n_vars]

            ratios = []
            for j in range(self.n_vars):
                if row_coefs[j] < 0:
                    ratio = abs(target_coefs[j] / row_coefs[j])
                    ratios.append((ratio, j))

            if not ratios:
                print("\n❌ Решения нет!")
                return None

            # Выбираем минимальное отношение
            _, col = min(ratios, key=lambda x: x[0])

            print(f"\nВыбрана разрешающая строка: x{self.basis[row]+1} (своб. член = {rhs[row]:.2f})")
            print(f"Выбран разрешающий столбец: x{col+1}")

            # Выполняем пересчет таблицы
            self._pivot(row, col)
            self.basis[row] = col

            iteration += 1
            self._print_table(iteration)

    def _pivot(self, row, col):
        """Пересчет симплекс-таблицы"""
        m, n_vars = self.m, self.n_vars
        pivot_elem = self.table[row, col]

        # Делим разрешающую строку на pivot элемент
        self.table[row, :] /= pivot_elem

        # Пересчитываем остальные строки
        for i in range(m + 1):
            if i != row:
                factor = self.table[i, col]
                self.table[i, :] -= factor * self.table[row, :]

    def _primal_simplex(self):
        """Прямой симплекс-метод (если потребуется)"""
        print("\n→ Переход к прямому симплекс-методу")
        # Здесь можно реализовать прямой симплекс
        return self._get_solution()

    def _get_solution(self):
        """Получение решения из таблицы"""
        solution = np.zeros(self.n)
        for i in range(self.m):
            var_idx = self.basis[i]
            if var_idx < self.n:
                solution[var_idx] = self.table[i, -1]

        optimal_value = self.table[self.m, -1]
        if not self.is_max:
            optimal_value = -optimal_value

        print(f"\n{'='*60}")
        print("РЕШЕНИЕ:")
        print(f"{'='*60}")
        for i in range(self.n):
            print(f"x{i+1} = {solution[i]:.2f}")
        print(f"Оптимальное значение F = {optimal_value:.2f}")

        return {
            'solution': solution,
            'value': optimal_value,
            'table': self.table
        }


def main():
    """Демонстрация работы на примерах"""

    print("\n" + "="*60)
    print("ДВОЙНОЙ СИМПЛЕКС-МЕТОД")
    print("="*60)

    # ПРИМЕР 1: Стандартная задача
    print("\n\n📌 ПРИМЕР 1: Максимизация с ограничениями ≤")
    print("-" * 50)
    # max F = 3x1 + 5x2
    # 2x1 + 3x2 ≤ 12
    # 3x1 + x2 ≤ 9
    # x1, x2 ≥ 0

    c = [3, 5]
    A = [[2, 3],
         [3, 1]]
    b = [12, 9]

    solver = DualSimplex(c, A, b, is_max=True)
    solver.solve()

    # ПРИМЕР 2: Минимизация
    print("\n\n📌 ПРИМЕР 2: Минимизация")
    print("-" * 50)
    # min F = 4x1 + x2
    # 3x1 + x2 ≥ 10
    # x1 + 2x2 ≥ 8
    # x1, x2 ≥ 0

    c = [4, 1]
    A = [[-3, -1],  # Преобразуем ≥ в ≤
         [-1, -2]]
    b = [-10, -8]

    solver = DualSimplex(c, A, b, is_max=False)
    solver.solve()

    # ПРИМЕР 3: Нет решений
    print("\n\n📌 ПРИМЕР 3: Нет решений")
    print("-" * 50)
    # max F = 2x1 + x2
    # x1 - x2 ≤ -2
    # -x1 + x2 ≤ -1
    # x1, x2 ≥ 0

    c = [2, 1]
    A = [[1, -1],
         [-1, 1]]
    b = [-2, -1]

    solver = DualSimplex(c, A, b, is_max=True)
    solver.solve()


if __name__ == "__main__":
    main()