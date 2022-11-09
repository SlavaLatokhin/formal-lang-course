from pyformlang.cfg import CFG


def cyk(s: str, cfg: CFG):
    if not s:
        return cfg.generate_epsilon()
    cfg = cfg.to_normal_form()
    n = len(s)
    m = list(list(set() for _ in range(n)) for _ in range(n))
    t = list()
    nt = list()
    for p in cfg.productions:
        if len(p.body) == 1:
            t.append(p)
        if len(p.body) == 2:
            nt.append(p)
    for i, c in enumerate(s):
        m[i][i] = set(p.head for p in t if p.body[0].value == c)
    for z in range(1, n):
        for y in range(n - z):
            x = z + y
            for i in range(y, x):
                j = i + 1
                for p in nt:
                    if p.body[0] in m[y][i] and p.body[1] in m[j][x]:
                        m[y][x].add(p.head)
    return cfg.start_symbol in m[0][n - 1]
