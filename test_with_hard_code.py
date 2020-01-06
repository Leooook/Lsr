from router import Router
import router

from shortest_path import dijkstra

router.DEBUG = True

r1 = Router("A", [('B', 6.5, 5009), ('C', 2.2, 5010)], 5008)
r2 = Router("B", [('A', 6.5, 5008), ('C', 3.5, 5010)], 5009)
r3 = Router("C", [('A', 2.2, 5008), ('B', 3.5, 5009), ('D', 1.0, 5011)], 5010)
r4 = Router("D", [('C', 1.0, 5010)], 5011)

'''
A
|──2.2──╮
6.5     C ──1.0── D
|──3.5──╯
B
'''

r1.broadcast_link_state_packets()
r2.broadcast_link_state_packets()
r3.broadcast_link_state_packets()
r4.broadcast_link_state_packets()

# let deamon theads flood...
import time
time.sleep(1)

print('-' * 50)

# check whether new packets are relayed
r1.broadcast_link_state_packets()

# let deamon theads flood...
import time
time.sleep(1)

print(r1.edges)

r1.report_shortest_path()
