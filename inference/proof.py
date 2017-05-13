import itertools

from unification import reify, Var


class Term(tuple):
    def __str__(self):
        return ' '.join(Term.__str__(x) if isinstance(x, tuple) else str(x) for x in self)

    def __repr__(self):
        # TODO maybe wrap this in <Term "%r">
        # TODO refactor for clarity and code resuse with __str__
        return '(%s)'%(' '.join(Term.__repr__(x) if isinstance(x, tuple) else str(x) for x in self))



class Proof:
    def __init__(self, rule, variables, premises=()):
        self.rule = rule
        self.premises = premises
        self.variables = variables

    @property
    def conclusion(self):
        return Term(reify(self.rule.conclusion, self.variables))

    def __getitem__(self, item_name):
        return Term(reify(self.variables[Var(item_name)], self.variables))

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
