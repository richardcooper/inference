from collections import defaultdict

from pyparsing import Keyword, Forward, And, Or

from unification import Var

# TODO THIS BIT IS NOT GENERAL PURPOSE
from pyparsing import Regex
def parse_token(token):
    if isinstance(token, str) and token.startswith('{'):
        return Var(token.lstrip('{').rstrip('}'))
    else:
        return token

def parse_action(tokens):
    return tuple(parse_token(t) for t in tokens)


class Syntax:
    def __init__(self, *definitions):
        self.definitions = definitions
        # TODO can we do this lazily so parser is only wrapped in a Forward if
        # absolutely necessary?
        self.parser = Forward()

    def __set_name__(self, owner, name):
        self.owner = owner
        string_parsers = [self.parser_for_string(s) for s in self.definitions]
        parser = Or(string_parsers)

        # TODO THIS BIT IS NOT GENERAL PURPOSE
        metavar = Regex(r'\{[^\{\}\s]+\}')
        parser = parser | metavar

        self.parser <<= parser

    def parser_for_string(self, string):
        tokens = string.split()
        token_parsers = [self.parser_for_token(t) for t in tokens]
        parser = And(token_parsers)
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
            return Keyword(token)

    def parse(self, string_to_parse):
        return self.parser.parseString(string_to_parse)[0]
