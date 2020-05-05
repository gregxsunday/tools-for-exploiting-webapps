from modules.utility import *

def dig_wrapper(domain, outdir):
    system(f'dig +noall +answer {domain} | grep -oE "(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)" >> {outdir}/ipspace.txt')


#ipspace: dig
def ipspace(domains, outdir):
    print('[*] Discovering IP space')
    for domain in domains:
        print(f'[*] {domain}...')
        dig_wrapper(domain, outdir)
    print('[*] Finished discovering IP space')
    remove_dups('ipspace.txt', outdir)