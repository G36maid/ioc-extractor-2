from pyparsing import Combine, Word, oneOf, alphas, alphanums, printables

"""
reference: https://www.microsoft.com/en-us/wdsi/threats/
resource: https://www.microsoft.com/en-us/wdsi/api/countryInfo
"""

threat_categories = [
    "Adware",
    "App",
    "Backdoor",
    "Behavior",
    "BrowserModifier",
    "Constructor",
    "DDoS",
    "DoS",
    "Exploit",
    "Gen",
    "HackTool",
    "Joke",
    "MonitoringTool",
    "PUA",
    "PWS",
    "Program",
    "Ransom",
    "Trojan",
]

threat_categories_to_text = " ".join(threat_categories)

categories = oneOf(threat_categories_to_text, caseless=False, asKeyword=False)
field = Word(alphas.upper(), alphanums)
name = Word(alphanums.upper(), printables)

expr = Combine(categories + ":" + field + "/" + name)
parser = expr.setResultsName("Microsoft Defender Threat")
