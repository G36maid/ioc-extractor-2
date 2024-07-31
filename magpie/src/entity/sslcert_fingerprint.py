from pyparsing import Combine, Word, hexnums

expr = sslcert_fingerprint = Combine(
    Word(hexnums.lower(), exact=2) + (":" + Word(hexnums.lower(), exact=2)) * 19
)
parser = expr.setResultsName("SSL Cert Fingerprint")