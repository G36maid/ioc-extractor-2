"""
generate pulse and indicator label from feed
"""

from collections import namedtuple, ChainMap
from itertools import product
from functional import seq


class PulseLabelGenerator:

    """
    generate pulse label from feed
    """

    SINGULAR_PARTS = ["name", "description", "adversary"]
    PLRUAL_PARTS = [
        "tags",
        "targeted_countries",
        "malware_families",
        "attack_ids",
        "industries",
    ]

    PulseLabel = namedtuple("PulseLabel", ["category", "group", "role"])

    def __init__(self, pulse: dict):
        self.pulse = pulse

    @property
    def singular_label(self):
        """
        get items which field is string and not ""
        """
        items = {
            key: self.pulse.get(key)
            for key in self.SINGULAR_PARTS
            if self.pulse.get(key) != ""
        }.items()
        # make label
        label = (
            seq(items)
            .starmap(lambda key, value: (value, key))
            .starmap(lambda string, key: (string, self.PulseLabel(key, 0, None)))
        )
        return label.to_dict()

    @property
    def plrual_label(self):
        """
        get items which field is list and not []
        """
        items = {
            key: self.pulse.get(key)
            for key in self.PLRUAL_PARTS
            if self.pulse.get(key) != []
        }.items()

        # key name replacements
        substitution = {
            "tags": "tag",
            "targeted_countries": "targeted_country",
            "malware_families": "malware_family",
            "attack_ids": "attack_id",
            "industries": "industry",
        }
        # make label
        label = (
            seq(items)
            .starmap(lambda key, values: product(values, [key]))
            .flatten()
            .starmap(
                lambda string, key: (
                    string,
                    self.PulseLabel(substitution.get(key), 0, None),
                )
            )
        )
        return label.to_dict()

    def get_label(self):
        """
        merge label together
        """
        return ChainMap(self.singular_label, self.plrual_label)



class IndicatorLabelGenerator:

    """
    generate pulse label from feed
    """

    IndicatorLabel = namedtuple("IndicatorLabel", ["category", "group", "role"])

    def __init__(self, indicators):
        self.indicators = indicators

    @property
    def enumerated_indicators(self):
        """
        enumerate indicators started from 1, to distinguish with pulse
        """
        indicators = enumerate(self.indicators, 1)
        return indicators

    @staticmethod
    def extract(index, indicator):
        """
        extract from feed's indicator part, lazy but nasty
        """
        extractions = (
            (
                (indicator.get("content"), (indicator.get("type"), index, "rule"))
                if indicator.get("content").startswith("rule")
                and indicator.get("type") is "YARA"
                else (
                    indicator.get("indicator"),
                    (indicator.get("type"), index, indicator.get("role")),
                )
            ),
            (indicator.get("title"), ("title", index, None)),
            (indicator.get("description"), ("description", index, None)),
        )

        return extractions

    def get_label(self):
        """
        filter and reformat label
        """
        label = (
            seq(self.enumerated_indicators)
            .starmap(lambda index, indicator: (self.extract(index, indicator)))
            .flatten()
            .starmap(
                lambda string, extraction: (
                    string,
                    self.IndicatorLabel(*extraction),
                )  # formatting with namedtuple
            )
            .filter(
                lambda label: label[0] is not ""
            )  # if string is not existed, drop out
        )

        return label.to_dict()
