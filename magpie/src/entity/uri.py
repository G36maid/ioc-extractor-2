from pyparsing import Combine, Word, alphanums, Optional, OneOrMore, alphas, hexnums, oneOf
from . import url


"""
expr = Combine(url.expr + Word(printables))
parser = expr.setResultsName("URI")
"""
"""
from pyparsing.core import Regex
parser = Regex(
    r"[a-zA-Z0-9\-@=#~$()[\]&;%_]+(\\|\/\/|:|:\/\/|:\\)[a-zA-Z0-9\-@=#~$()[\]&;%_]+([\\\/\?\*\"\'\>\<\:\|\.\-@=#~$()\[\]&;%]+[a-zA-Z0-9]+)*"
).setResultsName("URI")
# "([a-z][a-z0-9+.-]*):(?!\s)(?!$)(?:\/\/((?:(?=((?:[A-Za-z0-9-._~!$&'()*+,;=:[\]]|%[0-9A-F]{2})*))(\3)@)?(?=(\[[0-9A-F:.[\]]{2,}\]|(?:[a-zA-Z0-9-._~!$&'()*+,;=[\]]|%[0-9A-F]{2})*))\5(?::(?=(\d*))\6)?)(\/(?=((?:[A-Za-z0-9-._~!$&'()*+,;=:@\/[\]]|%[0-9A-F]{2})*))\8)?|(\/?(?!\/)(?=((?:[a-zA-Z0-9-._~!$&'()*+,;=:@\/[\]]|%[0-9A-F]{2})*))\10)?)(?:\?(?=((?:[a-zA-Z0-9-._~!$&'()*+,;=:@\/?[\]]|%[0-9A-F]{2})*))\11)?(?:#(?=((?:[A-Za-z0-9-._~!$&'()*+,;=:@\/?[\]]|%[0-9A-F]{2})*))\12)?"
# r"([a-z][a-z0-9+.-]*):(?![$\s])(?:\/\/((?:(?=((?:[A-Za-z0-9-._~!$&'()*+,;=:[\]]|%[0-9A-F]{2})*))(\3)@)?(?=(\[[0-9A-F:.[\]]{2,}\]|(?:[a-zA-Z0-9-._~!$&'()*+,;=[\]]|%[0-9A-F]{2})*))\5(?::(?=(\d*))\6)?)(\/(?=((?:[A-Za-z0-9-._~!$&'()*+,;=:@\/[\]]|%[0-9A-F]{2})*))\8)?|(\/?(?!\/)(?=((?:[a-zA-Z0-9-._~!$&'()*+,;=:@\/[\]]|%[0-9A-F]{2})*))\10)?)(?:\?(?=((?:[a-zA-Z0-9-._~!$&'()*+,;=:@\/?[\]]|%[0-9A-F]{2})*))\11)?(?:#(?=((?:[A-Za-z0-9-._~!$&'()*+,;=:@\/?[\]]|%[0-9A-F]{2})*))\12)?"
"""


scheme = Word(alphas.lower(), alphanums) + oneOf([":", "[:]", "[:"]) + Optional(oneOf(["//", "//]"])) #":" + Optional("//")
uri_user_info = OneOrMore(
    ("%" + Word(hexnums) | Word(alphanums, "-._~[]") | Word("!$&'()*+,;=") | ":")
) + Optional("@")

parser = Combine(
    scheme
    + uri_user_info
    + Optional(url.url_host_port)
    + url.url_path
    + url.url_query
    + url.url_fragment
).setResultsName("URI")
