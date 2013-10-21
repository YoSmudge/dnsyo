"""
Parse command line options


The MIT License (MIT)

Copyright (c) 2013 Sam Rudge (sam@codesam.co.uk)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""


from argparse import ArgumentParser
import logging
import dnsyo
import sys


def run():
    """
    Parse arguments and pass them into the main class

    This is invoked from the `dnsyo` script
    """

    #List all the possible options, defaults and help
    options = [
        ['resolvlist:l', 'store',
         'Location of the yaml resolvers list to download (http/https)',
         'https://raw.github.com/samarudge/dnsyo/master/resolver-list.yml'],
        ['verbose:v', 'store_true', 'Extended debug info'],
        ['simple:s', 'store_true',
         'Simple output mode (good for UNIX parsing)'],
        ['extended:x', 'store_true',
         'Extended output mode including server addresses'],
        ['threads:t', 'store', 'Number of worker threads to use', 100],
        ['servers:q', 'store',
         'Maximum number of servers to query (or ALL)', 500],
        ['country:c', 'store',
         'Query servers by two letter country code']
    ]

    #Create an argparse
    p = ArgumentParser(
        usage="%(prog)s [options] domain [type]",
        description="Query lots of DNS servers and colate the results",
        epilog="https://github.com/samarudge/dnsyo"
    )

    #Load the options
    for opt in options:
        #Split them into name and short flag
        name, flag = opt[0].split(':')

        #Set a default
        default = opt[3] if len(opt) > 3 else None

        #Add it to the parser object
        p.add_argument(
            '--{0}'.format(name),
            '-{0}'.format(flag),
            dest=name,
            action=opt[1],
            help=opt[2],
            default=default
        )

    #Add the default positional arguments
    p.add_argument('domain', action="store",
                   help="Domain to query", default=None)
    p.add_argument('type', action="store",
                   help='Record type (A, CNAME, MX, etc.)',
                   default="A", nargs="?")

    opts = p.parse_args()

    #Setup logging
    if len(logging.root.handlers) == 0:  # Only if there aren't any loggers
        if opts.verbose:
            #If the verbose option is passed, set debug output
            logging.basicConfig(
                level=logging.DEBUG
            )
        elif opts.simple:
            #If the simple option is passed only output warnings and errors
            logging.basicConfig(
                level=logging.WARNING
            )
        else:
            #Otherwise just info
            logging.basicConfig(
                level=logging.INFO
            )

        logging.debug("Debug logging enabled")

    #Prepare the lookup request
    try:
        lookup = dnsyo.lookup(
            domain=opts.domain,
            recordType=opts.type,
            listLocation=opts.resolvlist,
            maxWorkers=opts.threads,
            maxServers=opts.servers,
            country=opts.country
        )
    except AssertionError as e:
        #Some arguments were not valid, show the error and exit
        p.error(e)
        sys.exit(3)

    #Update the nameserver list, if needed
    lookup.updateList()

    #Filter the list to only the servers we want
    lookup.prepareList()

    try:
        #Query the servers, display progress if not simple output
        lookup.query(
            progress=not opts.simple
        )
    except ValueError as e:
        p.error(e)
        sys.exit(3)

    #Output the relevant result format
    if opts.simple:
        lookup.outputSimple()
    else:
        lookup.outputStandard(opts.extended)

if __name__ == '__main__':
    run()
