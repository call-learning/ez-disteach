# -*- coding: utf-8 -*-

import random
import string

def generate_uid():
    allletters = string.ascii_lowercase
    return ''.join(random.choice(allletters) for i in range(10))
