from modules.utility import *

def wayback_wrapper(domain, outdir):
    system(f'curl -s "http://web.archive.org/cdx/search/cdx?url={domain}/*&output=text&fl=original&collapse=urlkey" >> {outdir}/directories.txt')


def directories(domains, outdir):
    print('[*] Discovering paths from wayback')
    for domain in domains:
        print(f'[*] {domain}...')
        wayback_wrapper(domain, outdir)
    map_dirname('directories.txt', outdir)
    remove_dups('directories.txt', outdir)