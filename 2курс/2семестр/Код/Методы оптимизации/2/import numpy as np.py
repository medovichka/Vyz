import numpy as np
from collections import deque
import heapq


class DualSimplex:
    def __init__(self, c, A, b, is_max=True, verbose=False):
        self.c = np.array(c, dtype=float)
        self.A = np.array(A, dtype=float).copy()
        self.b = np.array(b, dtype=float).copy()
        self.is_max = is_max
        self.verbose = verbose
        self._prepare_table()

    def _prepare_table(self):
        m, n = self.A.shape
        self.table = np.zeros((m + 1, n + m + 1))
        self.table[:m, :n] = self.A
        self.table[:m, n : n + m] = np.eye(m)
        self.table[:m, -1] = self.b
        self.table[m, :n] = -self.c if self.is_max else self.c
        self.basis = list(range(n, n + m))
        self.n_vars = n + m
        self.m = m
        self.n = n

    def _var_name(self, idx):
        return f"x{idx + 1}"

    def _print_table(self, iteration):
        if not self.verbose:
            return
        header = "Initial" if iteration == 0 else f"Iteration {iteration}"
        print(f"  {header}")
        col_names = [self._var_name(i) for i in range(self.n_vars)] + ["b"]
        print(f"{'Basis':<8}", end="")
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
        rhs = self.table[: self.m, -1]
        coefs = self.table[self.m, : self.n_vars]
        feasible = np.all(rhs >= -1e-9)
        optimal = np.all(coefs >= -1e-9) if self.is_max else np.all(coefs <= 1e-9)
        print(f"  Feasible: {feasible}, Optimal: {optimal}")
        solution = np.zeros(self.n)
        for i in range(self.m):
            idx = self.basis[i]
            if idx < self.n:
                solution[idx] = self.table[i, -1]
        f_val = self.table[self.m, -1]
        vals = ",  ".join(
            f"{self._var_name(i)} = {solution[i]:.4f}" for i in range(self.n)
        )
        print(f"  Current solution: {vals}, F = {f_val:.4f}")

    def _pivot(self, row, col):
        pivot = self.table[row, col]
        if abs(pivot) < 1e-12:
            raise ValueError(f"Pivot too small: {pivot}")
        self.table[row, :] /= pivot
        for i in range(self.m + 1):
            if i != row:
                self.table[i, :] -= self.table[i, col] * self.table[row, :]

    def _extract_solution_info(self):
        solution = np.zeros(self.n)
        for i in range(self.m):
            idx = self.basis[i]
            if idx < self.n:
                solution[idx] = self.table[i, -1]
        value = self.table[self.m, -1]
        if not self.is_max:
            value = -value

        alt = False
        zero_tol = 1e-9
        for j in range(self.n_vars):
            if j not in self.basis:
                coef = self.table[self.m, j]
                if abs(coef) < zero_tol:
                    col_vals = self.table[: self.m, j]
                    if np.any(col_vals > zero_tol):
                        alt = True
                        break
        return {"solution": solution, "value": value, "alternative_optima": alt}

    def _check_unbounded(self, col):
        col_vals = self.table[: self.m, col]
        return np.all(col_vals <= 1e-9)

    def solve(self):
        if self.verbose:
            print("\n" + "=" * 65)
            print("  DUAL SIMPLEX METHOD")
            print("=" * 65)
            print(f" Problem: {'maximization' if self.is_max else 'minimization'}")
            print(f" Variables: {self.n}, constraints: {self.m}")
        iteration = 0
        self._print_table(iteration)

        while True:
            rhs = self.table[: self.m, -1]
            if np.all(rhs >= -1e-9):
                break

            row = int(np.argmin(rhs))
            iteration += 1
            if self.verbose:
                print(
                    f"\n Dual iteration {iteration}: leaving {self._var_name(self.basis[row])} (b = {rhs[row]:.3f})"
                )
            row_coefs = self.table[row, : self.n_vars]
            if np.all(row_coefs >= -1e-9):
                if self.verbose:
                    print("\n Infeasible problem: no solution.")
                return None
            target = self.table[self.m, : self.n_vars]
            ratios = []
            for j in range(self.n_vars):
                if row_coefs[j] < -1e-9:
                    ratios.append((abs(target[j] / row_coefs[j]), j))
            _, col = min(ratios, key=lambda x: x[0])
            if self.verbose:
                print(
                    f" Entering {self._var_name(col)} (ratio = {abs(target[col]/row_coefs[col]):.4f})"
                )
            self._pivot(row, col)
            self.basis[row] = col
            self._print_table(iteration)

        while True:
            coefs = self.table[self.m, : self.n_vars]
            if self.is_max:
                if np.all(coefs >= -1e-9):
                    if self.verbose:
                        print("\n Optimal solution reached.")
                    return self._extract_solution_info()
                col = int(np.argmin(coefs))
            else:
                if np.all(coefs <= 1e-9):
                    return self._extract_solution_info()
                col = int(np.argmax(coefs))

            if self._check_unbounded(col):
                if self.verbose:
                    print(
                        "\n Unbounded problem: objective can be increased indefinitely."
                    )
                return None

            ratios = []
            for i in range(self.m):
                if self.table[i, col] > 1e-9:
                    ratios.append((self.table[i, -1] / self.table[i, col], i))
            _, row = min(ratios, key=lambda x: x[0])
            iteration += 1
            if self.verbose:
                print(
                    f" Primal iteration {iteration}: entering {self._var_name(col)}, leaving {self._var_name(self.basis[row])}"
                )
            self._pivot(row, col)
            self.basis[row] = col
            self._print_table(iteration)


class BranchAndBound:
    def __init__(
        self,
        c,
        A,
        b,
        is_max=True,
        integer_vars=None,
        branching_strategy="first",
        search_strategy="DFS",
        verbose=True,
    ):
        self.c = np.array(c, dtype=float)
        self.A = np.array(A, dtype=float).copy()
        self.b = np.array(b, dtype=float).copy()
        self.is_max = is_max
        self.integer_vars = (
            integer_vars if integer_vars is not None else list(range(len(c)))
        )
        self.branching_strategy = branching_strategy
        self.search_strategy = search_strategy
        self.verbose = verbose

        self.best_value = -np.inf if is_max else np.inf
        self.best_solution = None
        self.best_is_alternative = False
        self.nodes = []
        self.node_counter = 0
        self.iteration_counter = 0

    class Node:
        def __init__(self, parent_id, constraints, depth):
            self.id = None
            self.parent_id = parent_id
            self.constraints = constraints
            self.depth = depth
            self.lp_value = None
            self.lp_solution = None
            self.is_integer = False
            self.is_infeasible = False
            self.is_pruned = False
            self.children = []

    def _build_LP(self, constraints):
        A_new = self.A.copy()
        b_new = self.b.copy()
        for var_idx, bound_type, bound_val in constraints:
            row = np.zeros(self.A.shape[1])
            row[var_idx] = 1.0
            if bound_type == "le":

                A_new = np.vstack([A_new, row])
                b_new = np.append(b_new, bound_val)
            elif bound_type == "ge":

                A_new = np.vstack([A_new, -row])
                b_new = np.append(b_new, -bound_val)
        return A_new, b_new

    def _solve_LP(self, constraints):
        A_new, b_new = self._build_LP(constraints)
        solver = DualSimplex(self.c, A_new, b_new, is_max=self.is_max, verbose=False)
        result = solver.solve()
        if result is None:

            return None, "infeasible"
        return result, "ok"

    def _pick_branching_variable(self, sol):
        fracs = []
        for j in self.integer_vars:
            val = sol[j]
            if abs(val - round(val)) > 1e-7:
                frac = val - np.floor(val)
                fracs.append((j, frac))
        if not fracs:
            return None
        if self.branching_strategy == "first":
            return fracs[0][0]
        elif self.branching_strategy == "most_fractional":

            return max(fracs, key=lambda x: min(x[1], 1 - x[1]))[0]
        else:
            return fracs[0][0]

    def _is_integer_solution(self, sol):
        for j in self.integer_vars:
            if abs(sol[j] - round(sol[j])) > 1e-6:
                return False
        return True

    def _update_best(self, sol, value):
        if self.is_max:
            if value > self.best_value + 1e-9:
                self.best_value = value
                self.best_solution = sol.copy()
                self.best_is_alternative = False
            elif abs(value - self.best_value) < 1e-8:

                self.best_is_alternative = True
        else:
            if value < self.best_value - 1e-9:
                self.best_value = value
                self.best_solution = sol.copy()
                self.best_is_alternative = False
            elif abs(value - self.best_value) < 1e-8:
                self.best_is_alternative = True

    def _prune_by_bound(self, node_lp_value):
        if self.is_max:
            return node_lp_value <= self.best_value + 1e-9
        else:
            return node_lp_value >= self.best_value - 1e-9

    def solve(self):
        if self.verbose:
            print(f"  Problem: {'maximization' if self.is_max else 'minimization'}")
            print(f"  Integer variables: {[f'x{i+1}' for i in self.integer_vars]}")
            print(f"  Branching strategy: {self.branching_strategy}")
            print(f"  Search strategy: {self.search_strategy}")
            print("-" * 70)

        root = self.Node(parent_id=None, constraints=[], depth=0)
        root.id = self.node_counter
        self.node_counter += 1

        if self.search_strategy == "best":

            heap = []
            heapq.heappush(heap, (0, root))
        else:
            queue = [root]

        nodes_explored = 0

        while True:
            if self.search_strategy == "best":
                if not heap:
                    break

                pass

            if self.search_strategy == "DFS":
                if not queue:
                    break
                current = queue.pop()
            elif self.search_strategy == "BFS":
                if not queue:
                    break
                current = queue.pop(0)
            else:

                current = queue.pop() if queue else None
                if not queue:
                    break

            nodes_explored += 1

            self.iteration_counter += 1
            sol_dict, status = self._solve_LP(current.constraints)

            if status == "infeasible":
                current.is_infeasible = True
                if self.verbose:
                    print(f" Node {current.id}: INFEASIBLE")
                continue

            current.lp_value = sol_dict["value"]
            current.lp_solution = sol_dict["solution"]

            if self._prune_by_bound(current.lp_value):
                current.is_pruned = True
                if self.verbose:
                    print(
                        f" Node {current.id}: pruned by bound (LP = {current.lp_value:.4f}, best = {self.best_value:.4f})"
                    )
                continue

            if self._is_integer_solution(current.lp_solution):
                current.is_integer = True
                self._update_best(current.lp_solution, current.lp_value)
                if self.verbose:
                    print(
                        f" Node {current.id}: INTEGER feasible solution: value = {current.lp_value:.4f}"
                    )
                    print(
                        f"            x = {[round(current.lp_solution[i],4) for i in self.integer_vars]}"
                    )
                continue

            branch_var = self._pick_branching_variable(current.lp_solution)
            if branch_var is None:
                continue

            frac_val = current.lp_solution[branch_var]
            floor_val = np.floor(frac_val)
            ceil_val = np.ceil(frac_val)

            if self.verbose:
                print(
                    f" Node {current.id}: branching on x{branch_var+1} = {frac_val:.4f}"
                )

            left_const = current.constraints + [(branch_var, "le", floor_val)]
            left_child = self.Node(
                parent_id=current.id, constraints=left_const, depth=current.depth + 1
            )
            left_child.id = self.node_counter
            self.node_counter += 1

            right_const = current.constraints + [(branch_var, "ge", ceil_val)]
            right_child = self.Node(
                parent_id=current.id, constraints=right_const, depth=current.depth + 1
            )
            right_child.id = self.node_counter
            self.node_counter += 1

            current.children = [left_child, right_child]

            if self.search_strategy == "DFS":
                queue.extend([right_child, left_child])
            elif self.search_strategy == "BFS":
                queue.extend([left_child, right_child])
            else:
                queue.extend([left_child, right_child])

        self._print_tree(root)
        self._print_final_result()

        return self.best_solution, self.best_value, self.best_is_alternative

    def _print_tree(self, root, prefix="", is_last=True):
        """Recursive tree printing."""
        if root is None:
            return

        node_label = f"Node {root.id}"
        if root.is_infeasible:
            node_label += " [INFEAS]"
        elif root.is_pruned:
            node_label += f" [PRUNED, LP={root.lp_value:.2f}]"
        elif root.is_integer:
            node_label += f" [INT, value={root.lp_value:.4f}]"
        else:
            node_label += f" [LP={root.lp_value:.4f}]"
        if self.verbose:
            print(prefix + ("└── " if is_last else "├── ") + node_label)

        new_prefix = prefix + ("    " if is_last else "│   ")
        for i, child in enumerate(root.children):
            self._print_tree(child, new_prefix, i == len(root.children) - 1)

    def _print_final_result(self):
        if self.best_solution is None:
            print("\n" + "=" * 70)
            print("  RESULT: No integer feasible solution found.")
            print("=" * 70)
        else:
            print("\n" + "=" * 70)
            print("  OPTIMAL INTEGER SOLUTION")
            print("=" * 70)
            for i in self.integer_vars:
                print(f"  x{i+1} = {self.best_solution[i]:.4f}")
            print(f"\n  Objective F = {self.best_value:.4f}")
            if self.best_is_alternative:
                print("  (Alternative optimal solutions exist)")
            print(f"  Total LP subproblems solved: {self.iteration_counter}")
            print("=" * 70)


def example():
    """
    Универсальная функция для быстрого тестирования.
    Просто меняйте значения ниже под задачу преподавателя.
    """

    # ==================== ВВЕДИТЕ ДАННЫЕ ЗДЕСЬ ====================

    # Коэффициенты целевой функции (F = 3x₁ + 5x₂)
    c = [3, 5]

    # Матрица ограничений (каждая строка = одно ограничение)
    A = [
        [1, 2],   # 1x₁ + 2x₂ ≤ 10
        [2, 1]    # 2x₁ + 1x₂ ≤ 12
    ]

    # Правые части ограничений (соответствуют строкам A)
    b = [10, 12]

    # Тип задачи: True = максимизация, False = минимизация
    is_max = True

    # Какие переменные должны быть целыми (0 = x₁, 1 = x₂, 2 = x₃ и т.д.)
    # None = все переменные целые
    integer_vars = [0, 1]

    # Стратегия ветвления: 'first' или 'most_fractional'
    branching_strategy = 'most_fractional'

    # Стратегия обхода: 'DFS' или 'BFS'
    search_strategy = 'DFS'

    # Показывать подробности: True или False
    verbose = True

    # ==================== КОД ЗАПУСКА (НЕ ТРОГАТЬ) ====================

    print("\n" + "="*70)
    print("  РЕШЕНИЕ ЗАДАЧИ ЦЕЛОЧИСЛЕННОГО ПРОГРАММИРОВАНИЯ")
    print("="*70)
    print("\n📊 Исходные данные:")
    print(f"   Целевая функция: {'max' if is_max else 'min'} F = ", end="")
    for i, coeff in enumerate(c):
        print(f"{coeff:+}x{i+1} ", end="")
    print()
    print(f"\n   Ограничения:")
    for i, row in enumerate(A):
        print(f"      ", end="")
        for j, coeff in enumerate(row):
            print(f"{coeff:+}x{j+1} ", end="")
        print(f"≤ {b[i]}")
    print(f"\n   Целочисленные переменные: x{', x'.join([str(v+1) for v in (integer_vars if integer_vars else range(len(c)))])}")
    print(f"   Стратегия ветвления: {branching_strategy}")
    print(f"   Стратегия обхода: {search_strategy}")
    print("-"*70)

    # Запуск метода ветвей и границ
    bb = BranchAndBound(
        c=c,
        A=A,
        b=b,
        is_max=is_max,
        integer_vars=integer_vars,
        branching_strategy=branching_strategy,
        search_strategy=search_strategy,
        verbose=verbose
    )

    result = bb.solve()

    if result:
        solution, value, has_alternative = result
        print("\n✅ ГОТОВО! Можно показывать преподавателю.")

    return bb


# Вызов функции - меняйте данные только внутри example()
if __name__ == "__main__":
    example()