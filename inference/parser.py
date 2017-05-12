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

class Parser:

    def __init__(self):

        self.non_terminals = defaultdict(Forward)
        non_terminal_names = [t for t in dir(self.__class__) if t not in dir(Parser)]

        for non_terminal_name in non_terminal_names:
            non_terminal_def = getattr(self, non_terminal_name)
            string_parsers = [self.parser_for_string(s) for s in non_terminal_def]
            parser = Or(string_parsers)

            # TODO THIS BIT IS NOT GENERAL PURPOSE
            metavar = Regex(r'\{[^\{\}\s]+\}')
            parser = parser | metavar

            self.non_terminals[non_terminal_name] <<= parser

    def parser_for_token(self, token):
        if token.startswith('{'):
            non_terminal_name = token.lstrip('{').rstrip('}')
            return self.non_terminals[non_terminal_name]
        else:
            return Keyword(token)

    def parser_for_string(self, string):
        tokens = string.split()
        token_parsers = [self.parser_for_token(t) for t in tokens]
        parser = And(token_parsers)
        parser.setParseAction(parse_action)
        #print('Grammar for', string, 'is', repr(parser))
        return parser

    def parse(self, **kwargs):
        items = list(kwargs.items())
        (non_terminal_name, string_to_parse) = items.pop()
        # TODO raise an exception if items is not now empty
        return self.non_terminals[non_terminal_name].parseString(string_to_parse)[0]
