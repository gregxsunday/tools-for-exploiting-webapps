# DNS server for DNS rebinding attacks 
DNS server for DNS rebinding attacks implemented in Python. The base DNS server part is cloned from https://gist.github.com/andreif/6069838 which has Apache 2.0 license.
## Typical use:
```
python3 dnsrebinding.py -d the.subdomain.mydomain.tld -i 1.2.3.4 169.254.169.254
```
**Use sudo in case of permission denied to run on port 53.**


Such server will run on port 53 and respond in turn to A DNS queries for ```the.subdomain.mydomain.tld``` with 1.2.3.4 or 169.254.169.254. If you want to start with the other IP address, restart the server with another order or simply *shift* the counter with manual DNS query.
Sample output of this example use would be:
```
$ dig @localhost +short the.subdomain.mydomain.tld
1.2.3.4

$ dig @localhost +short the.subdomain.mydomain.tld
169.254.169.254

$ dig @localhost +short the.subdomain.mydomain.tld
1.2.3.4

$ dig @localhost +short the.subdomain.mydomain.tld
169.254.169.254

$ dig @localhost +short the.subdomain.mydomain.tld
1.2.3.4
...
```

## Making the server visible in the web
To perform the DNS rebinding attack the server must be visible in the web. There are 2 prerequisites:
1. server with public IP address
2. having registered domain

### Testing the server
If you have a server with a public ip address, let's say 5.6.7.8, you can test the server using dig.
Run on the server:
```
python3 dnsrebinding.py -d the.subdomain.mydomain.tld -i 1.2.3.4 169.254.169.254
```
You don't need to have a registered domain in this step.
Then test your server with 
```
dig @5.6.7.8 the.subdomain.mydomain.tld
``` 

### Testing the domain setup
The next part is setting up your domain NS records to point into your server. I have used Namecheap *.me* domain using free 1 year domain registration from [Github Education Pack](https://education.github.com/pack). I also use this domain to access my VPS on DigitalOcean, so I don't want to break the resolution of mydomain.me, but instead work with the subdomains.
I will provide exact steps taken to set up the nameservers.
1. ```Namecheap > Domain List > Manage > Domain > Nameservers > Custom DNS```
    
    Here I just have standard DigitalOcean nameservers:
    ```
    ns1.digitalocean.com
    ns2.digitalocean.com
    ns3.digitalocean.com
    ```

2. ```DigitalOcean > Networking > Manage Domain```
    
    And here I have two records:
    ```
    dnsrebinding.mydomain.me NS ns1.mydomain.me
    ```
    And the ns1 also needs the A record
    ```
    ns1.mydomain.me A 5.6.7.8
    ```
    Where 5.6.7.8 is my public IP address. 

In such setup, I can run my DNS server with an arbitrary subdomain of `dnsrebinding.mydomain.me`.

To test this part, use dig with `+trace` option. When tracing is enabled, dig makes iterative queries to resolve the name being looked up. It will allow to verify the setup immidiately, as the synchronization of the DNS servers make take up to 48 hours and may cause false negatives.

So run the script on your server with:
```
python3 dnsrebinding.py -d test.dnsrebinding.mydomain.me -i 1.2.3.4 169.254.169.254
```
The IP addresses here do not matter much.
Test the server with dig:
```
dig +trace test.dnsrebinding.mydomain.me
```
If everything works fine, at the end of the output there should be something like:
```
test.dnsrebinding.mydomain.me. 0 IN A 169.254.169.254
;; Received 85 bytes from 5.6.7.8#53(ns1.mydomain.me) in 59 ms
```