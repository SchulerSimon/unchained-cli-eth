# This software is licensed under the GNU GENERAL PUBLIC LICENSE
# Version 3, 29 June 2007

# minimum difficulty for a proof to be accepted
difficulty_network_target = 40000
# list of addresses that are accepted as donation addresses
donation_addresses = ['0xed6ca7d908f897d0b0d5f9b9e7aa470698e10b1b']
# minimum amount of eth to be donated in order for the proof to be accepted
value_network_target = 10000

'''
There is an inofficial list of chainids. Here I am using 3 (Ropsten) 
but this could (and should) be changed for actual use of this tool.

0: Olympic, Ethereum public pre-release testnet
1: Frontier, Homestead, Metropolis, the Ethereum public main network
1: Classic, the (un)forked public Ethereum Classic main network, chain ID 61
1: Expanse, an alternative Ethereum implementation, chain ID 2
2: Morden, the public Ethereum testnet, now Ethereum Classic testnet
3: Ropsten, the public cross-client Ethereum testnet
4: Rinkeby, the public Geth PoA testnet
8: Ubiq, the public Gubiq main network with flux difficulty chain ID 8
42: Kovan, the public Parity PoA testnet
77: Sokol, the public POA Network testnet
99: Core, the public POA Network main network
7762959: Musicoin, the music blockchain
61717561: Aquachain, ASIC resistant chain
[Other]: Could indicate that your connected to a local development test network.
'''
const_chain_id = 3


# separators for strings. Used for serialisation
sep1 = ','
sep2 = ':'
sep3 = ';'

# unchained deploy target folder
target_folder = '/unchained-eth/'

# string bib
error_wrong_key = 'The private key that was provided is not the one that the transaction was signed with. Please provide the correct private key.'
text_proof_comment = 'proof-file for: "Unchained Identities: Putting a Price on Sybil Nodes in Mobile Ad hoc Networks" by Prof. Dr. Dieter Hogrefe, M.Sc. Arne Bochem and M.Sc. Bejmain Leiding.'
text_nodeid_comment = 'id-file for: "Unchained Identities: Putting a Price on Sybil Nodes in Mobile Ad hoc Networks" by Prof. Dr. Dieter Hogrefe, M.Sc. Arne Bochem and M.Sc. Bejmain Leiding.'
text_private_key_warning = 'DO NEVER EVER SHARE THIS KEY WITH ANYONE!'
name_proof_file = '/unchained-proof.xml'
name_id_file = '/unchained-id.xml'

# xsd to prove the structure of the proof
xsd = '''
<xs:schema attributeFormDefault="unqualified" elementFormDefault="qualified" xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="root">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="proof">
          <xs:annotation>
            <xs:documentation></xs:documentation>
          </xs:annotation>
          <xs:complexType>
            <xs:sequence>
              <xs:element type="xs:string" name="block"/>
              <xs:element name="transaction">
                <xs:complexType mixed="true">
                  <xs:sequence>
                    <xs:element type="xs:string" name="index"/>
                  </xs:sequence>
                </xs:complexType>
              </xs:element>
              <xs:element type="xs:string" name="trie"/>
              <xs:element name="nodeinfo">
                <xs:complexType>
                  <xs:sequence>
                    <xs:element type="xs:string" name="nodeid"/>
                    <xs:element type="xs:string" name="publickey"/>
                  </xs:sequence>
                </xs:complexType>
              </xs:element>
            </xs:sequence>
          </xs:complexType>
        </xs:element>
      </xs:sequence>
    </xs:complexType>
  </xs:element>
</xs:schema>
'''
