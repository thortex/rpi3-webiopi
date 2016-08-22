def request(method="GET", path="", data=None):
    def wrapper(func):
        func.routed = True
        func.method = method
        func.path = path
        func.data = data
        return func
    return wrapper

def response(fmt="%s", contentType="text/plain"):
    def wrapper(func):
        func.format = fmt
        func.contentType = contentType
        return func
    return wrapper

def macro(func):
    func.macro = True
    return func
