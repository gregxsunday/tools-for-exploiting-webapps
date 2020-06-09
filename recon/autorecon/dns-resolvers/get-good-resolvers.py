import requests

resp = requests.get('https://public-dns.info/nameservers.csv')
resolvers = resp.text.split('\n')

with open('good-resolvers.txt', 'w') as outfile:
    for res in resolvers:
        try:
            res = res.split(',')
            if ':' not in res[0] and float(res[-3]) > 0.95:
                print(res[0], file=outfile)
        except Exception:
            pass
