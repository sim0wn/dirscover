# -*- coding: utf-8 -*-
#Imports
from argparse import ArgumentParser, FileType, HelpFormatter
from sys import argv, exit, stdout, stderr
from requests import Request, Session, codes, exceptions
from datetime import timedelta
import os.path as path_parse
from socket import socket, AF_INET, SOCK_STREAM
from urllib.parse import urlparse

# Override "help" message
class CustomFormatter(HelpFormatter):
    def add_usage(self, usage, actions, groups, prefix=None):
        if prefix is None:
            prefix = '\033[1;36m❰\033[1;33m!\033[1;36m❱ \033[1;97mUsage\033[0;0m: '
        return super(CustomFormatter, self).add_usage(usage, actions, groups, prefix)

# Override error messages
class ArgumentParser(ArgumentParser):
    def error(self, message):
        self.exit(2, f'\033[1;36m❰\033[38:5:9m!\033[1;36m❱ \033[1;97mError\033[0;0m: {message}\n')

# Parse arguments
argparse = ArgumentParser(prog="Dirscover", usage=f"{argv[0]} <url> <wordlist>.",
        description="Tool to enumerate website directories",
        formatter_class=CustomFormatter)
argparse._positionals.title = 'Positional arguments'
argparse._optionals.title = 'Optional arguments'
argparse.add_argument("url", help="Url to fuzz", type=str)
argparse.add_argument("wordlist", help="Wordlist to use", type=FileType('r', encoding='utf-8'))
argparse.add_argument("--params", help="Optional url parameters", type=dict, dest="params")
argparse.add_argument("--method", help="HTTP method", type=str, default="GET", dest="method")
argparse.add_argument("--agent", help="Custom user-agent string/text file.", type=str, default="Dirscover v1.0", dest="agent")
argparse.add_argument("--data", help="POST request data", type=dict, dest="data")
argparse.add_argument("--cookies", help="Request cookies", type=dict, dest="cookies")
args = argparse.parse_args()

# Variables
wordlist = args.wordlist.read()
index = list()

# Check if informed method is valid
if not args.method.upper() in [ 'GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS' ]:
    exit(f'\033[1;36m❰\033[38:5:9m!\033[1;36m❱ \033[1;97mError\033[0;0m: invalid method specified (`{args.method}`).')

# Print formatted output
def printStats(response):
    template = (f'\n\r \033[38:5:15m╭─────────────────────> \033[38:5:29mDirscover \033[38:5:15m<─────────────────────╮\n'
     f'\r   \033[38:5:6m┌[ \033[38:5:3mRequest data:\n'
     f'\r   \033[38:5:6m└─┬[ \033[38:5:15mHost: \033[38:5:228m{urlparse(response.url).netloc}\n'
     f'\r   \033[38:5:6m  ├[ \033[38:5:15mRequest method: \033[38:5:228m{args.method}\n'
     f'\r   \033[38:5:6m  ├[ \033[38:5:15mUser-agent: \033[38:5:228m{response.request.headers["User-Agent"]}\n'
     f'\r  \033[38:5:6m   └[ \033[38:5:15mPing: \033[38:5:228m{response.elapsed.total_seconds()*1000:.1f}\033[38:5:15mms\n'
     f'\r   \033[38:5:6m┌[ \033[38:5:3mWordlist data:\n'
     f'\r  \033[38:5:6m └─┬[ \033[38:5:15mFile: \033[38:5:228m{args.wordlist.name}\n'
     f'\r   \033[38:5:6m  ├[ \033[38:5:15mLoaded: \033[38:5:228m{len(wordlist)} \033[38:5:15mwords\n'
     f'\r     \033[38:5:6m└[ \033[38:5:15mEstimated time: \033[38:5:228m{(response.elapsed.total_seconds()*(len(wordlist) - wordlist.index(directory)))/60:.0f} minutes\n'
     f'\r   \033[38:5:6m┌[ \033[38:5:3mStatus:\n'
     f'\r \033[38:5:6m  └─┬[ \033[38:5:15mTesting: \033[38:5:228m{urlparse(response.url).path}\n'
     f'\r     \033[38:5:6m└[ \033[38:5:15mRemaining: \033[38:5:228m{(len(wordlist) - wordlist.index(directory)) - 1} \033[38:5:15mwords\n'
     f'\r')
    stdout.write('\n'*len(template.split('\n')[1:]))
    stdout.write(f'\033[{str(len(template.split(chr(10))[1:]))}F\033[0J ')
    for line in template.split('\n')[1:]:
        stdout.write(line)
        stdout.write(u'\033[1E')
    if response.status_code == codes.ok:
        index.append({ 'host': response.url, 'code':response.status_code })
    for discovered in index:
        stdout.write(f'\r   [+] {discovered["host"]} (Code: {discovered["code"]})\n')
    stdout.write(' ╰───────────────────────────────────────────────────────╯')
    stdout.write(f'\033[{str(++len(template.split(chr(10))[1:]) + len(index))}F')
    stdout.flush()

# Enumerate
for directory in wordlist:
    try:
        if path_parse.isfile(args.agent):
            with open(args.agent) as agent_list: user_agent = { 'User-Agent':choice(agent_list.readlines()) }
        else:
            user_agent = { 'User-Agent': args.agent }
        response = Session().request(
            method=args.method.upper(), 
            url=f'{args.url}/{directory}',
            headers=user_agent,
            data=args.data,
            params=args.params,
            cookies=args.cookies)
    except (exceptions.InvalidSchema, exceptions.MissingSchema):
        print('\033[1;36m❰\033[38:5:9m!\033[1;36m❱ \033[1;97mError\033[0;0m: invalid url structure (missing schema).')
        exit(1)
    except KeyboardInterrupt:
        stdout.write(f'\033[{16+len(index)}B'
                f'\r ╰───────────────────────────────────────────────────────╯\n'
                f'\r\033[1;36m❰\033[38:5:9m!\033[1;36m❱ \033[1;97mError\033[0;0m: execution interrupted by user (`<CTRL+C>`).\n')
        exit(1)
    printStats(response)
