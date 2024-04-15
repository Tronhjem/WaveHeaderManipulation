import sys
import random

def show(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    funkyChars = ""
    for x in range(7):
        funkyChars += chr(random.randint(200, 900))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)
    sys.stdout.write('[%s][%s]%s%s ... %s ... [%s]\r' % (funkyChars, bar, percents, '%', status, funkyChars))
    sys.stdout.flush()
