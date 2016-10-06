

def make_params(mapping, _locals):
    return {
        dest: _locals[src]
        for src, dest in mapping.items() if _locals[src] is not None
    }
