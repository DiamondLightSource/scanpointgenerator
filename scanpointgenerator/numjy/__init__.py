import sys
if sys.hexversion < 0x02040000:
    raise 'Must use python of at least version 2.4'

import os

'''
We import jcore, jymaths and jycomparisons only on jython
'''
if os.name == 'java':
    from jycore import *
    from jymaths import *
    from jycomparisons import *
