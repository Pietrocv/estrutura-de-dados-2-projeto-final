LIMIAR_CORTE = 0.20


def _validate_square_matrix(matrix):
    if not isinstance(matrix, list):
        raise TypeError("A matriz deve ser uma lista de listas.")

    size = len(matrix)
    for row in matrix:
        if not isinstance(row, list) or len(row) != size:
            raise ValueError("A matriz deve ser quadrada.")


def _normalize_edge(edge):
    if len(edge) != 3:
        raise ValueError("Cada aresta deve ter o formato (origem, destino, peso).")

    origin, destination, weight = edge
    return int(origin), int(destination), float(weight)


def _empty_graph(size):
    return {vertex: [] for vertex in range(size)}


def _add_edge(graph, origin, destination):
    if destination not in graph[origin]:
        graph[origin].append(destination)
    if origin not in graph[destination]:
        graph[destination].append(origin)


def removed_edges(edges, cut_threshold=LIMIAR_CORTE):
    sorted_edges = sorted((_normalize_edge(edge) for edge in edges), key=lambda item: item[2])
    return [edge for edge in sorted_edges if edge[2] < cut_threshold]


def kept_edges(edges, cut_threshold=LIMIAR_CORTE):
    sorted_edges = sorted((_normalize_edge(edge) for edge in edges), key=lambda item: item[2])
    return [edge for edge in sorted_edges if edge[2] >= cut_threshold]


def _graph_after_cut(edges, vertex_count, cut_threshold):
    graph = _empty_graph(vertex_count)
    for origin, destination, weight in sorted(
        (_normalize_edge(edge) for edge in edges),
        key=lambda item: item[2],
    ):
        if origin < 0 or destination < 0 or origin >= vertex_count or destination >= vertex_count:
            raise ValueError("Aresta possui vertice fora do intervalo da matriz.")

        if weight >= cut_threshold:
            _add_edge(graph, origin, destination)

    return graph


def remove_weak_edges(edges, matrix, cut_threshold=LIMIAR_CORTE):
    _validate_square_matrix(matrix)

    graph = _graph_after_cut(edges, len(matrix), cut_threshold)

    return {
        "final_graph": graph,
        "removed_edges": removed_edges(edges, cut_threshold),
        "kept_edges": kept_edges(edges, cut_threshold),
    }
