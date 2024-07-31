#from pyparsing import pyparsing_common

#expr = pyparsing_common.ipv4_address
#parser = expr.setResultsName("IPv4")

from pyparsing.core import Regex

expr = Regex(
    r"(25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})((\.|\[\.\])(25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})){3}"
).set_name("IPv4 address")
parser = expr.setResultsName("IPv4")
