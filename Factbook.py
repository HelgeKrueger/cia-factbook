import os
import requests
import zipfile
from io import BytesIO
import json
import glob
import pandas as pd

from converters import *


class Factbook:
    def __init__(self, data_path="data"):
        self.data_path = data_path
        self.factbook_url = (
            "https://github.com/factbook/factbook.json/archive/refs/heads/master.zip"
        )

        self.keywords = []
        self.units = None

    def add_keyword(self, keyword):
        self.keywords.append(keyword)
        return self

    def set_unit(self, unit):
        self.units = [unit]
        return self

    def set_units(self, units):
        self.units = units
        return self

    def _get_for_short(self, short):
        result = self.get_content(short)
        for keyword in self.keywords:
            if keyword == "flatten":
                for x in result.keys():
                    if type(result[x]) == dict:
                        result[x] = result[x]["text"]
            else:
                result = result.get(keyword, {})

        result2 = [self._handle_units(key, value) for key, value in result.items()]

        return {key: value for key, value in result2}

    def _handle_units(self, key, value):
        for unit in self.units:
            if unit in value:
                return f"{key} ({unit})", to_number(value.split(unit)[0])

        return key, value

    def sample(self):
        return self._get_for_short("gm")

    def to_dataframe(self):
        data = []

        for filename in self.get_files():
            result = self._get_for_short(filename)

            if len(result) > 0:
                result["filename"] = short_filename(filename)
                result["name"] = self.get_name(self.get_content(filename))

                data.append(result)

        return pd.DataFrame.from_records(data)

    def get_content(self, short):
        candidates = [f for f in self.get_files() if short in f]
        if len(candidates) > 1:
            return candidates

        if len(candidates) == 0:
            return "Not Found"

        with open(candidates[0], "r") as f:
            return json.load(f)

    def get_files(self):
        files = glob.glob(f"./{self.data_path}/factbook.json-master/**/*.json")

        if len(files) == 0:
            raise Exception("No data found")

        return files

    def fetch_factbook(self):
        if not os.path.isdir(self.data_path):
            raise Exception(f"Directory {self.data_path} does not exist")

        response = requests.get(self.factbook_url)

        data = zipfile.ZipFile(BytesIO(response.content))
        for filename in data.namelist():
            data.extractall(path=self.data_path)

    def names(self):
        data = {"filenames": []}

        values = [
            "conventional long form",
            "conventional short form",
            "local long form",
            "local short form",
            "etymology",
            "former",
            "abbreviation",
        ]
        for v in values:
            data[v] = []

        for filename in self.get_files():
            data["filenames"].append(short_filename(filename))
            content = self.get_content(filename)
            government = content.get("Government", {})
            country_name = government.get("Country name", {})
            kk = list(country_name.keys())

            for v in values:
                data[v].append(get_value(country_name, v))

        return pd.DataFrame(data)

    def get_name(self, content):
        name = (
            content.get("Government", {})
            .get("Country name", {})
            .get("conventional short form", {})
            .get("text", "")
        )
        if name != "none":
            return name

        return (
            content.get("Government", {})
            .get("Country name", {})
            .get("conventional long form", {})
            .get("text", "")
        )

    def get_contents(self, filters=[], remove_empty=False):
        result = [
            {
                "short_name": short_filename(filename),
                "content": self.get_content(filename),
            }
            for filename in self.get_files()
        ]

        result = [
            {
                "short_name": x["short_name"],
                "name": self.get_name(x["content"]),
                "content": get_subentries(x["content"], filters),
            }
            for x in result
        ]

        if remove_empty:
            result = [x for x in result if len(x["content"]) > 0]

        return result
