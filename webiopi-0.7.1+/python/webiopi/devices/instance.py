DEVICES  = {}
def deviceInstance(name):
    if name in DEVICES:
        return DEVICES[name]["device"]
    else:
        return None
