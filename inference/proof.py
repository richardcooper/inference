import itertools

from unification import reify, Var


class Term(tuple):
    def __str__(self):
        return ' '.join(Term.__str__(x) if isinstance(x, tuple) else str(x) for x in self)

    def __repr__(self):
        return '(%s)'%(' '.join(Term.__repr__(x) if isinstance(x, tuple) else str(x) for x in self))



class Proof:
    def __init__(self, rule, variables, premises=()):
        self.rule = rule
        self.premises = premises
        self.variables = variables

    @property
    def conclusion(self):
        return Term(reify(self.rule.conclusion, self.variables))

    @property
    def parent_variables(self):
        # Before we throw away the variables which don't come from the parent
        # we need to resolving any indirection in the variables. We can do that
        # by reify the variables against themselves. For example if:
        #    self.variables = {~__parent__.x: ~x, ~x: '0'}
        # then without this reify()
        #    parent_variables = {~x: ~x} which is broken.
        # with this reify()
        #    parent_variables = {~x: 0} which is correct.
        reified_variables = reify(self.variables, self.variables)

        prefix = '__parent__.'
        return {
            Var(k.token[len(prefix):]) : v
            for k,v in reified_variables.items()
            if k.token.startswith(prefix)
        }


    def __getitem__(self, item_name):
        reified_item = reify(self.variables[Var(item_name)], self.variables)
        if isinstance(reified_item, tuple):
            return Term(reified_item)
        else:
            return Term((reified_item,))

    def __str__(self, to_string=str):
        premise_strs = [to_string(p) for p in self.premises]
        conclusion_str = to_string(self.conclusion)
        template = '  '.join('{:<%d}'%len(max(y, key=len)) for y in [x.split('\n')[::-1] for x in premise_strs])
        result = [template.format(*y) for y in itertools.zip_longest(*(x.split('\n')[::-1] for x in premise_strs), fillvalue='')][::-1]
        width = max([line.rfind('-') for line in result]) if result else 0
        width = max(len(conclusion_str), width+1)
        result.append('-'*width+f'  <<{self.rule.name}>>')
        result.append(conclusion_str)
        return '\n'.join(result)

    def __repr__(self):
        return self.__str__(to_string=repr)

    @property
    def size(self):
        return 1 + sum(x.size for x in self.premises)

    @property
    def depth(self):
        return 1 + max((x.depth for x in self.premises), default=0)

    @property
    def width(self):
        return sum(x.width for x in self.premises) or 1

    def _repr_html_(self):
        from .jupyter import proof_to_html
        return proof_to_html(self)
