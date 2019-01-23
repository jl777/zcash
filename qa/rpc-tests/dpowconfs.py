#!/usr/bin/env python2
# Copyright (c) 2018 The Hush developers
# Copyright (c) 2019 The SuperNET developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal, initialize_chain_clean, \
    start_node, stop_node, wait_bitcoinds, start_nodes, \
    assert_greater_than_or_equal

class DPoWConfsTest(BitcoinTestFramework):

    def setup_chain(self):
        self.num_nodes = 1
        print("Initializing DPoWconfs test directory "+self.options.tmpdir)
        initialize_chain_clean(self.options.tmpdir, self.num_nodes)

    def setup_network(self):
        print("Setting up network...")
        self.nodes            = []
        self.is_network_split = False
        self.addr             = "RWPg8B91kfK5UtUN7z6s6TeV9cHSGtVY8D"
        self.pubkey           = "02676d00110c2cd14ae24f95969e8598f7ccfaa675498b82654a5b5bd57fc1d8cf"
        self.nodes            = start_nodes( self.num_nodes, self.options.tmpdir,
                extra_args=[[
                    '-ac_name=REGTEST',
                    '-conf='+self.options.tmpdir+'/node0/REGTEST.conf',
                    '-port=64367',
                    '-rpcport=64368',
                    '-regtest',
                    '-addressindex=1',
                    '-spentindex=1',
                    '-ac_supply=5555555',
                    '-ac_reward=10000000000000',
                    #'-pubkey=' + self.pubkey,
                    '-ac_cc=2',
                    '-whitelist=127.0.0.1',
                    '-debug',
                    '--daemon',
                    '-rpcuser=rt',
                    '-rpcpassword=rt'
                    ]]
                )
        self.sync_all()

    def run_test(self):
        rpc = self.nodes[0]
        # 98 is notarized, next will be 105. Must mine at least 101
        # blocks for 100 block maturity rule
        blockhashes = rpc.generate(101)
        # block 98, this is 0 indexed
        notarizedhash = blockhashes[97]
        print rpc.getinfo()
        print rpc.getwalletinfo()

        taddr = rpc.getnewaddress()
        rpc.sendtoaddress(taddr, 5.55)
        rpc.generate(2)

        info = rpc.getinfo()
        print "notarizedhash=", notarizedhash
        print "info[notarizedhash]", info['notarizedhash']
        assert_equal( info['notarizedhash'], notarizedhash)

        result = rpc.listunspent()

        # this xtn has 2 raw confs, but not in a notarized block,
        # so dpowconfs holds it at 1
        for res in result:
            if (res['address'] == taddr and res['generated'] == 'false'):
                assert_equal( result[0]['confirmations'], 1 )
                assert_equal( result[0]['rawconfirmations'], 2 )

        print rpc.listreceivedbyaddress()

        # we will now have 3 rawconfs but confirmations=1 because not notarized
        rpc.generate(1)
        minconf = 2
        result = rpc.listreceivedbyaddress(minconf)
        print "listreceivedbyaddress(2)=", result

        # this will be empty because there are no notarized xtns
        for res in result:
            print res
            # there should be no entries with 1 dpowconf, since we asked for minconf=2
            assert( result[0]['confirmations'] >= minconf )

        # this is a notarized block
        rpc.generate(1)
        result = rpc.listreceivedbyaddress(minconf)
        assert( len(result), 'got results')
        print "listreceivedbyaddress(2)=", result
        for res in result:
            # there should be no entries with 1 dpowconf, since we asked for minconf=2
            assert_greater_than_or_equal( result[0]['confirmations'] , minconf )


if __name__ == '__main__':
    DPoWConfsTest().main()
