#!/usr/bin/env python3

import os
import sys
import time

params = dict([(i.split('=') + [''])[:2] for i in os.environ.get('QUERY_STRING', '').split('?')])
delay = float(params.get('delay', 5))

print('\nSleeping:')
for i in range(int(delay)):
    sys.stdout.write('.')
    sys.stdout.flush()
    time.sleep(1)
time.sleep(delay % 1)
print('\nDone.')