from os import system
from os.path import dirname as dirname

def remove_dups(filename, outdir):
    system(f'sort -u {outdir}/{filename} > {outdir}/{filename}.tmp')
    system(f'cat {outdir}/{filename}.tmp > {outdir}/{filename}')
    system(f'rm {outdir}/{filename}.tmp')


def map_dirname(filename, outdir):
    with open(f'{outdir}/{filename}', 'r') as infile:
        filepaths = infile.read().split()

    dirs = set(map(dirname, filepaths))

    print('\n'.join(dirs))