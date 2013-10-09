#DNSYO
##AALLLLL THE DNS

DNSYO is a little tool I built to help me keep track of DNS propagation.

In short, it's `nslookup`, if `nslookup` queried over 1500 servers and collated their results.

Here's what it does

    $ dnsyo -t 100 -q ALL example.com
    Status: Queried 1804 of 1804 servers, duration: 0:00:09.334441

     - RESULTS

    I asked 1804 servers for A records related to example.com,
    1771 responded with records and 33 gave errors
    Here are the results;


    1738 servers responded with;
    93.184.216.119

    26 servers responded with;
    127.0.0.1

    1 servers responded with;
    97.87.216.210

    1 servers responded with;
    64.202.162.37

    1 servers responded with;
    68.87.91.199

    1 servers responded with;
    216.8.179.23

    2 servers responded with;
    77.244.128.69

    1 servers responded with;
    1.1.1.12



    And here are the errors;


    8 servers responded with;
    No Nameservers

    4 servers responded with;
    No Answer

    21 servers responded with;
    Server Timeout

##Installation

DNSYO requires Python 2.6 or later. The easiest way to install is by running

    pip install dnsyo --upgrade

You should probably install it within a virtualenv.

If all goes well, you should be clear to start querying stuff

To test, try running

    dnsyo google.com

It will query all the DNS servers in the database, and give you the results.

##Usage

For more information on the flags run `dnsyo -h`

###Output modes

DNSYO has 3 output modes;

  * standard - Will display all the results and errors from querying
  * extended - Same as standard but includes the names and addresses of the servers it queried
  * simple - Simple output mode which is useful for UNIX scripting

To change output mode, pass ether `--extended` or `--simple` to DNSYO.

###Resolver list

DNSYO periodically updates it's internal resolver database from this repo. The first time you run it, and once every 2 weeks, it will try to download the `resolver-list.yml` file and store it to your systems `/tmp` directory. If you know of any more open DNS resolvers feel free to add them to the list.

By default, DNSYO will pick 500 servers at random from it's list to query. You can change this with the `--query` flag. If you want DNSYO to query all the servers just pass `--query=ALL`

###Record types

Just like dig, you can pass the record type as the second positional argument to DNSYO, so to get Google's MX records just do

    dnsyo google.com MX

##Licence

DNSYO is released under the MIT licence, see `LICENCE.txt` for more info