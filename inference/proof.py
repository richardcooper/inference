import itertools

from unification import reify, Var

class Proof:
    def __init__(self, rule, variables, premises=()):
        self.rule = rule
        self.premises = premises
        self.variables = variables

    @property
    def conclusion(self):
        return reify(self.rule.conclusion, self.variables)

    def __getitem__(self, item_name):
        return reify(self.variables[Var(item_name)], self.variables)

    def __str__(self):
        premise_strs = [str(p) for p in self.premises]
        conclusion_str = str(self.conclusion)
        template = '  '.join('{:<%d}'%len(max(y, key=len)) for y in [x.split('\n')[::-1] for x in premise_strs])
        result = [template.format(*y) for y in itertools.zip_longest(*(x.split('\n')[::-1] for x in premise_strs), fillvalue='')][::-1]
        width = max([line.rfind('-') for line in result]) if result else 0
        width = max(len(conclusion_str), width+1)
        result.append('-'*width+f'  <<{self.rule.name}>>')
        result.append(conclusion_str)
        return '\n'.join(result)
