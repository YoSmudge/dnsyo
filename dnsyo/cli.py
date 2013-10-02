from argparse import ArgumentParser
import logging
import dnsyo
import sys

def run():
    """
    Do all the argparse stuff from the dnsyo command
    """
    
    options = [
        ['resolvlist:l','store','Location of the yaml resolvers list', 'https://github.com/samarudge/dnsyo/raw/resolver-list.yml'],
        ['verbose:v','store_true','Extended debug info'],
        ['simple:s','store_true','Simple output mode (good for UNIX parsing)'],
        ['extended:x','store_true','Extended output mode including server addresses']
    ]
    
    p = ArgumentParser(
        usage="%(prog)s [options] domain [type]",
        description="Query lots of DNS servers and colate the results",
        epilog="https://github.com/samarudge/dnsyo"
    )
    
    #Load the options
    for opt in options:
        name,flag = opt[0].split(':')
        default = opt[3] if len(opt) > 3 else None
        
        p.add_argument(
            '--{0}'.format(name),
            '-{0}'.format(flag),
            dest=name,
            action=opt[1],
            help=opt[2],
            default=default
        )
    
    p.add_argument('domain',action="store",help="Domain to query", default=None)
    p.add_argument('type',action="store",help='Record type (A, CNAME, MX, etc.)', default="A", nargs="?")
    
    opts = p.parse_args()
    
    #Setup logging
    if len(logging.root.handlers) == 0:
        if opts.verbose:
            logging.basicConfig(
                level=logging.DEBUG
            )
        elif opts.simple:
            logging.basicConfig(
                level=logging.WARNING
            )
        else:
            logging.basicConfig(
                level=logging.INFO
            )
        
        logging.debug("Debug logging enabled")
    
    #Prepare the lookup request
    try:
        lookup = dnsyo.lookup(
            domain=opts.domain,
            recordType=opts.type,
            listLocation=opts.resolvlist
        )
    except AssertionError as e:
        p.error(e)
        sys.exit(3)
    except ValueError:
        p.error("Number of servers to query should be int or 'ALL'")
        sys.exit(3)
    
    #Update the list, if needed
    lookup.updateList()
    
    #Query the servers, display progress if not nagios or simple output
    lookup.query(
        progress=not opts.simple
    )
    
    #Output the relevant result format
    if opts.simple:
        lookup.outputSimple()
    else:
        lookup.outputStandard(opts.extended)
    
if __name__ == '__main__':
    run()