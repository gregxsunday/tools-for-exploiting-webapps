from modules.utility import *
import requests
import json
import os
import subprocess
from time import sleep

def amass_wrapper(domains, outdir):
    domains_str = ','.join(domains)
    cmd = f'amass enum -d {domains_str} | tee {outdir}/amass.out'
    print('[*]',cmd)
    system(cmd)
    system(f'cat {outdir}/amass.out >> {outdir}/subdomains.txt')
    remove_dups('subdomains.txt', outdir)


def virustotal_wrapper(domains, outdir):
    print('[*] Virustotal')
    # virustotal needs an api key
    virustotal_key = os.environ['VIRUSTOTAL_KEY']
    for index, domain in enumerate(domains):
        resp = requests.get(f'https://www.virustotal.com/vtapi/v2/domain/report?apikey={virustotal_key}&domain={domain}')
        try:
            resp_json = json.loads(resp.text)
            subdomains = resp_json['subdomains']
            with open(f'{outdir}/virustotal.out', 'a') as outfile:
                outfile.write('\n' + '\n'.join(subdomains))
                print('\n'.join(subdomains))
        except (KeyError, json.decoder.JSONDecodeError) as e:
            print(resp.text)

        # vt has 4 req/min
        if index % 4 == 3:
            sleep(60)
    system(f'cat {outdir}/virustotal.out >> {outdir}/subdomains.txt')
    remove_dups('subdomains.txt', outdir)


def filter_dns_wildcard(domains):
    # this function is used to generate input to massdns
    # the difference between this and the script is
    # that this removes the main domain as well
    # whereas the script removes only the higher level subdomains
    domains_without_wildcard = []
    for domain in domains:
        res = subprocess.check_output(f'dig +short *.{domain}'.split())
        if len(res) == 0:
            domains_without_wildcard.append(domain)
    return domains_without_wildcard


def massdns_wrapper(outdir, massdns_base, all_txt):
    # filtering the wildcard subdomains
    cmd = f'sh {os.path.dirname(os.path.realpath(__file__))}/../scripts/filter_dns_wildcards.sh {outdir}/provided_domains.txt'
    system(cmd)
    with open(f'{outdir}/domains_wo_wildcards.txt', 'r') as infile:
        domains = infile.read().split()
    # removing the subdomains which has the wildcard subdomains from the massdns input
    domains = filter_dns_wildcard(domains)
    domains_str = ' '.join(domains)

    # generating brute list and passing it to the massdns
    dns_resolver_path = os.path.dirname(os.path.realpath(__file__)) + '/../dns-resolvers/good-resolvers.txt'
    cmd = f'python2.7 {massdns_base}/scripts/subbrute.py {all_txt} {domains_str} | {massdns_base}/bin/massdns -r {dns_resolver_path} -t A -o S -q -w {outdir}/massdns.out'
    print('[*]', cmd)
    system(cmd)

    # parsing massdns output
    cmd = f'cat {outdir}/massdns.out' + r"| awk '{print $1}' | sed 's/.$//' | awk -F, '{print $NF}' | sort -u >> " + f'{outdir}/subdomains.txt'
    system(cmd)
    remove_dups('subdomains.txt', outdir)


def altdns_wrapper(outdir, words_txt, massdns_base):
    # altdns wordlist has to be prepared without wildcard domains
    cmd = f'sh {os.path.dirname(os.path.realpath(__file__))}/../scripts/filter_dns_wildcards.sh {outdir}/subdomains.txt'
    system(cmd)

    system(f'cat {outdir}/domains_wo_wildcards.txt > {outdir}/altdns.in')
    # altdns generates permutaions based on found ones
    cmd = f'python2.7 -m altdns -i {outdir}/altdns.in -o {outdir}/altdns.tmp -w {words_txt}'
    print('[*]', cmd)
    system(cmd)

    # also generate permutation with dnsgen
    system(f'cat {outdir}/domains_wo_wildcards.txt > {outdir}/dnsgen.in')
    cmd = f'cat {outdir}/dnsgen.in | dnsgen - >> altdns.tmp'
    print('[*]', cmd)
    system(cmd)
    remove_dups('altdns.tmp', outdir)

    # passing the generated list to massdns to resolve
    dns_resolver_path = os.path.dirname(os.path.realpath(__file__)) + '/../dns-resolvers/good-resolvers.txt'
    cmd = f'{massdns_base}/bin/massdns -r {dns_resolver_path} -t A -o S -q -w {outdir}/altdns-massdns.out {outdir}/altdns.tmp'
    print('[*]', cmd)
    system(cmd)
    cmd = f'cat {outdir}/altdns-massdns.out' + r"| awk '{print $1}' | sed 's/.$//' | awk -F, '{print $NF}' | sort -u >> " + f'{outdir}/subdomains.txt'
    system(cmd)
    system(f'rm {outdir}/altdns.tmp')
    remove_dups('subdomains.txt', outdir)

def aquatone_wrapper(outdir):
    # screenshoting
    system(f'cat {outdir}/subdomains.txt | aquatone -http-timeout 30000 -out {outdir}/aquatone.d -ports 80,443')

#subdomains
# 1. amass
# 2. virustotal
# 3. (nslookup wildcards before) massdns
# 4. altdns -> massdns
# 5. auatone screenshots
def subdomains(domains, outdir):
    system('mkdir -p {}'.format(outdir))

    with open(f'{outdir}/provided_domains.txt', 'a') as outfile:
        outfile.write('\n'.join(domains) + '\n')
        remove_dups('provided_domains.txt', outdir)


    config_path = os.path.dirname(os.path.realpath(__file__)) + '/../config.json'
    with open(config_path, 'r') as infile:
        config = infile.read()

    config = json.loads(config)
    massdns_base = config['massdns']
    all_txt = config['all.txt']
    words_txt = config['altdns-words.txt']


    print('[*] Discovering subdomains')
    # uses multiple sources of domains
    amass_wrapper(domains, outdir)
    # more of a backup to amass (which is prone to run out of memory)
    virustotal_wrapper(domains, outdir)
    # basic bruteforce
    massdns_wrapper(outdir, massdns_base, all_txt)
    # generating the permutations basen on found subdomains and bruteforcing again via massdns
    altdns_wrapper(outdir, words_txt, massdns_base)
    # merging
    system(f'cat {outdir}/virustotal.out >> {outdir}/subdomains.txt')
    system(f'cat {outdir}/amass.out >> {outdir}/subdomains.txt')

    # removing wildcard dns subdomains (but leaving the main one)
    cmd = f'sh {os.path.dirname(os.path.realpath(__file__))}/../scripts/filter_dns_wildcards.sh {outdir}/subdomains.txt'
    system(cmd)
    system(f'mv {outdir}/domains_wo_wildcards.txt {outdir}/subdomains.txt')

    # add results from amass and vt again, just in case their results were filtered by wildcard domain filter
    system(f'cat {outdir}/virustotal.out >> {outdir}/subdomains.txt')
    system(f'cat {outdir}/amass.out >> {outdir}/subdomains.txt')
    remove_dups('subdomains.txt', outdir)
    
    # screenshoting
    aquatone_wrapper(outdir)

