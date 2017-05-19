from functools import partial
from collections import Iterator

from unification import Var, isvar
from unification.dispatch import dispatch

@dispatch(Iterator, str)
def _rename_variables(t, prefix):
    return map(partial(rename_variables, prefix=prefix), t)
    # return (rename_variables(arg, s) for arg in t)

@dispatch(tuple, str)
def _rename_variables(t, prefix):
    return tuple(rename_variables(iter(t), prefix))

@dispatch(list, str)
def _rename_variables(t, prefix):
    return list(rename_variables(iter(t), prefix))

@dispatch(dict, str)
def _rename_variables(d, prefix):
    return dict((k, rename_variables(v, prefix)) for k, v in d.items())

@dispatch(object, str)
def _rename_variables(o, prefix):
    return o  # catch all, just return the object


def rename_variables(e, prefix):
    if isvar(e):
        return Var(prefix+e.token)
    return _rename_variables(e, prefix)


if __name__ == '__main__':
    x, y = Var('x'), Var('y')
    e = (1, x, (3, y))
    result = rename_variables(e,'__parent__.')
    e = {'a': Var('x'), 'b': Var('__parent__.x'), 'x': Var('__parent__.y')}

    print({k:Var(v.token[len('__parent__.'):]) for k,v in e.items() if v.token.startswith('__parent__.')})
