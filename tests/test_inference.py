import pytest

import inference
from inference import Rule

# The tests is this file are based on Chapter 3 of the book "Types and
# Programming Languages" by Benjamin C. Pierce. That chapter describes a simple
# untyped language of boolean and arithmetic expressions.

# This class describes the syntax of that language
class ArithSyntax(inference.Parser):
    rule = (
        '{term} ⟶ {term}',
        '{term} ∈ NV',
    )
    term = (
        'true',
        'false',
        '0',
        'if {term} then {term} else {term}',
        'succ {term}',
        'pred {term}',
        'iszero {term}',
    )

class SmallStepSemantics(inference.Rules):
    E_IfTrue        = Rule('if true then {t2} else {t3} ⟶ {t2}')
    E_IfFalse       = Rule('if false then {t2} else {t3} ⟶ {t3}')
    E_If            = Rule('if {t1} then {t2} else {t3} ⟶ if {t1ʹ} then {t2} else {t3}',
                        given=['{t1} ⟶ {t1ʹ}']
                    )
    E_PredZero      = Rule('pred 0 ⟶ 0')
    E_PredSucc      = Rule('pred succ {nv} ⟶ {nv}',
                        given=['{nv} ∈ NV']
                    )
    E_Succ          = Rule('succ {t} ⟶ succ {tʹ}',
                        given=['{t} ⟶ {tʹ}']
                    )
    E_Pred          = Rule('pred {t} ⟶ pred {tʹ}',
                        given=['{t} ⟶ {tʹ}']
                    )
    E_IsZeroZero    = Rule('iszero 0 ⟶ true')
    E_IsZeroSucc    = Rule('iszero succ {nv} ⟶ false',
                        given=['{nv} ∈ NV']
                    )
    E_IsZero        = Rule('iszero {t} ⟶ iszero {tʹ}',
                        given=['{t} ⟶ {tʹ}']
                    )
    S_NumericZero   = Rule('0 ∈ NV')
    S_NumericSucc   = Rule('succ {nv} ∈ NV',
                        given=['{nv} ∈ NV']
                    )
small_step_semantics = SmallStepSemantics(ArithSyntax())


def evaluate(term):
    # TODO remove the "rule=" from this method and use positional arg instead
    goal = ArithSyntax().parse(rule=(term+' ⟶ {result}'))
    for proof in small_step_semantics.prove(goal):
        result = proof['__parent__.result']
        yield (result, proof)

@pytest.mark.parametrize("term,expected_result", [
    ('if true then true else false', 'true'),
    ('if false then true else false', 'false'),
    (
        'if if true then false else true then true else false',
        'if false then true else false'
    ),
    ('pred 0', '0'),
    ('pred succ 0', '0'),
    ('succ pred 0', 'succ 0'),
    ('pred pred succ 0', 'pred 0'),
    ('iszero 0', 'true'),
    ('iszero succ 0', 'false'),
    ('iszero pred 0', 'iszero 0'),
])
def test_single_step_evaluation(term, expected_result):
    # TODO also check that they are deterministic
    expected_result = ArithSyntax().parse(term=expected_result)
    (result, proof) = next(evaluate(term))
    assert result == expected_result
