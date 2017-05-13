
from unification import Var, unify, reify

from .proof import Proof

class Rule:
    def __init__(self, conclusion, given=()):
        self.conclusion = conclusion
        self.premises = given
        self.name = None

    def __set_name__(self, owner, name):
        self.name = name


class Rules:

    @property
    def rules(self):
        for name in dir(self):
            candidate_rule = getattr(self, name)
            if isinstance(candidate_rule, Rule):
                rule = candidate_rule

                # TODO If posible move this into Rule.__set_name__. Need to
                # no some rejiging so that the parser is available at that
                # point first.
                if isinstance(rule.conclusion, str):
                    rule.conclusion = self.parse(rule=rule.conclusion)
                    rule.premises = tuple(self.parse(rule=p) for p in rule.premises)

                yield rule

    def prove_many(self, terms):
        (first_term, *other_terms) = terms
        for proof in self.prove(first_term):
            if other_terms:
                reified_other_terms = reify(other_terms, proof.variables)
                for other_proofs in prove_many(self, reified_other_terms):
                    yield (proof, *other_proofs)
            else:
                yield (proof, )


    def prove(self, term):

        # If term contains any variables then we rename them here so that they
        # don't collide with variable names used in this proof.
        # TODO Pull out into a function and generalise it to
        # handle the parent vars being nested rather than top level.
        term = list(term)
        for (i, x) in enumerate(term):
            if isinstance(x, Var):
                term[i] = Var('__parent__.'+x.token)
        term = tuple(term)

        for rule in self.rules:
            variables = unify(term, rule.conclusion)
            if variables is False:
                continue

            if not rule.premises:
                yield Proof(rule, variables)
                continue

            # If we reach here it means that there are premises to prove.
            reified_premises = [reify(x, variables) for x in rule.premises]
            for premise_proofs in self.prove_many(reified_premises):
                candiate_variables = variables
                for (premise, premise_proof) in zip(reified_premises, premise_proofs):
                    candiate_variables = unify(premise, premise_proof.conclusion, candiate_variables)
                    if candiate_variables is False:
                        continue # TODO is this the correct way to bail out here?
                        # Don't we need to continue the for loop one level higher?
                yield Proof(rule, candiate_variables, premise_proofs)

    def parse(self, **kwargs):
        items = list(kwargs.items())
        (non_terminal_name, string_to_parse) = items.pop()
        # TODO raise an exception if items is not now empty
        return getattr(self, non_terminal_name).parse(string_to_parse)
