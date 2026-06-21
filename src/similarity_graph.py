def jaccard(a, b):
    if len(a) == 0 and len(b) == 0:
        return 0

    intersecao = 0
    for item in a:
        if item in b:
            intersecao += 1

    uniao = len(a) + len(b) - intersecao

    return intersecao / uniao
