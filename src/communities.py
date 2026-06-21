from collections import deque


LIMIAR_CORTE = 0.20
LIMIAR_ANEXACAO = 0.20


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


def _validate_graph(graph):
    if not isinstance(graph, dict):
        raise TypeError("O grafo deve ser um dicionario de listas de adjacencia.")

    for vertex, neighbors in graph.items():
        if not isinstance(vertex, int) or not isinstance(neighbors, list):
            raise TypeError("O grafo deve ter vertices inteiros e listas de vizinhos.")


def dfs_components(graph):
    _validate_graph(graph)

    visited = set()
    communities = []

    for vertex in graph:
        if vertex in visited:
            continue

        component = []
        stack = [vertex]
        visited.add(vertex)

        while stack:
            current = stack.pop()
            component.append(current)

            for neighbor in graph[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    stack.append(neighbor)

        communities.append(sorted(component))

    return communities


def bfs_components(graph):
    _validate_graph(graph)

    visited = set()
    communities = []

    for vertex in graph:
        if vertex in visited:
            continue

        component = []
        queue = deque([vertex])
        visited.add(vertex)

        while queue:
            current = queue.popleft()
            component.append(current)

            for neighbor in graph[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        communities.append(sorted(component))

    return communities


def _best_community_for_vertex(vertex, communities, matrix):
    best_community = None
    best_vertex = None
    best_weight = 0.0

    for community in communities:
        for candidate in community:
            weight = float(matrix[vertex][candidate])
            if weight > best_weight:
                best_weight = weight
                best_community = community
                best_vertex = candidate

    return best_community, best_vertex, best_weight


def _handle_single_vertex_communities(communities, matrix, graph, attach_threshold):
    working_communities = [list(community) for community in communities]
    single_vertices = [community[0] for community in communities if len(community) == 1]
    outliers = []

    for vertex in single_vertices:
        current_community = next(
            (
                community
                for community in working_communities
                if len(community) == 1 and community[0] == vertex
            ),
            None,
        )

        if current_community is None:
            continue

        candidate_communities = [
            community for community in working_communities if community is not current_community
        ]

        if not candidate_communities:
            outliers.append(vertex)
            working_communities.remove(current_community)
            continue

        best_community, best_vertex, best_weight = _best_community_for_vertex(
            vertex,
            candidate_communities,
            matrix,
        )

        if best_weight >= attach_threshold:
            best_community.append(vertex)
            _add_edge(graph, vertex, best_vertex)
            working_communities.remove(current_community)
        else:
            outliers.append(vertex)
            working_communities.remove(current_community)

    final_communities = [sorted(community) for community in working_communities]
    final_communities.sort(key=lambda community: (community[0], len(community)))
    outliers.sort()

    return final_communities, outliers


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


def remove_weak_edges(
    edges,
    matrix,
    cut_threshold=LIMIAR_CORTE,
    attach_threshold=LIMIAR_ANEXACAO,
):
    _validate_square_matrix(matrix)

    graph = _graph_after_cut(edges, len(matrix), cut_threshold)
    initial_communities = dfs_components(graph)
    communities, outliers = _handle_single_vertex_communities(
        initial_communities,
        matrix,
        graph,
        attach_threshold,
    )

    return graph, communities, outliers


def detect_communities(
    mst_edges,
    matrix,
    cut_threshold=LIMIAR_CORTE,
    attach_threshold=LIMIAR_ANEXACAO,
):
    graph, communities, outliers = remove_weak_edges(
        mst_edges,
        matrix,
        cut_threshold,
        attach_threshold,
    )

    return {
        "communities": communities,
        "outliers": outliers,
        "final_graph": graph,
        "removed_edges": removed_edges(mst_edges, cut_threshold),
        "kept_edges": kept_edges(mst_edges, cut_threshold),
        "components_before_singleton_handling": dfs_components(
            _graph_after_cut(mst_edges, len(matrix), cut_threshold)
        ),
    }
