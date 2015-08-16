"""
Code to take the list of resolvers and return a list of working ones

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

import logging
import dnsyo
import os
import yaml


class update(object):
    """

    @cvar   testRecords:    List of records to test and, optionally the
                            expected result(s)
    """

    testRecords = [
        {
            "query": ["google.com", "A"]
        },
        {
            "query": ["facebook.com", "A"]
        },
        {
            "query": ["amazon.com", "A"]
        },
        {
            "query": ["www.youtube.com", "A"]
        },
        {
            "query": ["www.codesam.co.uk", "A"],
            "result": "188.165.232.223"
        },
        {
            "query": ["dnsyo-list.codesam.co.uk", "CNAME"],
            "result": "eu1.srv.codesam.co.uk."
        },
        {
            "query": ["www.songkick.com", "A"],
            "result": "94.228.36.46"
        }
    ]

    def __init__(self, lookup, summaryFile, outputFile):
        """
        Create an instance of the updater

        Gets passed a pre-configured L{dnsyo.lookup} object

        @param  lookup:         Instance of a L{dnsyo.lookup}
        @param  summaryFile:    Location of file to write update summary to
        @param  outputFile:     Target list to write results to

        @type   lookup:         L{dnsyo.lookup}
        @type   summaryFile:    str(file)
        @type   outputFile:     str(file)
        """
        self.lookup = lookup
        self.sourceServers = self.lookup.prepareList(noSample=True)

        self.summaryFile = summaryFile
        self.outputFile = outputFile

        foundServers = []
        duplicateServers = []

        for s in self.sourceServers:
            if s['ip'] in foundServers:
                logging.warning("Server {0} is a duplicate!".format(
                    s['ip']
                ))
                duplicateServers.append(s['ip'])
            else:
                foundServers.append(s['ip'])

        if len(duplicateServers) > 0:
            raise Exception("{0} duplicate servers in source file!".format(
                len(duplicateServers)
            ))

        logging.info(
            "Will test {0} servers currently in list "
            "against {1} test records".format(
                len(foundServers),
                len(self.testRecords)
            )
        )

        self.testServers()

    def testServers(self):
        """
        Query all the servers in the source list against the test records

        Runs a L{dnsyo.lookup.query} against the test records and validates the
        results to determine which servers are still alive, then writes the
        results to the destination file and generates a summary.
        """

        serverFailures = {s['ip']: 0 for s in self.sourceServers}

        for test in self.testRecords:
            logging.info("Running test query {0}".format(test['query']))
            self.lookup.query(*test['query'], progress=False)

            for result in self.lookup.resultsColated:
                if not result['success'] or (
                    test.get('result') and
                    not test['result'] in result['results']
                ):
                    logging.warning("{0} servers failed ({1})".format(
                        len(result['servers']),
                        ",".join(result['results'])
                    ))

                    for s in result['servers']:
                        serverFailures[s['ip']] += 1

        passedServers = [
            s for s in self.sourceServers
            if serverFailures[s['ip']] < len(self.testRecords)
        ]

        logging.info("Tested {0} servers, found {1} working".format(
            len(self.sourceServers),
            len(passedServers)
        ))

        # Calculate the change from current resolvers
        currentResolvers = self.lookup.prepareList(
            self.outputFile,
            noSample=True
        )

        logging.info("Loaded {0} resolvers from destination list".format(
            len(currentResolvers)
        ))

        serversRemoved = [
            s for s in currentResolvers
            if s not in passedServers
        ]
        serversAdded = [
            s for s in passedServers
            if s not in currentResolvers
        ]

        # Generate the summary file
        with open(os.path.expanduser(self.summaryFile), 'w') as f:
            f.write("Updated server list ({0} added, {1} removed)\n\n".format(
                len(serversAdded),
                len(serversRemoved)
            ))

            for summaryDetails in [
                ("Added", serversAdded), ("Removed", serversRemoved)
            ]:
                if len(summaryDetails[1]) > 0:
                    f.write("Servers {0}\n---\n".format(
                        summaryDetails[0]
                    ))

                    f.write("\n".join([
                        " * {0} ({1} - {2})".format(
                            s['reverse'],
                            s['ip'],
                            s['country']
                        )
                        for s in summaryDetails[1]
                    ]))
                    f.write("\n\n")

        # Write out the destination file
        with open(os.path.expanduser(self.outputFile), 'w') as f:
            f.write("""# List of known *working* servers
# Working server list is calculated fortnightly
# If you'd like to add a new server, add it to resolver-list-sources.yml
""")
            f.write(yaml.safe_dump(
                sorted(
                    passedServers,
                    key=lambda k: k['provider']
                ),
                indent=2,
                default_flow_style=False
            ))
