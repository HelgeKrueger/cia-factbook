from argparse import ArgumentParser
import os

from rich import print
from rich.table import Table

from ciafactbook import CiaFactbook


def format_entry(value):
    value = str(value)
    if value == "nan":
        return ""
    return value


def main():
    factbook = CiaFactbook()
    if not os.path.isdir("data/factbook.json-master"):
        factbook.fetch_factbook()

    parser = ArgumentParser()
    parser.add_argument("keyword", nargs="*")
    parser.add_argument("--keys", action="store_true")
    parser.add_argument("--table", action="store_true")
    parser.add_argument("--flatten", action="store_true")
    parser.add_argument("--units", help="Units separated by , e.g. 'kW,kWh")

    args = parser.parse_args()

    for key in args.keyword:
        factbook = factbook.add_keyword(key)

    if args.units:
        factbook = factbook.set_units(args.units.split(","))

    if args.flatten:
        factbook.add_keyword("flatten")

    if args.table:
        df = factbook.to_dataframe()
        columns = df.columns
        columns = [c for c in columns if "note" not in c and "text" not in c]
        table = Table()
        for col in columns:
            table.add_column(col)

        for _, row in df.iterrows():
            table.add_row(*[format_entry(row[c]) for c in columns])

        print(table)

    elif args.keys:
        print(factbook.sample().keys())
    else:
        print(factbook.sample())


if __name__ == "__main__":
    main()
