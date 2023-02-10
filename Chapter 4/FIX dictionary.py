from functools import reduce

fixdict = {}
fixdict["start"] = "8"
fixdict["body_len"] = "9"
fixdict["checksum"] = "10"
fixdict["msg_type"] = "35"

exceptions = ["8", "9", "10"]


def compose_message(fix_dictionary, fix_exceptions, **kwargs):
    msg = ""
    for arg in kwargs:
        if fix_dictionary[arg] not in fix_exceptions:
            msg += fix_dictionary[arg] + "=" + kwargs[arg] + "\001"
    msg = fix_dictionary["body_len"] + "=" + str(len(msg)) + msg
    msg = fix_dictionary["start"] + "=" + "FIX.4.4" + msg

    checksum = reduce(lambda x, y: x + y, list(map(ord, msg))) % 256
    msg += fix_dictionary["checksum"] + "=" + str(checksum)
    return msg


message = compose_message(fixdict, exceptions, msg_type="5")
print(message)
