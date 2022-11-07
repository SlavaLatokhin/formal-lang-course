from pyformlang.cfg import CFG, Variable


def to_weakened_normal_form(cfg: CFG):
    cfg = (
        cfg.remove_useless_symbols()
        .eliminate_unit_productions()
        .remove_useless_symbols()
    )
    new_productions = cfg._get_productions_with_only_single_terminals()
    new_productions = cfg._decompose_productions(new_productions)
    cfg = CFG(start_symbol=cfg.start_symbol, productions=set(new_productions))
    return cfg


def cfg_from_file(file, start_symbol=Variable("S")):
    return CFG.from_text(open(file).read(), start_symbol)
