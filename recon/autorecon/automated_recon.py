import argparse
from modules.utility import *
from modules.ipspace import ipspace
from modules.subdomains import subdomains
from modules.directories import directories as dirs

#ports: masscan
def ports(outdir):
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Automated recon')
    domain_group = parser.add_mutually_exclusive_group(required=True)
    domain_group.add_argument('-d', '--domain', nargs='+', required=False, help='target domain or domains separated by spaces')
    domain_group.add_argument('-dl', '--domain_list', required=False, help='file with target domains in separate lines')
    parser.add_argument('-o', '--out', default='./recon', help='output directory, ./recon by default')
    parser.add_argument('-m', '--method', required=False, default='a', help='recon method, available: [i]pspace, [p]orts, [s]ubdomains, [d]irectories, [a]ll')
    args = parser.parse_args()

    outdir = args.out
    if outdir[-1] == '/':
        outdir = outdir[:-1]

    if args.domain:
        domains = args.domain
    else:
        with open(args.domain_list, 'r') as infile:
            domains = infile.read().split()


    if 'a' in args.method or 'i' in args.method:
        ipspace(domains, outdir)
    if 'a' in args.method or 's' in args.method:
        subdomains(domains, outdir)
    if 'a' in args.method or 'd' in args.method:
        dirs(domains, outdir)