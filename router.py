import socket
from socketserver import BaseRequestHandler, UDPServer

from shortest_path import dijkstra
import threading

import json
import time

DEBUG = False

class Server(threading.Thread):
    class BroadcastHandler(BaseRequestHandler):
        def handle(self):
            # Get message and client socket
            msg, sock = self.request

            if DEBUG:
                print("Router {} received packet: {}".format(self.server.router.name, msg.decode("ascii")))

            msg = json.loads(msg.decode("ascii"))
            sender = msg["sender"]
            timestamp = msg["timestamp"]

            if sender in self.server.router.dead_nodes:
                self.server.router.dead_nodes.remove(sender)

            need_broadcast = False
            if sender not in self.server.router.sent.keys():
                need_broadcast = True
            else:
                last_timestamp = self.server.router.sent[sender]
                if last_timestamp < timestamp:
                    need_broadcast = True

            if need_broadcast:
                self.server.router.router_lock.acquire()

                self.server.router.update_edges(sender, msg["neighbours"])
                self.server.router.sent[sender] = timestamp

                if DEBUG:
                    print("{} will relay for {}".format(
                        self.server.router.name, sender))

                # broadcast to neighbours, but don't send
                # it back to sender, that's a waste
                self.server.router.broadcast_packets(msg, exception={sender})

                self.server.router.router_lock.release()
            else:
                if DEBUG:
                    print("{} will not relay for {}".format(
                        self.server.router.name, sender))

            # resp = "Hello " + msg.decode('ascii')
            # sock.sendto(resp.encode('ascii'), self.client_address)

    def __init__(self, address, port, router):
        threading.Thread.__init__(self)
        self.port = port
        self.udp_server = UDPServer((address, port), Server.BroadcastHandler)
        self.udp_server.router = router

    def run(self):
        self.udp_server.serve_forever()

class Router(object):
    '''
    router class
    '''

    def __init__(self, name, neighbours, port, address='127.0.0.1'):
        self.name = name
        self.neighbours = neighbours

        self.edges = []
        for other_name, cost, _ in neighbours:
            self.edges.append((name, other_name, cost))

        self.router_lock = threading.Lock()

        self.port = port
        self.start_server(address, port)

        self.address = address

        self.sent = {}
        # nerver relay for oneself
        self.sent[self.name] = float("inf")

        self.dead_nodes = set()

    def start_server(self, address, port):
        self.server = Server(address, port, self)
        self.server.setDaemon(True)
        self.server.start()

    def broadcast_link_state_packets(self):
        msg = dict()
        msg["sender"] = self.name
        msg["neighbours"] = list(filter(lambda x: x[0] not in self.dead_nodes, self.neighbours))
        msg["timestamp"] = time.time()
        self.broadcast_packets(msg)

    def broadcast_packets(self, packets_msg, exception={}):
        json_msg = json.dumps(packets_msg)
        c = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        for other_name, cost, port in self.neighbours:
            if other_name in exception:
                continue

            if DEBUG:
                print("Router {} sending: {} to {}".format(self.name, json_msg, other_name))

            c.sendto(json_msg.encode('ascii'), (self.address, port))

    def update_edges(self, sender, neighbours):
        if sender in self.dead_nodes:
            return

        if DEBUG:
            print("{} updating: {}".format(self.name, neighbours))

        for other_name, cost, _ in neighbours:
            if ((sender, other_name, cost) not in self.edges) and (other_name not in self.dead_nodes):
                self.edges.append((sender, other_name, cost))

    def report_shortest_path(self):
        targets = set()
        for f, t, _ in self.edges:
            targets.add(f)
            targets.add(t)

        targets.remove(self.name)

        print("I am Router {}".format(self.name))

        for t in targets:
            dist, path = dijkstra(self.edges, self.name, t)
            print("Least cost path to router {}: {} and the cost is {}".format(t, ''.join(path), round(dist, 1)))

    def check_node_failure(self, patient):
        now = time.time()
        for k, v in self.sent.items():
            if now - v > patient:
                self.dead_nodes.add(k)

        self.edges = list(filter(lambda x: x[0] not in self.dead_nodes and x[1] not in self.dead_nodes, self.edges))

        return len(self.dead_nodes)
