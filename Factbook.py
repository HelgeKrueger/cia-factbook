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

        response = requests.get(url)

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
