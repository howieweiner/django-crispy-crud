def remove_empty_url_params(url_params: str) -> str:
    params = url_params.split("&")
    if len(params) == 1 and params[0] == "":
        return ""

    new_params = []
    for kv in params:
        k, v = kv.split("=")
        if v != "":
            new_params.append(kv)

    return "&".join(new_params)
