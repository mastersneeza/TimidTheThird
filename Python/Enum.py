__iota_counter = 0
# Loose enum implementation, so I don't have to use a qualified name like Enum.EnumVal0, Enum.EnumVal1, e.t.c.
def iota(reset = False, value : int = 0) -> int:
    global __iota_counter
    __iota_counter += 1
    if reset: __iota_counter = value
    return __iota_counter
