def prim_maximum_spanning_tree(
    matrix: list[list[float]],
) -> list[tuple[int, int, float]]:
    if not matrix or len(matrix) == 0:
        raise ValueError("A matriz de adjacência não pode ser vazia.")

    n = len(matrix) 

    for i, row in enumerate(matrix):
        if len(row) != n:
            raise ValueError(
                f"A matriz não é quadrada: a linha {i} tem {len(row)} "
                f"elementos, mas esperava {n}."
            )

    if n == 1:
        return []

    in_mst: list[bool] = [False] * n
    key: list[float] = [-float("inf")] * n
    parent: list[int] = [-1] * n

    key[0] = 0

    for _ in range(n):
        u = -1 

        for v in range(n):
            if in_mst[v]:
                continue

            if u == -1 or key[v] > key[u]:
                u = v

        in_mst[u] = True

        for v in range(n):
            weight = matrix[u][v]

            if not in_mst[v] and weight > 0 and weight > key[v]:
                key[v] = weight    
                parent[v] = u      

    mst_edges: list[tuple[int, int, float]] = []

    for v in range(1, n):
        u = parent[v] 

        if u == -1:
            print(
                f"[prim_max] Aviso: vértice {v} ficou isolado "
                f"(sem conexão com peso > 0). Será tratado como outlier."
            )
            continue

        weight = matrix[u][v]
        mst_edges.append((u, v, weight))

    return mst_edges