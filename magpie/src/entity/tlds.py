import requests
import hashlib
from pathlib import Path
from functional import seq
from functools import lru_cache


class TopLevelDomain(object):

    # iana tlds
    URL = "https://data.iana.org/TLD/tlds-alpha-by-domain.txt"
    MD5 = "https://data.iana.org/TLD/tlds-alpha-by-domain.txt.md5"

    def __init__(self, filepath):
        self.filepath = self.is_updated_file(filepath)

    def is_updated_file(self, filepath):
        path = Path(filepath)

        def checksum(path):
            # get md5 checksum from iana
            resp = requests.get(self.MD5)
            iana_md5 = resp.text.split("  ")[0]
            # generate file md5 checksum
            try:
                h = hashlib.md5(path.read_bytes())
                file_md5 = h.hexdigest()
                return iana_md5 == file_md5
            except:
                return False

        if path.exists() & checksum(path):
            pass
        else:
            # download tlds file
            response = requests.get(self.URL)
            with path.open(mode="wb") as f:
                f.write(response.text.encode())

        return path

    @property
    @lru_cache()
    def registed_domains(self):

        """
        add special domains
        https://en.wikipedia.org/wiki/List_of_Internet_top-level_domains
        """
        iana_tlds = self.filepath.read_text()

        # merge all domains
        regular_domains = iana_tlds.lower().splitlines()
        special_use_domains = [
            "example",
            "invalid",
            "local",
            "localhost",
            "onion",
            "test",
        ]
        crypto_use_domains = ["eth", "zil", "crypto", "bit"]

        domains = (
            seq(regular_domains + special_use_domains + crypto_use_domains)
            .drop(1)
            .filter_not(lambda tld: tld.startswith("xn--"))
            .sorted()
            .cache()
        )

        return domains.to_list()
