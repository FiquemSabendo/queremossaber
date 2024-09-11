import random
import string


def generate_protocol(length=8):
    alphanumeric = string.ascii_uppercase + string.digits
    return "".join(random.choices(alphanumeric, k=length))
