from pyparsing import Combine, oneOf, ZeroOrMore, Word, alphanums, Optional, nums, OneOrMore
from . import domain, hostname, ipv4, ipv6

url_path = ZeroOrMore("/" + Word(alphanums + "-.[]~_%")) + Optional("/")
url_host_port = (
    (hostname.expr | ipv4.expr | ipv6.expr) + Optional(":" + Word(nums, max=5))
) | domain.expr
query = (
    Word(alphanums + "-!*'@;:$,/%._\+~#[]")
    + "="
    + Word(alphanums + "-!*'@;:$,/%._\+~#[]")
)
url_query = Optional("?" + query + ZeroOrMore("&" + query))
url_account_pwd = Optional(Word(alphanums) + ":" + Word(alphanums)) + Optional("@")
url_fragment = Optional("#" + Word(alphanums + "-!*'@;:&$,/?%._\+~#=[]"))


http = Combine(
    oneOf(["https://", "http://", "hxxps://", "hxxp://", "https[://]", "http[://]", "hxxps[://]", "hxxp[://]", "https[:]//", "http[:]//", "hxxps[:]//", "hxxp[:]//"])
    + url_host_port
    + url_path
    + url_query
    + url_fragment
)

ftp = Combine(
    oneOf("ftps:// ftp:// fxps:// fxp:// ftps[:]// ftp[:]// fxps[:]// fxp[:]//")
    + url_account_pwd
    + url_host_port
    + url_path
    + Optional(";type=" + Word(alphanums))
)

gopher_or_file = Combine(oneOf("gopher:// file://") + url_host_port + url_path)
telnet = Combine(
    oneOf("telnet:// tn3270://") + url_account_pwd + url_host_port + Optional("/")
)

mailto = Combine(
    "mailto:" + OneOrMore(Word(alphanums)) + "@" + OneOrMore(Word(alphanums + "."))
)
parser = (http | ftp | gopher_or_file | mailto | telnet).setResultsName("URL")


"""
expr = Combine(
    oneOf("https:// http://")
    + (hostname.expr | domain.expr | ipv4.expr | ipv6.expr)
    + "/"
    + ZeroOrMore(Word(alphanums + "-.") + "/")
    # + Optional(Word(alphanums))
)

parser = expr.setResultsName("URL")
"""
"""
from pyparsing.core import Regex

parser = Regex(
    r"((http|hxxp)[s]?|(ftp|fxp))?:\/\/(www(\.|\[\.\]))?[-a-zA-Z0-9@:%._\+~#=]{1,256}(\.|\[\.\])?[a-zA-Z0-9()]{1,6}\b(([.]?[-a-zA-Z0-9()!@:%_\+~#?&\/\/=])*)"
).setResultsName("URL")
"""
