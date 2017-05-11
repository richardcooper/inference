import pytest

import inference
Var = inference.Var

# The tests is this file are based on Chapter 3 of the book "Types and
# Programming Languages" by Benjamin C. Pierce. That chapter describes a simple
# untyped language of boolean and arithmetic expressions. These rules allow that
# language to be evaluated.
small_step_semantics = inference.Rules()
small_step_semantics.add('E_IfTrue', (('if', 'true', 'then', Var('t2'), 'else', Var('t3')), '⟶', Var('t2')))
small_step_semantics.add('E_IfFalse', (('if', 'false', 'then', Var('t2'), 'else', Var('t3')), '⟶', Var('t3')))
small_step_semantics.add('E_If',
    (
        ('if', Var('t1'), 'then', Var('t2'), 'else', Var('t3')),
        '⟶',
        ('if', Var('t1_prime'), 'then', Var('t2'), 'else', Var('t3'))
    ),
    given=[
        (Var('t1'), '⟶', Var('t1_prime')),
    ]
)
small_step_semantics.add('E_PredZero',(('pred', '0'), '⟶', '0'))
small_step_semantics.add('E_PredSucc',(('pred', ('succ', Var('nv'))), '⟶', Var('nv')), given=[
    (Var('nv'), '∈', 'NV')
])
small_step_semantics.add('E_Succ',
    (
        ('succ', Var('t')),
        '⟶',
        ('succ', Var('t_prime')),
    ),
    given=[
        (Var('t'), '⟶', Var('t_prime')),
    ]
)
small_step_semantics.add('E_Pred',(('pred', Var('t')), '⟶', ('pred', Var('t_prime'))), given=[
    (Var('t'), '⟶', Var('t_prime')),
])
small_step_semantics.add('E_IsZeroZero',(('iszero', '0'), '⟶', 'true'))
small_step_semantics.add('E_IsZeroSucc',(('iszero', ('succ', Var('nv'))), '⟶', 'false'), given=[
    (Var('nv'), '∈', 'NV')
])
small_step_semantics.add('E_IsZero',(('iszero', Var('t')), '⟶', ('iszero', Var('t_prime'))), given=[
    (Var('t'), '⟶', Var('t_prime'))
])
small_step_semantics.add('S_NumericZero',('0', '∈', 'NV'))
small_step_semantics.add('S_NumericSucc',(('succ', Var('nv')), '∈' 'NV'), given=[
    (Var('nv'), '∈', 'NV')
])


def evaluate(term):
    for proof in small_step_semantics.prove((term,'⟶',Var('result'))):
        result = proof['__parent__.result']
        yield (result, proof)

@pytest.mark.parametrize("term,result", [
    (('if', 'true', 'then', 'true', 'else', 'false'), 'true'),
    (('if', 'false', 'then', 'true', 'else', 'false'), 'false'),
    (
        ('if', ('if', 'true', 'then', 'false', 'else', 'true'), 'then', 'true', 'else', 'false'),
        ('if', 'false', 'then', 'true', 'else', 'false')
    ),
    (('pred', '0'), '0'),
    (('pred', ('succ', '0')), '0'),
    (('succ', ('pred', '0')), ('succ', '0')),
    (('pred', ('pred', ('succ', '0'))), ('pred', '0')),
    (('iszero', '0'), 'true'),
    (('iszero', ('succ', '0')), 'false'),
    (('iszero', ('pred', '0')), ('iszero', '0')),
])
def test_single_step_evaluation(term, result):
    # TODO also check that they are deterministic
    assert next(evaluate(term))[0] == result
