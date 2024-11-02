from flask import Flask, request, jsonify
from kafka import KafkaProducer
from pymongo import MongoClient
from kafka.admin import KafkaAdminClient, NewTopic
import json

from api_server import purchases_history_collection

app = Flask(__name__)


producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8') 
)

client = MongoClient('localhost', 27017)
db = client['shop']
inventory = db['inventory']

@app.route('/')
def index():
    return app.send_static_file('index.html')
@app.route('/admin')
def index_amdmin():
    return app.send_static_file('index_admin.html')

@app.route('/buy', methods=['POST'])
def buy_item():
    data = request.json
    item_name = data.get('item')

    product = inventory.find_one({'item': item_name})

    if product and product.get('count', 0) > 0:
        producer.send('purchases-events', {'item': item_name})
        producer.flush() 

        return jsonify({"message": f"Purchase for {item_name} has been placed!"}), 200
    else:
        return jsonify({"message": f"Sorry, {item_name} is sold out!"}), 400

@app.route('/admin/buy', methods=['POST'])
def buy_item_for_inventory():
    data = request.json 
    item_name = data.get('item')

    producer.send('inventory-events', {'item': item_name})
    producer.flush()

    return jsonify({"message": f"Inventory updated for {item_name}!"}), 200

@app.route('/inventory', methods=['GET'])
def get_inventory():
    purchases = list(inventory.find({}, {'_id': 0}))
    return jsonify(purchases), 200
@app.route('/history', methods=['GET'])
def get_purchases():
    purchases = list(purchases_history_collection.find({}, {'_id': 0}))
    return jsonify(purchases), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
