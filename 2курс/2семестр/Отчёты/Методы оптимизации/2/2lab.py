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
        print(f"{'-' * 65}")
        for i in range(self.m + 1):
            label = self._var_name(self.basis[i]) if i < self.m else "F"
            print(f"{label:<8}", end="")
            for j in range(self.n_vars + 1):
                print(f"{self.table[i, j]:9.3f}", end="")
            print()
        print(f"{'-' * 65}")
        rhs = self.table[:self.m, -1]
        coefs = self.table[self.m, :self.n_vars]
        feasible = np.all(rhs >= -1e-9)
        optimal = np.all(coefs >= -1e-9) if self.is_max else np.all(coefs <= 1e-9)
        print(f"  Допустимость:  {' все b >= 0' if feasible else f' отрицательные b: {np.round(rhs[rhs < 0], 3)}'}")
        print(f"  Оптимальность: {' оптимум достигнут' if optimal else ''}")
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
            print("\n" + "-" * 65)
            print("  !! Оптимальное решение не единственно.")
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
        print("\n" + "-" * 65)
        print("  ДВОЙСТВЕННЫЙ СИМПЛЕКС-МЕТОД")
        print("-" * 65)
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
                  f"(a = {row_coefs[col]:.3f}, d = {target[col]:.3f}, "
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


# ==================== МЕТОД ВЕТВЕЙ И ГРАНИЦ ====================
class BranchAndBound:
    def __init__(self, c, A, b, integer_vars=None):
        self.c = np.array(c, dtype=float)
        self.A = np.array(A, dtype=float).copy()
        self.b = np.array(b, dtype=float).copy()
        self.integer_vars = integer_vars if integer_vars is not None else list(range(len(c)))
        self.all_solutions = []
        self.best_value = -np.inf
        self.best_solution = None
        self.lp_count = 0
        self.node_count = 0

    def _add_constraints(self, A, b, constraints):
        A_new = A.copy()
        b_new = b.copy()
        for var_idx, op, val in constraints:
            row = np.zeros(A.shape[1])
            row[var_idx] = 1.0
            if op == '<=':
                A_new = np.vstack([A_new, row])
                b_new = np.append(b_new, val)
            elif op == '>=':
                A_new = np.vstack([A_new, -row])
                b_new = np.append(b_new, -val)
        return A_new, b_new

    def _solve_lp(self, A, b):
        self.lp_count += 1
        solver = DualSimplex(self.c, A, b, is_max=True)
        # Подавляем вывод
        import sys
        import io
        old = sys.stdout
        sys.stdout = io.StringIO()
        result = solver.solve()
        sys.stdout = old
        return result

    def _is_integer(self, solution):
        for i in self.integer_vars:
            if abs(solution[i] - round(solution[i])) > 1e-6:
                return False
        return True

    def _find_fractional_var(self, solution):
        for i in self.integer_vars:
            val = solution[i]
            if abs(val - round(val)) > 1e-6:
                return i, val
        return None, None

    def _print_tree(self, node, prefix="", is_last=True):
        if node['infeasible']:
            label = f"Узел {node['id']} [НЕТ РЕШЕНИЙ]"
        elif node['pruned']:
            label = f"Узел {node['id']} [ОТСЕЧЕН, F={node['lp_value']:.2f}]"
        elif node['integer']:
            label = f"Узел {node['id']} [ЦЕЛОЕ, F={node['lp_value']:.2f}] x"
        else:
            label = f"Узел {node['id']} [LP={node['lp_value']:.2f}]"

        print(prefix + ("L-- " if is_last else "|--- ") + label)
        new_prefix = prefix + ("    " if is_last else "|   ")
        for i, child in enumerate(node['children']):
            self._print_tree(child, new_prefix, i == len(node['children']) - 1)

    def solve(self, verbose=True):
        if verbose:
            print("\n" + "-" * 70)
            print("  МЕТОД ВЕТВЕЙ И ГРАНИЦ ")
            print("-" * 70)
            print(f"  Целочисленные переменные: {[f'x{i+1}' for i in self.integer_vars]}")
            print("-" * 70)

        root = {
            'id': 0, 'constraints': [], 'children': [],
            'lp_value': None, 'lp_solution': None,
            'integer': False, 'infeasible': False, 'pruned': False
        }

        queue = [root]

        while queue:
            node = queue.pop(0)
            self.node_count += 1

            if verbose:
                print(f"\n--- УЗЕЛ {node['id']} ---")
                if node['constraints']:
                    print("Дополнительные ограничения:")
                    for var, op, val in node['constraints']:
                        print(f"   x{var+1} {op} {val:.0f}")

            A_node, b_node = self._add_constraints(self.A, self.b, node['constraints'])
            result = self._solve_lp(A_node, b_node)

            if result is None:
                node['infeasible'] = True
                if verbose:
                    print("X! НЕТ ДОПУСТИМЫХ РЕШЕНИЙ")
                continue

            node['lp_value'] = result['value']
            node['lp_solution'] = result['solution']

            if verbose:
                print(f" LP-решение: F = {node['lp_value']:.4f}")
                vars_str = ", ".join([f"x{i+1}={node['lp_solution'][i]:.4f}" for i in range(len(self.c))])
                print(f"   {vars_str}")

            # Отсечение
            if node['lp_value'] <= self.best_value + 1e-9:
                node['pruned'] = True
                if verbose:
                    print(f"️ ОТСЕЧЕНО (лучшее = {self.best_value:.2f})")
                continue

            # Целочисленное решение
            if self._is_integer(node['lp_solution']):
                node['integer'] = True
                self.all_solutions.append({
                    'value': node['lp_value'],
                    'solution': node['lp_solution'].copy(),
                    'node_id': node['id']
                })
                if node['lp_value'] > self.best_value + 1e-9:
                    self.best_value = node['lp_value']
                    self.best_solution = node['lp_solution'].copy()
                    if verbose:
                        print(f" НОВОЕ ЛУЧШЕЕ РЕШЕНИЕ! F = {self.best_value:.4f}")
                continue

            # Ветвление
            var_idx, var_val = self._find_fractional_var(node['lp_solution'])
            if var_idx is None:
                continue

            floor_val = np.floor(var_val)
            ceil_val = np.ceil(var_val)

            if verbose:
                print(f" ВЕТВЛЕНИЕ по x{var_idx+1} = {var_val:.4f}")
                print(f"   Левая ветвь: x{var_idx+1} =< {floor_val:.0f}")
                print(f"   Правая ветвь: x{var_idx+1} >= {ceil_val:.0f}")

            left = {
                'id': self.node_count, 'constraints': node['constraints'] + [(var_idx, '<=', floor_val)],
                'children': [], 'lp_value': None, 'lp_solution': None,
                'integer': False, 'infeasible': False, 'pruned': False
            }
            self.node_count += 1

            right = {
                'id': self.node_count, 'constraints': node['constraints'] + [(var_idx, '>=', ceil_val)],
                'children': [], 'lp_value': None, 'lp_solution': None,
                'integer': False, 'infeasible': False, 'pruned': False
            }
            self.node_count += 1

            node['children'] = [left, right]
            queue.extend([left, right])

        if verbose:
            print("\n" + "-" * 70)
            print("  ДЕРЕВО РЕШЕНИЙ")
            print("-" * 70)
            self._print_tree(root)


            if self.best_solution is None:
                print("\nX! ОПТИМАЛЬНОЕ РЕШЕНИЕ НЕ НАЙДЕНО")
            else:
                print("\n ОПТИМАЛЬНОЕ ЦЕЛОЧИСЛЕННОЕ РЕШЕНИЕ:\n")
                for i in range(len(self.c)):
                    print(f"   x{i+1} = {self.best_solution[i]:.0f}")
                print(f"\n   Максимум F = {self.best_value:.4f}")

        return self.best_solution, self.best_value

def example():

    c = [3, 5]
    A = [[1, 0], [0, 1], [3, 2]]
    b = [4, 6, 18]

    print("Максимизировать: F = 3x_1 + 5x_2")
    print("x_1 =< 4, x_2 =< 6, 3x_1 + 2x_2 =< 18, x_1,x_2 >= 0, целые")

    bb = BranchAndBound(c, A, b, integer_vars=[0, 1])
    bb.solve()

if __name__ == "__main__":
    example()