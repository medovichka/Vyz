def check_balance(supply, demand):
    sum_supply = sum(supply)
    sum_demand = sum(demand)
    if sum_supply != sum_demand:
        print(f"Ошибка: задача не сбалансирована!")
        print(f"Сумма запасов: {sum_supply}, сумма потребностей: {sum_demand}")
        return False
    return True

def min_element_method(supply, demand, costs):
    m, n = len(supply), len(demand)
    alloc = [[0] * n for _ in range(m)]
    basic_cells = []

    s = supply.copy()
    d = demand.copy()

    active_rows = list(range(m))
    active_cols = list(range(n))

    # Гарантируем ровно (m + n - 1) базисных клеток
    while len(active_rows) > 0 and len(active_cols) > 0:
        if len(active_rows) == 1 and len(active_cols) == 1:
            # Последняя клетка
            i, j = active_rows[0], active_cols[0]
            alloc[i][j] = s[i] # или d[j], они равны
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

        # Правило обработки вырожденности:
        # Вычеркиваем только строку ИЛИ столбец, даже если обнулились оба
        if s[i0] == 0 and d[j0] == 0:
            if len(active_rows) > 1:
                active_rows.remove(i0)
            else:
                active_cols.remove(j0)
        elif s[i0] == 0:
            active_rows.remove(i0)
        else:
            active_cols.remove(j0)

    return alloc, basic_cells

def compute_potentials(costs, basic_cells, m, n):
    u = [None] * m
    v = [None] * n
    u[0] = 0 # Базовый потенциал

    # Итеративное вычисление потенциалов
    while True:
        changed = False
        for i, j in basic_cells:
            if u[i] is not None and v[j] is None:
                v[j] = costs[i][j] - u[i]
                changed = True
            elif v[j] is not None and u[i] is None:
                u[i] = costs[i][j] - v[j]
                changed = True

        if not changed:
            break

    # Если граф несвязный (не должно происходить при правильном базисе)
    for i in range(m):
        if u[i] is None: u[i] = 0
    for j in range(n):
        if v[j] is None: v[j] = 0

    return u, v

def compute_deltas(costs, u, v, basic_cells):
    m, n = len(costs), len(costs[0])
    delta = [[0] * n for _ in range(m)]
    for i in range(m):
        for j in range(n):
            if (i, j) not in basic_cells:
                delta[i][j] = costs[i][j] - (u[i] + v[j])
    return delta

def find_cycle(basic_cells, start_cell):
    # Метод удаления "висячих" вершин. То что останется — и есть цикл.
    cells = basic_cells + [start_cell]

    while True:
        to_remove = []
        for cell in cells:
            row_count = sum(1 for c in cells if c[0] == cell[0])
            col_count = sum(1 for c in cells if c[1] == cell[1])
            # Если у клетки нет пары в строке или столбце, она не в цикле
            if row_count == 1 or col_count == 1:
                to_remove.append(cell)

        if not to_remove:
            break
        for cell in to_remove:
            cells.remove(cell)

    # Упорядочиваем цикл (чередование строк и столбцов)
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

def print_allocation_table(alloc, costs, supply, demand, basic_cells):
    m, n = len(alloc), len(alloc[0])

    print("\n        ", end="")
    for j in range(n):
        print(f"  B{j+1}   ", end="")
    print("  Запасы")

    print("      " + "─" * (7 * n + 2))

    for i in range(m):
        print(f" A{i+1}   │", end="")
        for j in range(n):
            val = alloc[i][j]
            cost = costs[i][j]
            if (i, j) in basic_cells:
                if val == 0:
                    print(f"  0*/{cost:<2d}", end="") # 0* - вырожденная базисная клетка
                else:
                    print(f" {val:3d}/{cost:<2d}", end="")
            else:
                print(f"   -/{cost:<2d}", end="")
        print(f"│ {supply[i]:3d}")

    print("      " + "─" * (7 * n + 2))
    print("Потр.  ", end="")
    for d in demand:
        print(f" {d:5d} ", end="")
    print()

def get_total_cost(alloc, costs):
    total = 0
    m, n = len(alloc), len(alloc[0])
    for i in range(m):
        for j in range(n):
             total += alloc[i][j] * costs[i][j]
    return total

def transportation_problem(supply, demand, costs):
    if not check_balance(supply, demand):
        return None, None

    m, n = len(supply), len(demand)
    print("=== ИСХОДНЫЕ ДАННЫЕ ===")
    print("Запасы:     ", supply)
    print("Потребности:", demand)
    print("Матрица стоимостей:")
    for i, row in enumerate(costs):
        print(f"  A{i+1}: {row}")

    alloc, basic_cells = min_element_method(supply, demand, costs)

    print("\n=== НАЧАЛЬНЫЙ ПЛАН (Метод минимального элемента) ===")
    print(f"Базисных клеток: {len(basic_cells)} (Должно быть {m + n - 1})")
    print_allocation_table(alloc, costs, supply, demand, basic_cells)
    print(f"Стоимость перевозок: {get_total_cost(alloc, costs)}")

    iteration = 0
    max_iterations = 20

    while iteration < max_iterations:
        iteration += 1
        print(f"\n\n\n================ ИТЕРАЦИЯ {iteration} ================\n")

        u, v = compute_potentials(costs, basic_cells, m, n)
        print(f"Потенциалы:\n u = {u}\n v = {v}")

        delta = compute_deltas(costs, u, v, basic_cells)

        min_delta = 0
        in_i = in_j = -1

        # Ищем максимальную по модулю отрицательную оценку
        for i in range(m):
            for j in range(n):
                if (i, j) not in basic_cells and delta[i][j] < min_delta:
                    min_delta = delta[i][j]
                    in_i, in_j = i, j

        if min_delta >= 0:
            print("\nВсе оценки свободных клеток >= 0. План ОПТИМАЛЕН!")
            break

        print(f"Вводим в базис клетку A{in_i+1}B{in_j+1} с оценкой delta = {min_delta}")

        cycle = find_cycle(basic_cells, (in_i, in_j))
        print("Цикл пересчёта: ", " -> ".join([f"A{i+1}B{j+1}({sign})" for (i, j), sign in cycle]))

        # Поиск тета (минимальное значение среди клеток со знаком минус)
        theta = float('inf')
        exiting_cell = None

        for (i, j), sign in cycle:
            if sign == '-':
                if alloc[i][j] < theta:
                    theta = alloc[i][j]

        # Определяем клетку, которая выйдет из базиса
        for (i, j), sign in cycle:
            if sign == '-' and alloc[i][j] == theta:
                exiting_cell = (i, j)
                break # Убираем только ОДНУ клетку, даже если обнулилось несколько

        print(f"Theta = {theta}. Выводим из базиса клетку A{exiting_cell[0]+1}B{exiting_cell[1]+1}")

        # Пересчет объемов
        for (i, j), sign in cycle:
            if sign == '+':
                alloc[i][j] += theta
            else:
                alloc[i][j] -= theta

        # Обновление базиса
        basic_cells.remove(exiting_cell)
        basic_cells.append((in_i, in_j))

        print(f"Новая стоимость перевозок: {get_total_cost(alloc, costs)}")
        print_allocation_table(alloc, costs, supply, demand, basic_cells)

    print("\n=== ОПТИМАЛЬНЫЙ ПЛАН ПЕРЕВОЗОК ===")
    print_allocation_table(alloc, costs, supply, demand, basic_cells)
    total = get_total_cost(alloc, costs)
    print(f"Минимальная общая стоимость перевозок: {total}")

    return alloc, total

if __name__ == "__main__":
    supply = [78, 94, 29, 86]
    demand = [49, 60, 78, 50, 50]

    costs = [
        [9, 5, 7, 10, 18],
        [36, 29, 6, 38, 40],
        [41, 20, 11, 25, 19],
        [30, 28, 13, 39, 50]
    ]
    transportation_problem(supply, demand, costs)