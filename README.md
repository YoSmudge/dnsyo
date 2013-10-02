#DNSYO
##AALLLLL THE DNS

DNSYO is a little tool I built to help me keep track of DNS propagation.

In short, it's `nslookup`, if `nslookup` queried over 100 servers and collated their results.

Here's what it does

    $ dnsyo example.com A
    Status: Queried 127 of 127 servers, duration: 0:00:10

     - RESULTS

    I asked 127 servers for A records related to geo.example.com,
    115 responded with records and 12 gave errors
    Here are the results;


    29 servers responded with;
    1.2.3.4

    48 servers responded with;
    4.3.2.1

    38 servers responded with;
    5.5.4.4


    And here are the errors;


    5 servers responded with;
    No Answer

    7 servers responded with;
    Server Timeout

##Installation

DNSYO requires Python 2.6 or later. The easiest way to install is by running

    pip install -r https://raw.github.com/samarudge/dnsyo/master/requirements.txt

You should probably install it within a virtualenv.

If all goes well, you should be clear to start querying stuff

To test, try running

    dnsyo google.com

It will query all the DNS servers in the database, and give you the results.

##Usage

###Output modes

DNSYO has 3 output modes;

  * standard - Will display all the results and errors from querying
  * extended - Same as standard but includes the names and addresses of the servers it queried
  * simple - Simple output mode which is useful for UNIX scripting

To change output mode, pass ether `--extended` or `--simple` to DNSYO.

###Resolver list

DNSYO periodically updates it's internal resolver database from this repo. The first time you run it, and once every 2 weeks, it will try to download the `resolver-list.yml` file and store it to your systems `/tmp` directory. If you know of any more open DNS resolvers feel free to add them to the list.

##Licence

DNSYO is released under the MIT licence, see `LICENCE.txt` for more info