def short_filename(filename):
    parts = filename.split("/")
    return parts[-2] + "/" + parts[-1].split(".")[0]


def get_value(data, fieldname):
    field = data.get(fieldname, {})
    return field.get("text")
