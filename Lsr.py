import time
import argparse
from router import Router
import router

# globals
UPDATE_INTERVAL = 1
ROUTE_UPDATE_INTERVAL = 15
NODE_FAILURE_PATIENT = 3


parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('config', type=str, help='configuration txt file')

args = parser.parse_args()

f = open(args.config)

router_name, router_port = f.readline().split()
router_port = int(router_port)

N = int(f.readline())

neighbours = []
for _ in range(N):
    other_name, cost, port = f.readline().split()
    cost = float(cost)
    port = int(port)

    neighbour = (other_name, cost, port)
    neighbours.append(neighbour)

router = Router(router_name, neighbours, router_port)

counter = 0
failure_num = 0
fail_mode = False
while True:
    time.sleep(1)
    counter += 1

    router.broadcast_link_state_packets()
    failure_num_new = router.check_node_failure(NODE_FAILURE_PATIENT)

    # failure node increased, wait for synchronization
    if failure_num_new > failure_num:
        failure_num = failure_num_new
        router.report_shortest_path()
        counter = 0
        fail_mode = True
    elif failure_num_new < failure_num:
        failure_num = failure_num_new

    if counter == 2 * ROUTE_UPDATE_INTERVAL and fail_mode:
        router.report_shortest_path()
        counter = 0
        fail_mode = False

    if counter == ROUTE_UPDATE_INTERVAL and not fail_mode:
        router.report_shortest_path()
        counter = 0
