"""
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

import os
import requests
import yaml
import time
import logging
import threading
import random
import sys
from datetime import datetime
import dns.resolver
import itertools
import json

class lookup(object):
    """
    Main DNSYO class, this does pretty much everything
    If you want to use it in your own scripts external to the CLI just look through the docstrings
    
    @cvar   lookupRecordTypes:      Types of DNS records supported, feel free to add more
    @cvar   updateListEvery:        How often to update the resolver list
    @cvar   serverList:             Resolvers to query
    @cvar   results:                Store the results from each server
    @cvar   resultsColated:         The processed results
    """
    
    #I'd like to support IPV6 but my local network doesn't so I can't test
    #If you can add support for AAAA records and test it I will give you a hypothetical cookie
    lookupRecordTypes = ['A','CNAME','MX','NS','PTR','SOA','SPF','SRV','TXT']
    
    #Update the resolver list every 14 days
    updateListEvery = 60*60*24*14
    
    serverList = []
    
    results = []
    resultsColated = []
    
    def __init__(self,
        domain,
        recordType,
        listLocation,
        listLocal='/tmp/dnsyo-resovers-list-{0}.yaml'.format(os.getuid()),
        expected=None,
        maxServers='ALL',
        maxWorkers=50):
        """
        Get everything setup and ready to go
        
        Here we check all of the options and make sure they're valid
        Then the rest of the script can just run without worrying about validation (hopefully)
        
        @param  domain:         Domain to query
        @param  recordType:     Type of record to query for
        @param  listLocation:   HTTP address of the resolvers list
        @param  listLocal:      Local file where resolver list should be stored, by default in /tmp and use the user ID to avoid conflicts
        @param  expected:       Not used yet
        @param  maxServers:     Limit number of servers to query
        @param  maxWorkers:     Maximum number of threads
        
        @type   domain:         str
        @type   recordType:     str
        @type   listLocation:   str (HTTP address)
        @type   listLocal:      str (File path)
        @type   maxServers:     int (or str `ALL`)
        @type   maxWorkers:     int
        """
        
        #Ignore domain validation, if someone wants to lookup an invalid domain let them
        #Just ensure it's a string
        assert type(domain) == str, "Domain must be a string"
        
        #Ensure record type is valid, and in our list of allowed records
        recordType = recordType.upper()
        assert recordType in self.lookupRecordTypes, "Record type is not in valid list of record types {0}".format(', '.join(self.lookupRecordTypes))
        
        #Again, ignore list URL validation, requests will just throw a funny
        assert type(listLocation) == str, "List location must be a string"
        
        #Check local file location exists and is writable
        assert os.path.isdir(os.path.dirname(listLocal)), "{0} is not a directory!".format(os.path.dirname(listLocal))
        assert os.access(os.path.dirname(listLocal), os.W_OK), "{0} is not writable!".format(os.path.dirname(listLocal))
        
        #Check maxWorkers is valid
        try:
            maxWorkers = int(maxWorkers)
        except ValueError:
            assert False, "Thread count should be a number"
        
        #Check maxServers
        if not maxServers == 'ALL':
            try:
                maxServers = int(maxServers)
            except ValueError:
                assert False, "Servers to query should be a number or ALL"
        
        #W00T! Validation completed, save everything to instance
        self.domain = domain
        self.recordType = recordType
        self.listLocation = listLocation
        self.listLocal = listLocal
        self.maxWorkers = maxWorkers
        self.maxServers = maxServers
    
    def updateList(self):
        """
        Check to see if the resolver list needs updating
        
        Get the filemtime on the local list, if it's older than the hosted list download the new one
        """
        
        logging.debug("Checking local and remote resolver list for update")
        
        #If the local resolver file does not exist, or it has expired
        if not os.path.isfile(self.listLocal) or os.path.getmtime(self.listLocal) < time.time()-self.updateListEvery:
            logging.info("Updating resolver list file")
            r = requests.get(self.listLocation)
            
            if r.status_code != 200:
                #If status code response is not 200 and we don't already have a resolvers file, raise an exception
                #Otherwise keep going with the old file
                if not os.path.isfile(self.listLocal):
                    #File does not exist locally, we can't continue
                    raise EnvironmentError("List location returned HTTP status {0} and we don't have a local copy of resolvers to fall back on. Can't continue".format(r.status_code))
            else:
                #Save the file
                with open(self.listLocal, 'w') as lf:
                    lf.write(r.text)
    
    def query(self,progress=True):
        """
        Run the query
        
        Query spins out multiple thread workers to query each server
        
        @param  progress:   Write progress to stdout
        """
        
        logging.debug("Loading resolver file")
        
        #Open and yaml parse the resolver list
        with open(self.listLocal) as ll:
            raw = ll.read()
            #Use safe_load, just to be safe.
            serverList = yaml.safe_load(raw)
        
        #Get selected number of servers
        if self.maxServers == 'ALL':
            #Set servers to the number of servers we have
            self.maxServers = len(serverList)
        elif self.maxServers > len(serverList):
            #We were asked for more servers than exist in the list
            logging.warning(
                "You asked me to query {0} servers, but I only have {1} servers in my serverlist".format(
                    self.maxServers,
                    len(serverList)
            ))
            
            #Fallback to setting it to all
            self.maxServers = len(serverList)
        
        #Get a random selection of the specified number of servers from the list
        self.serverList = random.sample(serverList,self.maxServers)
        
        logging.debug("Starting query against {0} servers".format(len(self.serverList)))
        
        workers = []
        startTime = datetime.utcnow()
        serverCounter = 0
        
        #Run continuously while waiting for results
        while len(self.results) < len(self.serverList):
            
            #Count the workers still running
            runningWorkers = len([w for w in workers if w.result == None])
            
            #Get the results of any finished workers
            for i,w in enumerate(workers):
                if w.result:
                    #Add the results and get rid of the worker from the worker list
                    self.results.append(w.result)
                    workers.pop(i)
            
            #Output progress
            if progress:
                #Output progress on one line that updates if terminal supports it
                sys.stdout.write("\r\x1b[KStatus: Queried {0} of {1} servers, duration: {2}".format(
                    len(self.results),
                    len(self.serverList),
                    (datetime.utcnow()-startTime)
                ))
                #Make sure the stdout updates
                sys.stdout.flush()
            
            #Start more workers if needed
            if runningWorkers < self.maxWorkers:
                logging.debug("Starting {0} workers".format(self.maxWorkers - runningWorkers))
                
                #Start however many workers we need, based on max workers - running workers
                for i in range(0,self.maxWorkers - runningWorkers):
                    if serverCounter < len(self.serverList):
                        
                        #Create a new thread with all the details
                        wt = QueryWorker()
                        wt.server = self.serverList[serverCounter]
                        wt.domain = self.domain
                        wt.recType = self.recordType
                        wt.daemon = True
                        
                        #Add it to the worker tracker
                        workers.append(wt)
                        
                        #Start it
                        wt.start()
                        
                        serverCounter += 1
            
            #Pause a little bit
            time.sleep(0.1)
        
        #Now colate the results
        #Group by number of servers with the same response
        for r in self.results:
            #Result already in collation
            if r['results'] in [rs['results'] for rs in self.resultsColated]:
                cid = [i for i,rs in enumerate(self.resultsColated) if r['results'] == rs['results']][0]
                
                self.resultsColated[cid]['servers'].append(r['server'])
            else:
                self.resultsColated.append(
                    {
                        'servers':[
                            r['server']
                        ],
                        'results':r['results'],
                        'success':r['success']
                    }
                )
        
        if progress:
            sys.stdout.write("\n\n")
        logging.debug("There are {0} unique resulsts".format(len(self.resultsColated)))
    
    def outputStandard(self,extended=False):
        """
        Standard, multi-line output display
        """
        
        successfulResponses = len([True for rsp in self.results if rsp['success']])
        
        sys.stdout.write(""" - RESULTS

I asked {num_servers} servers for {rec_type} records related to {domain},
{success_responses} responded with records and {error_responses} gave errors
Here are the results;\n\n\n""".format(
            num_servers=len(self.serverList),
            rec_type=self.recordType,
            domain=self.domain,
            success_responses=successfulResponses,
            error_responses=len(self.serverList) - successfulResponses
        ))
        
        errors = []
        
        for rsp in self.resultsColated:
            
            out = []
            
            if extended:
                out.append("The following servers\n")
                out.append("\n".join([
                    " - {0} ({1} - {2})".format(s['ip'],s['provider'],s['country'])
                    for s in rsp['servers']
                ]))
                out.append("\nresponded with;\n")
            else:
                out.append("""{num_servers} servers responded with;\n""".format(num_servers=len(rsp['servers'])))
            
            out.append(
                "\n".join(rsp['results'])
            )
            
            out.append("\n\n")
            
            if rsp['success']:
                sys.stdout.write("".join(out))
            else:
                errors.append("".join(out))
        
        
        sys.stdout.write("\n\nAnd here are the errors;\n\n\n")
        
        sys.stdout.write("".join(errors))
    
    def outputSimple(self):
        """
        Simple output mode
        """
        
        out = []
        errors = []
        
        successfulResponses = len([True for rsp in self.results if rsp['success']])
        
        out.append("INFO QUERIED {0}".format(len(self.serverList)))
        out.append("INFO SUCCESS {0}".format(successfulResponses))
        out.append("INFO ERROR {0}".format(len(self.serverList) - successfulResponses))
        
        for rsp in self.resultsColated:
            if rsp['success']:
                out.append("RESULT {0} {1}".format(
                    len(rsp['servers']),
                    "|".join(rsp['results'])
                ))
            else:
                errors.append("ERROR {0} {1}".format(
                    len(rsp['servers']),
                    "|".join(rsp['results'])
                ))
        
        out += errors
        
        sys.stdout.write("\n".join(out))
        sys.stdout.write("\n")

class QueryWorker(threading.Thread):
    """
    A single worker, in charge of querying one DNS server
    
    @ivar   server:     Info on the server to query
    @ivar   domain:     Domain to query for
    @ivar   recType:    Record type
    @ivar   result:     Query result
    """
    
    server = None
    domain = None
    recType = None
    result = None
    
    def run(self):
        """
        Do a single DNS query against a server
        """
        
        logging.debug("Querying server {0}".format(self.server['ip']))
        
        try:
            #Create a DNS resolver query
            rsvr = dns.resolver.Resolver()
            rsvr.nameservers = [self.server['ip']]
            rsvr.lifetime = 5
            rsvr.timeout = 5
            
            qry = rsvr.query(self.domain, self.recType)
            
            #Get the results, sort for consistancy
            results = sorted([r.to_text() for r in qry])
            success = True
        except dns.resolver.NXDOMAIN:#Handle all the various exceptions
            success = False
            results = ['NXDOMAIN']
        except dns.resolver.NoNameservers:
            success = False
            results = ['No Nameservers']
        except dns.resolver.NoAnswer:
            success = False
            results = ['No Answer']
        except dns.resolver.Timeout:
            success = False
            results = ['Server Timeout']
        
        #Save the results
        self.result = {
            'server':self.server,
            'results':results,
            'success':success
        }