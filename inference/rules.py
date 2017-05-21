
from unification import Var, unify, reify

from .proof import Proof, Term
from .rename_variables import rename_variables
from .errors import NoProofFoundError, MultipleProofsError


class Rule:
    def __init__(self, conclusion, given=()):
        self.conclusion = conclusion
        self.premises = given
        self.name = None

    def __set_name__(self, owner, name):
        self.name = name
        self.conclusion = owner.parse(self.conclusion)
        self.premises = tuple(owner.parse(p) for p in self.premises)


class Rules:

    @classmethod
    def get_rules(cls):
        for name in dir(cls):
            candidate_rule = getattr(cls, name)
            if isinstance(candidate_rule, Rule):
                rule = candidate_rule
                yield rule

    @classmethod
    def _proofs_of_many(cls, terms):
        (first_term, *other_terms) = terms
        for proof in cls._proofs_of(first_term):
            if other_terms:
                reified_other_terms = reify(other_terms, proof.parent_variables)
                for other_proofs in cls._proofs_of_many(reified_other_terms):
                    yield (proof, *other_proofs)
            else:
                yield (proof, )

    @classmethod
    def _proofs_of(cls, term):

        # If term contains any variables then we rename them here so that they
        # don't collide with variable names used in this proof.
        term = rename_variables(term, '__parent__.')

        for rule in cls.get_rules():
            variables = unify(term, rule.conclusion)
            if variables is False:
                continue

            if not rule.premises:
                yield Proof(rule, variables)
                continue

            # If we reach here it means that there are premises to prove.
            reified_premises = [reify(x, variables) for x in rule.premises]
            for premise_proofs in cls._proofs_of_many(reified_premises):
                candiate_variables = variables
                for (premise, premise_proof) in zip(reified_premises, premise_proofs):
                    candiate_variables = unify(premise, premise_proof.conclusion, candiate_variables)
                    if candiate_variables is False:
                        break
                else:
                    yield Proof(rule, candiate_variables, premise_proofs)


    @classmethod
    def parse(cls, *args, **kwargs):
        number_of_args = len(args) + len(kwargs)
        if number_of_args != 1:
            raise TypeError(f'{cls.__name__}.parse expected 1 argument, got {number_of_args}')
        if kwargs:
            (non_terminal_name, string_to_parse) = kwargs.popitem()
        else:
            non_terminal_name = 'rule'
            string_to_parse = args[0]
        return getattr(cls, non_terminal_name).parse(string_to_parse)

    @classmethod
    def prove(cls, goal, unambiguously=True):
        term = cls.parse(goal)
        proofs = cls._proofs_of(term)
        try:
            proof = next(proofs)
        except StopIteration:
            raise NoProofFoundError from None

        if unambiguously:
            try:
                next(proofs)
                raise MultipleProofsError()
            except StopIteration:
                pass

        return proof

    @classmethod
    def proofs_of(cls, goal):
        term = cls.parse(goal)
        yield from cls._proofs_of(term)

    @classmethod
    def solve(cls, goal, unambiguously=True):
        proof = cls.prove(goal, unambiguously=unambiguously)
        result = proof['__parent__.__result__']
        result.proof = proof
        return result

    @classmethod
    def solutions_to(cls, goal):
        for proof in cls.proofs_of(goal):
            result = proof['__parent__.__result__']
            result.proof = proof
            yield result
