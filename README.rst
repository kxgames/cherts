******
Cherts
******
A chess-inspired real-time strategy game.

.. image:: https://img.shields.io/pypi/v/cherts.svg
   :target: https://pypi.python.org/pypi/cherts

.. image:: https://img.shields.io/pypi/pyversions/cherts.svg
   :target: https://pypi.python.org/pypi/cherts

.. image:: https://img.shields.io/readthedocs/cherts.svg
   :target: https://cherts.readthedocs.io/en/latest/?badge=latest

.. image:: https://img.shields.io/travis/kxgames/cherts.svg
   :target: https://travis-ci.org/kxgames/cherts

.. image:: https://img.shields.io/coveralls/kxgames/cherts.svg
   :target: https://coveralls.io/github/kxgames/cherts?branch=master

Installation
============
Install cherts using ``pip``::

    $ pip install cherts

Usage
=====
Run a single-player game::

    $ cherts sandbox

Run a multiplayer server::

    # Get a hostname that is visible from the internet:
    $ hostname
    example.com

    # Open a port for the server.  The specific command needed to do this will 
    # depend on the server's firewall, but `iptables` is a representative 
    # example.  Any port can be used, but `53351` is the default.
    $ iptables -A INPUT -p tcp –dport 53351 -j ACCEPT

    $ cherts server 2 --host example.com

Run a multiplayer client (to connect with the above server)::

    $ cherts client --host example.com

Run a server and any number of clients all on one machine, to debug multiplayer 
gameplay::

    $ cherts debug 2
