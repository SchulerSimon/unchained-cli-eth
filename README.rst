unchained-cli-eth
=========

*A command line implementation of unchained-identities in Python for the Ethereum Network.*

Purpose
-------
This is a Python implementation of the paper "Unchained Identities: Putting a 
Price on Sybil Nodes in Mobile Ad hoc Networks". 

https://www.benjaminleiding.com/wp-content/uploads/2018/09/bo_le_ho_2018_unchained_identities.cameraready.pdf

Usage
-----
**This whole project needs python3**

.. code:: bash

 $ unchained create <private_key> <tx_hash> <rpc_endpoint> <path/for/proof>
  $ unchained verify <path/to/proof.xml>
  $ unchained deploy <path/to/proof.xml> <path/to/raspberry/dist/path/to/destination>
  $ unchained -h | --help
  $ unchained --version

Example
-------
On the ropsten testnetwork there is a transaction (hash: 0x8ec420a3ba331f2a967ecdaf69b78bbb604ebbb2554a8c635142b7b306defaae) of 1 eth that is accepted as valid transaction. This can be taken to verify that everything is working.


.. code:: bash

 $ pip install .
  $ unchained create 785cdcd731a1b2438ec4511a25d04efbdc499ed350df612364af1aa6f4fd6abd 0x8ec420a3ba331f2a967ecdaf69b78bbb604ebbb2554a8c635142b7b306defaae https://ropsten.infura.io/ffn6QLIJrYtke3b07YLp ./example_proof/
  $ unchained verify ./example_proof/unchained-proof.xml

output: 
    {'nodeid': 'RwqsYOJSFdAUTAQxvaag2w55T0GvTzBqpS6l41EfFwI=', 'publickey': '4bd485055bf829d8b8fd817ac6b4a0213f76b80c757cb33bd2f52ee6dc18240ac5ba4fb646d50eeac0eb6f9b01a22d3a9245b543105d47304869b14673bbbab5'}
    True

Dependencies
------------
* web3
* ethereum
* trie
* docopt
* lxml

Installation
------------
If you've cloned this project, and want to install the library (*and all
development dependencies*), the command you'll want to run is

.. code:: bash

 $ cd unchained-cli-eth
  $ pip install .


*if this installation failes, you need to install python3-dev and libssl-dev, because cytoolz and scrypt need them:*

.. code:: bash

 $ sudo apt-get install python3-dev
  $ sudo apt-get install libssl-dev

*then try again*


You should consider using a clean python3 environment, this can be done with virtualenv:
https://virtualenv.pypa.io/en/stable/

Installation on a raspberry pi
-----
After You installed this tool, you can use it to install unchained-identities on a raspberry pi
It is recommended to use virtualenv.

* Flash a sd-card with raspbian (strech-lite is recommended)
* change the rights, so You can write on the sdcard:

.. code:: bash

 $ sudo chmod -R a+rwx /meidia/<user>/rootfs/home/pi/<some sub folder>

* * be sure to not run chmod -R on /media/<user>>/rootfs/ because it will mess up the raspberry os
* Run unchained deploy

.. code:: bash

 $ unchained deploy <path/to/unchained-identities/repo/folder> <path/to/proof-and-id/folder> <path/to/raspberry/dist/path/to/destination/folder>
 
* boot up the raspberry

Under /<destination-folder>/unchained-eth you can find 
    * 'verify.py' - the skript that verifies proofs
    * 'unchained-proof.xml' - the proof for this node
    * 'unchained-id.xml' - the id for this node (contains private key, be carefull)
    * 'requirements.txt' - requirements for pip
    
* install python3 on the raspberry
* run 

.. code:: bash

 $ pip install -r /path/to/requirements.txt

* now You can try to verify Your own proof with

.. code:: bash

 $ python3 verify.py unchained-proof.xml

* output should be True
* Done

* if You get the error, that the import "from lxml import etree" is not working try installing lxml with 

.. code:: bash

 $ apt-get install python3-lxml

Configuration
-----
under <repo>/unchained/commands/mylib/ is a file called const.py

There are some options to custamize how this tool behaves, they are explained there.

Notes
-----
There is also a version of this Project for bitcoin: TODO(link)

please note that due to naming reasons it is not possible to install and run both versions in the same python3 environment on a PC (use virtualenv: https://virtualenv.pypa.io/en/stable/). Both versions can run alongside eachother on a pi.

this was implemented by Simon Schuler (schuler.simon@gmx.net)

Performance Measures
-----
Bitcoin:
    * Proof size (depending on blocksize): 
    * * ~10kb-50kb
    * Verify proof time on a raspberry pi 3:
    * * ~2 sec
    * Create proof time on desktop intel i7 quadcore
    * * ~1 sec

Ethereum:
    * Proof size (depending on blocksize): 
    * * ~50kb-150kb
    * Verify proof time on a raspberry pi 3:
    * * ~60 sec (!!)
    * Create proof time on desktop intel i7 quadcore
    * * ~10 sec (dependent on the speed of the provided rpc)

All in all we can say that the Bitcoin-Network has superior performance properties for IOT-devices. This is due to the deliberate design of the Ethereum hash function ethash. See: https://github.com/ethereum/wiki/wiki/Ethash-Design-Rationale