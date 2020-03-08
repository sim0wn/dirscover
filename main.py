from argparse import ArgumentParser, FileType, HelpFormatter
from sys import argv, exit, stdout
from requests import get, post, put, delete, head, options, codes, exceptions
from time import sleep

class CapitalisedHelpFormatter(HelpFormatter):
    def add_usage(self, usage, actions, groups, prefix=None):
        if prefix is None:
            prefix = '\033[1;36m❰\033[1;33m!\033[1;36m❱ \033[1;97mUsage\033[0;0m: '
        return super(CapitalisedHelpFormatter, self).add_usage(usage, actions, groups, prefix)

argparse = ArgumentParser(prog="Dirscover", usage="{} <url> <wordlist>".format(argv[0]),
        description="Tool to enumerate website directories",
        formatter_class=CapitalisedHelpFormatter)
argparse._positionals.title = 'Positional arguments'
argparse._optionals.title = 'Optional arguments'
argparse.add_argument("url", help="Url to fuzz", type=str)
argparse.add_argument("wordlist", help="Wordlist to use", type=FileType('r', encoding='utf-8'))
argparse.add_argument("--params", help="Optional url parameters", type=dict, dest="params")
argparse.add_argument("--method", help="HTTP method", type=str, default="GET", dest="method")
argparse.add_argument("--agent", help="Custom user-agent (fill with \"random\" to randomize)", type=str, default="%(prog)s v1.0", dest="agent")
argparse.add_argument("--data", help="POST request data", type=dict, dest="data")
argparse.add_argument("--cookies", help="Request cookies", type=dict, dest="cookies")
args = argparse.parse_args()

HTTP_METHODS = [ 'GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS' ]

if not args.method in HTTP_METHODS:
    print('Invalid request method')

def customAgent(agent):
    if (agent != "random"):
        return { "User-Agent": agent }
    else:
        try:
            with open("/usr/share/wordlist/Dirscover/user-agent.txt") as wordlist:
                return { "User-Agent": choice(wordlist.readlines()) }
        except:
            print("Couldn\'t open \"/usr/share/wordlist/Dirscover/user-agent.txt\"")

wordlist = args.wordlist.read().split()
discovered = []

def printStats(request, directory):
    template = """
     \r «˹¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯ Dirscover  ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯˺»
     \r   ┌[Request data:
     \r   └─┬[Host: {host}
     \r     ├[HTTP method: {method}
     \r     ├[User-agent: {agent}
     \r     └[Ping: {ping:.1f}ms
     \r   ┌[Wordlist data:
     \r   └─┬[File: {filename}
     \r     ├[Loaded: {wc} words
     \r     └[Estimated time: {etime}
     \r   ┌[Status:
     \r   └─┬[Testing: {testing}
     \r     └[Remaining: {remaining} words
     \r
     \r{discovered}
               """.format(host=args.url, method=request.request.method.upper(), agent=request.request.headers['User-Agent'],
                       ping=request.elapsed.total_seconds()*1000, filename=args.wordlist.name, wc=len(wordlist), etime=20, testing=directory,
                       remaining=len(wordlist) - wordlist.index(directory), discovered=discovered)
    length = len(template.split('\n')[1:])
    stdout.write('\n'*length)
    stdout.write(u'\u001b[1000D' + u'\u001b[' + str(length) + 'A')
    for line in template.split('\n')[1:]:
        stdout.write('\r' + line)
        stdout.write(u'\u001b[1B')
        stdout.flush()
    stdout.write(u'\u001b[1000D' + u'\u001b[' + str(length) + 'A')
    stdout.flush()

    if request.status_code == codes.ok:
        discovered.append("\r» {} (Code: {})".format(args.url.strip() + path.strip(), request.status_code))

for directory in wordlist:
    path = '{}/{}'.format(args.url, directory)
    try:
        request = eval("{}(path, params=args.params, headers=customAgent(args.agent), data=args.data, cookies=args.cookies)".format(args.method.lower()))
    except exceptions.MissingSchema:
        print("\033[1;36m❰\033[1;31m!\033[1;36m❱ \033[1;97mInvalid url '\033[33m{}\033[1;97m' (missing schema).\033[0;0m".format(args.url.strip()))
        exit(1)

    printStats(request, directory)

    if request.status_code == codes.ok:
        print("\t» {} (Code: {})".format(args.url.strip() + path.strip(), request.status_code))
