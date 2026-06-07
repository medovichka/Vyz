def knapsack_unbounded(weights, values, capacity):

    n = len(weights)
    dp = [0] * (capacity + 1)
    choice = [-1] * (capacity + 1)

    for cap in range(1, capacity + 1):
        best_val = dp[cap]
        best_idx = -1
        for i in range(n):
            w = weights[i]
            if w <= cap:
                cand = dp[cap - w] + values[i]
                if cand > best_val:
                    best_val = cand
                    best_idx = i
        dp[cap] = best_val
        choice[cap] = best_idx

    taken = []
    cap = capacity
    while cap > 0 and choice[cap] != -1:
        i = choice[cap]
        taken.append(i)
        cap -= weights[i]

    return dp[capacity], taken


def print_knapsack_table(weights, values, capacity):
    """Выводит таблицу DP для наглядности (как в транспортной задаче)."""
    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    print(" № : вес : стоимость")
    for i, (w, v) in enumerate(zip(weights, values)):
        print(f"{i+1:2} :  {w:2}  :   {v:2}")
    print(f"Вместимость рюкзака: {capacity}\n")

    dp_unbounded = [0] * (capacity + 1)
    choices = [-1] * (capacity + 1)

    for cap in range(1, capacity + 1):
        best_val = 0
        best_i = -1
        for i in range(n):
            if weights[i] <= cap:
                cand = dp_unbounded[cap - weights[i]] + values[i]
                if cand > best_val:
                    best_val = cand
                    best_i = i
        dp_unbounded[cap] = best_val
        choices[cap] = best_i

    print(" виестимость | стоимость")
    for cap in range(capacity + 1):
        print(f"{cap:4} | {dp_unbounded[cap]:5}")

    taken = []
    cap = capacity
    while cap > 0 and choices[cap] != -1:
        i = choices[cap]
        taken.append(i)
        cap -= weights[i]

    print("\nВзятые предметы:", [i + 1 for i in taken])
    print("Общая стоимость:", dp_unbounded[capacity])
    print("Общий вес:", sum(weights[i] for i in taken))


def main_knapsack():
    weights = [1, 2, 7, 4]
    values  = [2, 5, 7, 9]
    capacity = 4

    print_knapsack_table(weights, values, capacity)

if __name__ == "__main__":
    main_knapsack()