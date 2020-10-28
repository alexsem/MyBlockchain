import argparse

from flask import Flask, jsonify, request
from Alfajoin.alfajoin import Blockchain
from uuid import uuid4

app = Flask(__name__)

# Creating an address for the node on Port 5000
node_address = str(uuid4()).replace('-', '')

receiver: str

# Create Blockchain
blockchain = Blockchain()

# Mining new block
@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender=node_address, receiver=receiver, amount=1)
    block = blockchain.create_block(proof, previous_hash)
    response = {
        'message': 'Congratulations, you just mined a block',
        'index': block['index'],
        'timestamp': block['timestamp'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
        'transactions': block['transactions']
    }
    return jsonify(response), 200


# Getting the full Blockchain
@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {
        'chain': blockchain.chain,
        'lenght': len(blockchain.chain)
    }
    return jsonify(response), 200


# Check if the chain is valid
@app.route('/is_valid', methods=['GET'])
def is_valid():
    valid_chain = blockchain.is_chain_valid(blockchain.chain)
    response = {
        'is_valid': valid_chain
    }
    return jsonify(response), 200


@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all(key in json for key in transaction_keys):
        return 'Some elements of the transaction are missing', 400
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response = {'message': f'This transaction will be added to Block{index}'}
    return jsonify(response), 201


@app.route('/connect_node', methods=['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return 'No nodes', 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': f'All the nodes are now connected. The Alfjoin Blockchain now contains the following nodes:',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response, 201)


@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    is_chain_replace = blockchain.replace_chain()
    if is_chain_replace:
        response = {'message': 'The node had different chains so the chain was replaced by the longest one.',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'All good. The chain is the correct one.',
                    'actual_chain': blockchain.chain}
    return jsonify(response, 200)


def parse_args():
    parser = argparse.ArgumentParser(description='alfajoin')

    parser.add_argument('-p', '--port', required=True)
    parser.add_argument('-r', '--receiver', required=True)

    return parser.parse_args()


# Running the app
if __name__ == '__main__':
    args = parse_args()
    receiver = args.receiver
    app.run(host='0.0.0.0', port=args.port)
