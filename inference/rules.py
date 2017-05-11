
from unification import Var, unify, reify

from .proof import Proof

class Rules:
    def __init__(self):
        self.rules = []

    def add(self, rule_name, inference, given=()):
        self.rules.append((rule_name, inference, given))

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

        for (rule_name, conclusion, premises) in self.rules:
            variables = unify(term, conclusion)
            if variables is False:
                continue

            if not premises:
                yield Proof(rule_name, conclusion, variables)
                continue

            # If we reach here it means that there are premises to prove.
            reified_premises = [reify(x, variables) for x in premises]
            for premise_proofs in self.prove_many(reified_premises):
                candiate_variables = variables
                for (premise, premise_proof) in zip(reified_premises, premise_proofs):
                    candiate_variables = unify(premise, premise_proof.conclusion, candiate_variables)
                    if candiate_variables is False:
                        continue # TODO is this the correct way to bail out here?
                        # Don't we need to continue the for loop one level higher?
                yield Proof(rule_name, conclusion, candiate_variables, premise_proofs)
