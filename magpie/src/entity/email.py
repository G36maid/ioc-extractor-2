from pyparsing import Combine, Word, alphanums
from . import domain, hostname

expr = Combine(Word(alphanums + "-_[].") + "@" + (domain.expr | hostname.expr))
parser = expr.setResultsName("Email")

"""
from pyparsing.core import Regex
parser = Regex(r'(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))\@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+(\.|\[\.\]))+[a-zA-Z]{2,}))'
).setResultsName("email")
"""