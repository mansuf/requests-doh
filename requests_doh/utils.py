import socket
import ipaddress

def fix_resolved_dns(answers, port, family, _type):
    fixed_dns = set()
    raw_domains = set()
    for answer in answers:
        err = False
        try:
            ipaddress.ip_address(answer)
        except ValueError:
            # An domain detected
            # query it using socket.getaddrinfo
            err = True
        
        if err:
            raw_domains.add(answer)
            socket_answers = socket.getaddrinfo(answer, port, family, _type)
            for socket_answer in socket_answers:
                af, socktype, proto, canonname, sa = socket_answer
                fixed_dns.add(sa[0])

    # Remove raw domains
    for domain in raw_domains:
        answers.discard(domain)

    answers.update(fixed_dns)
