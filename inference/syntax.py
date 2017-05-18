from collections import defaultdict
import re

import pyparsing as pp
from unification import Var

# TODO THIS BIT IS NOT GENERAL PURPOSE
def parse_token(token):
    if isinstance(token, str) and token.startswith('{'):
        return Var(token.lstrip('{').rstrip('}'))
    else:
        return token

def parse_action(tokens):
    parsed_tokens = tuple(parse_token(t) for t in tokens)
    if len(parsed_tokens) == 1 and isinstance(parsed_tokens[0], (tuple, Var)):
        # In some more complex grammars a token could go through many non-terminal grammar
        # rules before being matched by a terminal. That leads to parse trees with a level
        # of nesting equal to the number of non-terminals passed through. To avoid having
        # the shape of the AST depends on implementation details of the grammar we unwrap
        # redundantly nested terms and variables here.
        return parsed_tokens[0]
    else:
        return parsed_tokens


class Syntax:
    def __init__(self, *definitions):
        self.definitions = definitions
        # TODO can we do this lazily so parser is only wrapped in a Forward if
        # absolutely necessary?
        self.parser = pp.Forward()

    def __set_name__(self, owner, name):
        self.owner = owner
        string_parsers = [self.parser_for_string(s) for s in self.definitions]
        parser = pp.Or(string_parsers)
        parser.setName(name)

        # TODO THIS BIT IS NOT GENERAL PURPOSE
        metavar = pp.Regex(r'\{[^\{\}\s]+\}')
        metavar.setName('metavar')
        parser |= metavar

        self.parser <<= parser

    def parser_for_string(self, string):
        if string == '':
            return pp.Empty()

        if hasattr(string, 'match'):
            return pp.Regex(string)

        tokens = string.split()
        token_parsers = [self.parser_for_token(t) for t in tokens]
        parser = pp.And(token_parsers)
        parser.setParseAction(parse_action)
        #print('Grammar for', string, 'is', repr(parser))
        return parser

    def parser_for_token(self, token):
        if token.startswith('{'):
            non_terminal_name = token.lstrip('{').rstrip('}')
            return getattr(self.owner, non_terminal_name).parser
            # TODO Check what happens if this getattr() fails or returns
            # something without a parser. Raise a better exception if it's not
            # clear.
        else:
            return pp.Keyword(token)

    def parse(self, string_to_parse):
        return self.parser.parseString(string_to_parse, parseAll=True)[0]
