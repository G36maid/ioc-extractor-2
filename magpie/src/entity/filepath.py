from pyparsing import (
    Combine,
    Word,
    alphas,
    alphanums,
    printables,
    oneOf,
    OneOrMore,
    Optional,
)
from . import file_extensions


def verify_extension(string, loc, tokens):
    # tokens is pyparsing.ParseResults
    exceptions = ['e.g', 'E.g', 'i.e']
    if tokens[0] not in exceptions:
        token = "." + tokens[0].split(".", 1)[-1]
        verification = token in file_extensions.data
        return verification
    else:
        pass


filename = Combine(
    Word(alphanums + "-_") + OneOrMore("." + Word(alphanums))
).addCondition(
    verify_extension
)  # .setResultsName("FileName")

windows_filepath = Combine(
    Optional(oneOf(alphas.upper()) + ":\\")
    + OneOrMore(Word(printables, excludeChars="\\") + "\\")
    + filename
)

unixlike_filepath = Combine(
    "/" + OneOrMore(Word(printables, excludeChars="/") + "/") + filename
)

expr = windows_filepath | unixlike_filepath | filename
parser = expr.setResultsName("File Path")
