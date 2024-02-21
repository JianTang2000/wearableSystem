import time
import threading
import sys
import hiwonder.ActionGroupControl as AGC

print('''
Usage:
    python3 ActionGroupControlDemo.py
''')

AGC.runActionGroup('stand', times=1, with_stand=True)
