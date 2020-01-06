import string
import subprocess
import time

for router_name in string.ascii_uppercase[: 6]:
    # leave some space for ordered output
    # not guaranteed though
    time.sleep(1)
    filename = "mock_configs/config{}.txt".format(router_name)
    # only print output from A
    if router_name == 'A':
        subprocess.Popen('run Lsr.py {}'.format(filename))
    else:
        # prevent output
        subprocess.Popen('run Lsr.py {}'.format(filename), stdout=subprocess.PIPE)