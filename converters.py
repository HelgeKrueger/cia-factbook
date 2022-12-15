def short_filename(filename):
    parts = filename.split("/")
    return parts[-2] + "/" + parts[-1].split(".")[0]


def get_value(data, fieldname):
    field = data.get(fieldname, {})
    return field.get("text")


def get_subentries(data, values):
    if len(values) == 0:
        return data

    return get_subentries(data.get(values[0], {}), values[1:])


def to_number(value):

    value = value.replace(",", "")

    for postfix, mult in [("million", 1e6), ("billion", 1e9)]:
        if postfix in value:
            value = value.split(postfix)[0]
            try:
                return float(value) * mult
            except:
                return None

    try:
        return float(value)
    except:
        return value
