# This software is licensed under the GNU GENERAL PUBLIC LICENSE
# Version 3, 29 June 2007

from mylib.const import *
from mylib.block import *
from mylib.transaction import *
from mylib.trie import *
from mylib.pow import *

from typing import (
    Tuple,
)
from lxml import etree
import sys
from ethereum.pow import ethash
from web3 import Web3, TestRPCProvider
from ethereum.utils import (
    normalize_key,
    ecrecover_to_pub,
)
from binascii import unhexlify
import hmac
import hashlib
from base64 import (
    b64decode,
    b64encode,
)
from eth_utils import (
    keccak
)

key = str
index = int
nodeid = str
UserInput_Verify = Tuple[MyBlockHeader,
                         MyTransaction,
                         MyTrie,
                         index,
                         nodeid,
                         key
                         ]


def run(path):
    try:
        xml_doc = etree.parse(path)
    except Exception as e:
        print(False)
        print(e)
        exit(1)

    if not validate_structure(xml_doc):
        print(False)
        exit(1)

    block, tx, trie, index, nodeid, key = parse_user_input_verify(xml_doc)
    key = strip_string(key)

    if not verify_block_hash_and_transaction_trie(tx, trie, index):
        print(False)
        exit(1)

    if not verify_block_difficulty(block):
        print(False)
        exit(1)

    if not verify_difficulty_against_target(block):
        print(False)
        exit(1)

    if not verify_tx_details_and_signature(tx, key):
        print(False)
        exit(1)

    if not verify_node_id(block, index, nodeid):
        print(nodeid)
        print(False)
        exit(1)

    info = {
        'nodeid': nodeid,
        'publickey': key
    }

    print(info)
    print(True)


def validate_structure(xml_doc) -> bool:
    xmlschema = etree.XMLSchema(etree.XML(xsd))
    return xmlschema.validate(xml_doc)


def verify_block_hash_and_transaction_trie(tx, trie, index) -> bool:
    '''trie.trie is initialized with block['transactionsRoot'] this means, that if
    block['transactionsRoot'] is not correct the trie.trie[tx_index] returns "". And
    then this method fails. So there is no need to prove that
    block['transactionsRoot'] == trie.trie.root_hash'''
    tx_rlp = rlp.encode(tx)
    tx_index = rlp.encode(index, sedes=rlp.sedes.big_endian_int)
    if not trie.trie[tx_index] == tx_rlp:
        return False
    return True


def verify_block_difficulty(block) -> bool:
    return check_pow(block)


def verify_difficulty_against_target(block) -> bool:
    return block['difficulty'] >= difficulty_network_target


def verify_tx_details_and_signature(tx, key) -> bool:
    if not prove_signature(tx, key):
        return False
    if not tx['to'] in [unhexlify(x[2:]) for x in donation_addresses]:
        return False
    return tx['value'] >= value_network_target


def prove_signature(tx: MyTransaction, key: key) -> bool:
    key = unhexlify(key)
    if not tx.sender() == utils.sha3(key)[-20:]:
        return False
    return True


def verify_node_id(block, index, nodeid):
    return create_node_id(block.hash(), bytes([index])) == nodeid


def parse_user_input_verify(xml_doc) -> UserInput_Verify:
    block = deserialize_block_header(
        str(xml_doc.xpath('//root/proof/block/text()')))

    tx = deserialize_transaction(
        str(xml_doc.xpath('//root/proof/transaction/text()'))[10:-20])

    trie = deserialize_trie(strip_string(
        str(xml_doc.xpath('//root/proof/trie/text()'))), block['transactionsRoot'])

    index = int(strip_string(str(xml_doc.xpath(
        '//root/proof/transaction/index/text()'))))

    nodeid = str(xml_doc.xpath('//root/proof/nodeinfo/nodeid/text()'))[2:-2]

    public_key = str(xml_doc.xpath('//root/proof/nodeinfo/publickey/text()'))

    return block, tx, trie, index, nodeid, public_key


def create_node_id(blockhash: bytes, tx_index: bytes) -> str:
    '''calculates the nodeid as nid=HMAC(k_HMAC,TX_index)'''
    dig = hmac.new(blockhash, msg=tx_index,
                   digestmod=hashlib.sha256).digest()
    return b64encode(dig).decode()


def data_encoder(data: bytes, length=None) -> str:
    '''convert data from unformatted binary to str,
    if length is given the result will be padded with leading zeros
    e.g.: data_encoder(\\ff,3) returns 0x00000ff'''
    s = binascii.hexlify(data).decode('ascii')
    if length is None:
        return '0x' + s
    else:
        return '0x' + s.rjust(length * 2, '0')


def private_key_to_address(private_key: str) -> str:
    '''Extracts the address from the given private key, returning the
    hex representation of the address'''
    if isinstance(private_key, str):
        private_key = data_decoder(private_key)
    return data_encoder(privtoaddr(private_key))


def strip_string(string: str) -> str:
    return string.replace('\'', '').replace('[', '').replace(']', '').replace('\"', '')


if __name__ == "__main__":
    run(sys.argv[1:][0])
