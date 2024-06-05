import json


def json_uni_return(flag: bool, data: any, message=""):
    return {"flag": flag, "data": data, "message": message}
