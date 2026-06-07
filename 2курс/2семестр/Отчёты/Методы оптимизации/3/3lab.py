import copy

def balance_problem(supply, demand, costs, forced_suppliers=None):
    """Балансирует задачу с возможностью установки штрафа за невывоз"""
    sum_supply = sum(supply)
    sum_demand = sum(demand)

    new_supply = supply.copy()
    new_demand = demand.copy()
    new_costs = copy.deepcopy(costs)

    if sum_supply == sum_demand:
        return new_supply, new_demand, new_costs, False

    m, n = len(supply), len(demand)

    if sum_supply > sum_demand:
        new_demand.append(sum_supply - sum_demand)
        for i in range(m):
            if forced_suppliers and i in forced_suppliers:
                new_costs[i].append(999)
            else:
                new_costs[i].append(0)
    else:
        new_supply.append(sum_demand - sum_supply)
        new_costs.append([0] * n)

    return new_supply, new_demand, new_costs, True

def min_element_method(supply, demand, costs):
    """Метод минимального элемента"""
    m, n = len(supply), len(demand)
    alloc = [[0] * n for _ in range(m)]
    basic_cells = []

    s = supply.copy()
    d = demand.copy()

    active_rows = list(range(m))
    active_cols = list(range(n))

    while active_rows and active_cols:
        if len(active_rows) == 1 and len(active_cols) == 1:
            i, j = active_rows[0], active_cols[0]
            alloc[i][j] = s[i]
            basic_cells.append((i, j))
            break

        min_cost = float('inf')
        i0 = j0 = -1

        for i in active_rows:
            for j in active_cols:
                if costs[i][j] < min_cost:
                    min_cost = costs[i][j]
                    i0, j0 = i, j

        amount = min(s[i0], d[j0])
        alloc[i0][j0] = amount
        basic_cells.append((i0, j0))

        s[i0] -= amount
        d[j0] -= amount

        if s[i0] == 0 and d[j0] == 0:
            if len(active_rows) > 1: active_rows.remove(i0)
            else: active_cols.remove(j0)
        elif s[i0] == 0:
            active_rows.remove(i0)
        else:
            active_cols.remove(j0)

    return alloc, basic_cells

def compute_potentials(costs, basic_cells, m, n):
    """Вычисление потенциалов"""
    u = [None] * m
    v = [None] * n
    u[0] = 0

    while True:
        changed = False
        for i, j in basic_cells:
            if u[i] is not None and v[j] is None:
                v[j] = costs[i][j] - u[i]
                changed = True
            elif v[j] is not None and u[i] is None:
                u[i] = costs[i][j] - v[j]
                changed = True
        if not changed: break

    for i in range(m):
        if u[i] is None: u[i] = 0
    for j in range(n):
        if v[j] is None: v[j] = 0
    return u, v

def compute_deltas(costs, u, v, basic_cells):
    """Вычисление оценок для свободных клеток"""
    m, n = len(costs), len(costs[0])
    delta = [[0] * n for _ in range(m)]
    for i in range(m):
        for j in range(n):
            if (i, j) not in basic_cells:
                delta[i][j] = costs[i][j] - (u[i] + v[j])
    return delta

def find_cycle(basic_cells, start_cell):
    """Поиск цикла пересчёта (очистка тупиков + обход)"""
    cells = basic_cells + [start_cell]

    while True:
        to_remove = [cell for cell in cells if
                     sum(1 for c in cells if c[0] == cell[0]) == 1 or
                     sum(1 for c in cells if c[1] == cell[1]) == 1]
        if not to_remove: break
        for cell in to_remove: cells.remove(cell)

    cycle_ordered = []
    current = start_cell
    cycle_ordered.append((current, '+'))
    cells.remove(current)

    looking_for = 'row'
    while cells:
        for nxt in cells:
            if looking_for == 'row' and nxt[0] == current[0]:
                cycle_ordered.append((nxt, '-'))
                current = nxt
                cells.remove(nxt)
                looking_for = 'col'
                break
            elif looking_for == 'col' and nxt[1] == current[1]:
                cycle_ordered.append((nxt, '+'))
                current = nxt
                cells.remove(nxt)
                looking_for = 'row'
                break
    return cycle_ordered

def print_allocation_table(alloc, costs, supply, demand, basic_cells, orig_demand_len):
    """Выводит таблицу и детализацию стоимости без форматирования"""
    m, n = len(alloc), len(alloc[0])
    is_fake_col = len(demand) > orig_demand_len

    header = "      \t"
    for j in range(n):
        name = f"B{j+1}*" if is_fake_col and j == n-1 else f"B{j+1}"
        header += f"{name}\t"
    print("\n" + header + " | Запасы")

    for i in range(m):
        row_str = f"   A{i+1}\t"
        for j in range(n):
            val = alloc[i][j]
            cost_str = "много" if costs[i][j] >= 999 else str(costs[i][j])

            if (i, j) in basic_cells:
                if val == 0: row_str += f"0*/{cost_str}\t"
                else: row_str += f"{val}/{cost_str}\t"
            else:
                row_str += f"-/{cost_str}\t"
        print(row_str + f"| {supply[i]}")

    demand_row = "Потр. \t"
    for d in demand:
        demand_row += f"{d}\t"
    print(demand_row + "\n")

    total_cost = 0
    print("стоимость каждой перевозки:")

    for i in range(m):
        for j in range(n):
            if alloc[i][j] != 0:
                cost_per_unit = 0 if costs[i][j] >= 999 else costs[i][j]
                transport_cost = alloc[i][j] * cost_per_unit
                total_cost += transport_cost

                to_name = f"B{j+1}*" if is_fake_col and j == n-1 else f"B{j+1}"
                print(f"  A{i+1} → {to_name}: {alloc[i][j]} × {cost_per_unit} = {transport_cost}")

    print(f"  общая стоимость: {total_cost}")
    return total_cost

def solve_transportation(supply, demand, costs, forced_suppliers=None):
    """Основной оркестратор"""
    orig_demand_len = len(demand)
    print("\n=== ИСХОДНЫЕ ДАННЫЕ ===")
    print("Запасы:     ", supply)
    print("Потребности:", demand)

    s, d, c, balanced = balance_problem(supply, demand, costs, forced_suppliers)
    m, n = len(s), len(d)

    print("Матрица стоимостей:")
    for i, row in enumerate(c):
        row_str = []
        for j, val in enumerate(row):
            if val >= 999:
                row_str.append("штр")
            elif val == 0 and balanced and (i == m-1 or j == n-1):
                row_str.append(f"{val}*")
            else:
                row_str.append(str(val))
        print(f"  A{i+1}:  {'   '.join(row_str)}")

    if balanced:
        print("* - фиктивный пункт, штр - штраф за невывоз")

    alloc, basic_cells = min_element_method(s, d, c)
    print("\n=== НАЧАЛЬНЫЙ ПЛАН ===")
    print_allocation_table(alloc, c, s, d, basic_cells, orig_demand_len)

    iteration = 0
    while True:
        iteration += 1
        u, v = compute_potentials(c, basic_cells, m, n)
        delta = compute_deltas(c, u, v, basic_cells)

        min_delta = 0
        in_i, in_j = -1, -1

        for i in range(m):
            for j in range(n):
                if (i, j) not in basic_cells and delta[i][j] < min_delta:
                    min_delta = delta[i][j]
                    in_i, in_j = i, j

        if min_delta >= 0:
            if iteration > 1:
                print(f"\nВсе оценки >= 0. План ОПТИМАЛЕН! (Понадобилось итераций: {iteration-1})")
                print("\n=== ОПТИМАЛЬНЫЙ ПЛАН ===")
                total = print_allocation_table(alloc, c, s, d, basic_cells, orig_demand_len)
            else:
                total = sum(alloc[i][j] * (0 if c[i][j] >= 999 else c[i][j]) for i in range(m) for j in range(n))
            return alloc, total

        print(f" -> Оптимизация {iteration}: вводим A{in_i+1}B{in_j+1} (оценка {min_delta})")
        cycle = find_cycle(basic_cells, (in_i, in_j))

        theta = float('inf')
        exiting_cell = None
        for (i, j), sign in cycle:
            if sign == '-' and alloc[i][j] < theta:
                theta = alloc[i][j]

        for (i, j), sign in cycle:
            if sign == '-' and alloc[i][j] == theta:
                exiting_cell = (i, j)
                break

        for (i, j), sign in cycle:
            if sign == '+': alloc[i][j] += theta
            else: alloc[i][j] -= theta

        basic_cells.remove(exiting_cell)
        basic_cells.append((in_i, in_j))

if __name__ == "__main__":
    supply = [25, 15]
    demand = [10, 20]
    costs = [[1, 2], [3, 4]]
    solve_transportation(supply, demand, costs, forced_suppliers=[1])