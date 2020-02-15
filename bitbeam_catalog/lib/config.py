"""Configuration module."""
from os.path import join

import logging as log

from openapi_core.shortcuts import RequestValidator, ResponseValidator
from openapi_core import create_spec
from extendparser import ExtendParser
from openapi_spec_validator.schemas import read_yaml_file
from sqlite3 import connect

from .. import __name__ as appname

HANDLER = log.StreamHandler()
log.root.addHandler(HANDLER)
log.getLogger("poorwsgi").setLevel("WARNING")
log.getLogger("openapi_spec_validator.validators").setLevel("WARNING")
log.getLogger("openapi_spec_validator.decorators").setLevel("WARNING")

LOGGER = log.getLogger(appname)

LOG_FORMAT = (
    "%(asctime)s %(levelname)s: %(name)s: %(message)s "
    "{%(filename)s.%(funcName)s():%(lineno)d}"
)

OPEN_API = "openapi.yaml"


class Config(ExtendParser):
    """Configuration class."""

    def __init__(self, config_file):
        super(Config, self).__init__()

        with open(config_file, "r") as src:
            self.read_file(src)

        self.log_level = self.get_option("logging", "level",
                                         fallback="WARNING")
        self.log_format = self.get_option("logging", "format",
                                          fallback=LOG_FORMAT)

        log.root.setLevel(self.log_level)  # final output
        LOGGER.setLevel(self.log_level)
        HANDLER.setFormatter(log.Formatter(self.log_format))

        self.static_files = self.get_option("main", "static_files")

        self.validate_response = self.get_option(
            "main", "validate_response", target=bool, fallback=False
        )
        spec = create_spec(read_yaml_file(join(self.static_files, OPEN_API)))
        self.request_validator = RequestValidator(spec)
        self.response_validator = ResponseValidator(spec)

        self.db_uri = self.get_option("main", "db_uri")

        self.db = connect(self.db_uri, uri=True)
        self.db.execute("SELECT * FROM parts LIMIT 1")
