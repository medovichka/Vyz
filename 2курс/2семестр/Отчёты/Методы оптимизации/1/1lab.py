import numpy as np
import numpy as np

class DualSimplex:
    def __init__(self, c, A, b, is_max=True):
        self.c = np.array(c, dtype=float)
        self.A = np.array(A, dtype=float).copy()
        self.b = np.array(b, dtype=float).copy()
        self.is_max = is_max
        self._prepare_table()

    def _prepare_table(self):
        m, n = self.A.shape
        self.table = np.zeros((m + 1, n + m + 1))
        self.table[:m, :n] = self.A
        self.table[:m, n:n + m] = np.eye(m)
        self.table[:m, -1] = self.b
        self.table[m, :n] = -self.c if self.is_max else self.c
        self.basis = list(range(n, n + m))
        self.n_vars = n + m
        self.m = m
        self.n = n

    def _var_name(self, idx):
        return f"x{idx + 1}"

    def _print_table(self, iteration):
        header = "Начальная таблица" if iteration == 0 else f"Таблица после итерации {iteration}"
        print(f"  {header}")
        col_names = [self._var_name(i) for i in range(self.n_vars)] + ["b"]
        print(f"{'Базис':<8}", end="")
        for h in col_names:
            print(f"{h:>9}", end="")
        print()
        print(f"{'─' * 65}")
        for i in range(self.m + 1):
            label = self._var_name(self.basis[i]) if i < self.m else "F"
            print(f"{label:<8}", end="")
            for j in range(self.n_vars + 1):
                print(f"{self.table[i, j]:9.3f}", end="")
            print()
        print(f"{'─' * 65}")
        rhs = self.table[:self.m, -1]
        coefs = self.table[self.m, :self.n_vars]
        feasible = np.all(rhs >= -1e-9)
        optimal = np.all(coefs >= -1e-9) if self.is_max else np.all(coefs <= 1e-9)
        print(f"  Допустимость:  {'✓ все b ≥ 0' if feasible else f'✗ отрицательные b: {np.round(rhs[rhs < 0], 3)}'}")
        print(f"  Оптимальность: {'✓ оптимум достигнут' if optimal else '✗'}")
        solution = np.zeros(self.n)
        for i in range(self.m):
            idx = self.basis[i]
            if idx < self.n:
                solution[idx] = self.table[i, -1]
        f_val = self.table[self.m, -1]
        vals = ",  ".join(f"{self._var_name(i)} = {solution[i]:.4f}" for i in range(self.n))
        print(f"  Текущее решение: {vals},  F = {f_val:.4f}")

    def _pivot(self, row, col):
        pivot = self.table[row, col]
        if abs(pivot) < 1e-12:
            raise ValueError(f"Разрешающий элемент слишком мал: {pivot}")
        self.table[row, :] /= pivot
        for i in range(self.m + 1):
            if i != row:
                self.table[i, :] -= self.table[i, col] * self.table[row, :]

    def _check_alternative_optima(self):
        zero_tolerance = 1e-9
        has_alternative = False
        alternative_vars = []
        for j in range(self.n_vars):
            if j not in self.basis:
                coef = self.table[self.m, j]
                if abs(coef) < zero_tolerance:
                    col_vals = self.table[:self.m, j]
                    if np.any(col_vals > zero_tolerance):
                        has_alternative = True
                        alternative_vars.append(self._var_name(j))
        if has_alternative:
            print("\n" + "=" * 65)
            print("  ⚠️ Оптимальное решение не единственно.")
            print(f"  Небазисные переменные с нулевой оценкой: {', '.join(alternative_vars)}")
        return has_alternative

    def _extract_solution(self):
        solution = np.zeros(self.n)
        for i in range(self.m):
            idx = self.basis[i]
            if idx < self.n:
                solution[idx] = self.table[i, -1]
        value = self.table[self.m, -1]
        if not self.is_max:
            value = -value
        print(f"\n{'=' * 65}")
        print("  ОПТИМАЛЬНОЕ РЕШЕНИЕ")
        print(f"{'=' * 65}")
        for i in range(self.n):
            print(f"  {self._var_name(i)} = {solution[i]:.4f}")
        print(f"\n  F = {value:.4f}")
        print(f"{'=' * 65}")
        self._check_alternative_optima()
        return {"solution": solution, "value": value}

    def solve(self):
        print("\n" + "=" * 65)
        print("  ДВОЙСТВЕННЫЙ СИМПЛЕКС-МЕТОД")
        print("=" * 65)
        print(f"  Задача: {'максимизация' if self.is_max else 'минимизация'} F")
        print(f"  Переменных: {self.n}, ограничений: {self.m}")
        iteration = 0
        self._print_table(iteration)
        while True:
            rhs = self.table[:self.m, -1]
            if np.all(rhs >= -1e-9):
                coefs = self.table[self.m, :self.n_vars]
                optimal = np.all(coefs >= -1e-9) if self.is_max else np.all(coefs <= 1e-9)
                if optimal:
                    print("\n  Решение оптимально. Метод завершён.")
                    return self._extract_solution()
                else:
                    print("\n  Двойственная фаза завершена — решение допустимо.")
                    print("  Переход к прямому симплекс-методу для достижения оптимума.\n")
                    return self._primal_simplex(iteration)
            row = int(np.argmin(rhs))
            iteration += 1
            print(f"\n  Шаг {iteration}: выводим {self._var_name(self.basis[row])} "
                  f"(b = {rhs[row]:.3f}) — наиболее отрицательное b")
            row_coefs = self.table[row, :self.n_vars]
            if np.all(row_coefs >= -1e-9):
                print("\n  Задача не имеет решений: система ограничений несовместна.")
                return None
            target = self.table[self.m, :self.n_vars]
            ratios = []
            for j in range(self.n_vars):
                if row_coefs[j] < -1e-9:
                    ratios.append((abs(target[j] / row_coefs[j]), j))
            _, col = min(ratios, key=lambda x: x[0])
            print(f"  Вводим {self._var_name(col)} "
                  f"(a = {row_coefs[col]:.3f}, Δ = {target[col]:.3f}, "
                  f"отношение = {abs(target[col] / row_coefs[col]):.4f})")
            self._pivot(row, col)
            self.basis[row] = col
            self._print_table(iteration)

    def _primal_simplex(self, start_iteration):
        iteration = start_iteration
        while True:
            coefs = self.table[self.m, :self.n_vars]
            if self.is_max:
                if np.all(coefs >= -1e-9):
                    print("\n  Оптимум достигнут.")
                    return self._extract_solution()
                col = int(np.argmin(coefs))
            else:
                if np.all(coefs <= 1e-9):
                    return self._extract_solution()
                col = int(np.argmax(coefs))
            col_vals = self.table[:self.m, col]
            if np.all(col_vals <= 1e-9):
                print("\n  Целевая функция не ограничена — задача не имеет конечного оптимума.")
                return None
            ratios = []
            for i in range(self.m):
                if col_vals[i] > 1e-9:
                    ratios.append((self.table[i, -1] / col_vals[i], i))
            _, row = min(ratios, key=lambda x: x[0])
            iteration += 1
            print(f"  Шаг {iteration} (прямой): вводим {self._var_name(col)}, "
                  f"выводим {self._var_name(self.basis[row])}")
            self._pivot(row, col)
            self.basis[row] = col
            self._print_table(iteration)



c = [2, 3]  # F = x + 3y

A = [
    [2, 3],  # -2x -3y ≤ -6
    [-1, -1],   # x + y ≥ 1 → -x - y ≤ -1
    [-1,  2],   # -x + 2y ≤ 2
]

b = [6, -1, 2]

solver = DualSimplex(c, A, b, is_max=True)
result = solver.solve()