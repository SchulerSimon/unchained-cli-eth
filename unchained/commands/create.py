# This software is licensed under the GNU GENERAL PUBLIC LICENSE
# Version 3, 29 June 2007
from .base import Base
from .mylib.const import *
from .mylib.block import *
from .mylib.transaction import *
from .mylib.trie import *

from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement, Comment
from xml.dom import minidom

from web3 import Web3, HTTPProvider

from typing import (
    Tuple,
)

from ethereum.utils import (
    normalize_key,
    privtoaddr,
    ecsign,
    ecrecover_to_pub,
)
import sys
import binascii
import hmac
import hashlib
from base64 import (
    b64decode,
    b64encode,
)


raw_transaction = dict
tx_hashes = list
key = str
path = str

Transactions = Tuple[MyTransaction, ...]
UserInput_Create = Tuple[Web3, MyBlockHeader,
                         raw_transaction, tx_hashes, key, path]


class Create(Base):

    def run(self):
        web3, block, raw_tx, tx_hashes, private_key, path = parse_user_input_create()

        tx = make_transaction(raw_tx)

        if not prove_signature(web3, raw_tx, private_key):
            raise ValueError(error_wrong_key)
            exit(1)

        tx_index = raw_tx['transactionIndex']

        nodeid = create_node_id(
            block.hash(), bytes([tx_index]))

        public_key = private_to_public_key(tx, private_key)

        trie = make_trie_from_hashes(web3, tx_hashes)

        if not trie.trie.root_hash == block['transactionsRoot']:
            exit(1)

        block_str = serialize_block_header(block)

        tx_str = serialize_transaction(tx)

        trie_str = serialize_trie(trie)[0]

        xml = make_proof_xml(block_str, tx_str, trie_str,
                             tx_index, nodeid, public_key)
        try:
            file = open(path + name_proof_file, 'w')
            file.write(xml)
            file.close()
        except Exception as e:
            print(e)
            exit(1)

        xml = make_nodeid_xml(nodeid, public_key, private_key)

        try:
            file = open(path + name_id_file, 'w')
            file.write(xml)
            file.close()
        except Exception as e:
            print(e)
            exit(1)


def parse_user_input_create() -> UserInput_Create:
    args = sys.argv[2:]
    private_key = args[0]
    tx_hash = args[1]
    rpc_endpoint = args[2]
    path = args[3]

    try:
        web3_local = Web3(HTTPProvider(rpc_endpoint))
    except Exception as e:
        print(e)
        exit(1)

    try:
        raw_tx = web3_local.eth.getTransaction(tx_hash)
    except Exception as e:
        print(e)
        exit(1)

    try:
        bl = web3_local.eth.getBlock(raw_tx['blockHash'])
        block = make_block_header(bl)
        tx_hashes = bl['transactions']
    except Exception as e:
        print(e)
        exit(1)

    if path[-1:] == '/':
        path = path[:-1]

    return web3_local, block, raw_tx, tx_hashes, private_key, path


def make_proof_xml(block_str, tx_str, trie_str, tx_index, nodeid_str, public_key):
    root = Element('root')
    comment = Comment(text_proof_comment)
    root.append(comment)

    proof = SubElement(root, 'proof')

    block = SubElement(proof, 'block')
    block.text = block_str

    transaction = SubElement(proof, 'transaction')
    transaction.text = tx_str
    index = SubElement(transaction, 'index')
    index.text = str(tx_index)

    trie = SubElement(proof, 'trie')
    trie.text = trie_str

    nodeinfo = SubElement(proof, 'nodeinfo')

    nodeid = SubElement(nodeinfo, 'nodeid')
    nodeid.text = str(nodeid_str)

    publickey = SubElement(nodeinfo, 'publickey')
    publickey.text = public_key

    return prettify_xml(root)


def make_nodeid_xml(nodeid_str, public_key, private_key):
    root = Element('root')
    comment = Comment(text_nodeid_comment)
    root.append(comment)

    nodeinfo = SubElement(root, 'nodeinfo')

    nodeid = SubElement(nodeinfo, 'nodeid')
    nodeid.text = str(nodeid_str)

    publickey = SubElement(nodeinfo, 'publickey')
    publickey.text = public_key

    privatekey = SubElement(nodeinfo, 'privatekey')
    warning = Comment(text_private_key_warning)
    privatekey.append(warning)
    privatekey.text = private_key

    return prettify_xml(root)


def prettify_xml(elem) -> str:
    '''Return a pretty-printed XML string for the Element'''
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def prove_signature(web3: Web3, tx: dict, key: key, chain_id=const_chain_id) -> bool:
    if not make_transaction(tx).sender().hex().lower() == tx['from'][2:].lower():
        return False

    key = normalize_key(key)
    if not tx['from'].lower() == private_key_to_address(key).lower():
        return False

    transaction = {
        'to': tx['to'],
        'value': tx['value'],
        'gas': tx['gas'],
        'gasPrice': tx['gasPrice'],
        'nonce': tx['nonce'],
        'chainId': chain_id
    }
    signed = web3.eth.account.signTransaction(transaction, key)
    if signed.r == int(tx['r'].hex()[2:], 16) and signed.s == int(tx['s'].hex()[2:], 16) and signed.v == tx['v']:
        return True
    else:
        return False


def private_key_to_address(private_key: str) -> str:
    '''Extracts the address from the given private key, returning the
    hex representation of the address'''
    if isinstance(private_key, str):
        private_key = data_decoder(private_key)
    return data_encoder(privtoaddr(private_key))


def private_to_public_key(tx: MyTransaction,  private_key: str) -> str:
    '''finds the corresponding public key to the given private key'''
    signhash, _ = tx.get_sign_hash()
    v, r, s = ecsign(signhash, normalize_key(private_key))
    return ecrecover_to_pub(signhash, v, r, s).hex()


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


def strip_string(string: str) -> str:
    return string.replace('\'', '').replace('[', '').replace(']', '').replace('\"', '')
