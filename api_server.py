from flask import Flask, jsonify
from kafka import KafkaConsumer
from pymongo import MongoClient
import json
import threading

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client['shop']
purchases_history_collection = db['purchases_history']
inventory_collection = db['inventory']

purchase_consumer = KafkaConsumer(
    'purchases-events',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='purchase-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

inventory_consumer = KafkaConsumer(
    'inventory-events',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='inventory-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

def consume_purchase_messages():
    print("Starting Kafka consumer for purchase events...")
    for message in purchase_consumer:
        try:
            purchase_event = message.value
            print(f"Received purchase event: {purchase_event}")

            if purchase_event:
                item_name = purchase_event.get('item')

                print(f"Processing item: {item_name}")

                product = inventory_collection.find_one({'item': item_name})
                if product:
                    print(f"Item found in inventory: {product}")

                    result = inventory_collection.update_one(
                        {'item': item_name},
                        {'$inc': {'count': -1}}
                    )

                    print(f"Inventory updated for {item_name}, count decreased.")

                    purchases_history_collection.update_one(
                        {'item': item_name},
                        {'$inc': {'count': 1}},
                        upsert=True
                    )

                else:
                    print(f"Item '{item_name}' not found in inventory.")

        except json.JSONDecodeError as e:
            print(f"Skipping invalid message: {message.value} - Error: {e}")

def consume_inventory_messages():
    print("Starting Kafka consumer for inventory events...")
    for message in inventory_consumer:
        try:
            inventory_event = message.value
            print(f"Received inventory event: {inventory_event}")

            if inventory_event:
                item_name = inventory_event.get('item')

                result = inventory_collection.update_one(
                    {'item': item_name},
                    {'$inc': {'count': 1}},
                    upsert=True
                )

                print(f"Inventory updated for {item_name}, count increased. Result: {result.modified_count} document(s) updated.")

        except json.JSONDecodeError as e:
            print(f"Skipping invalid message: {message.value} - Error: {e}")

def start_purchase_consumer():
    consumer_thread = threading.Thread(target=consume_purchase_messages)
    consumer_thread.daemon = True
    consumer_thread.start()

def start_inventory_consumer():
    consumer_thread = threading.Thread(target=consume_inventory_messages)
    consumer_thread.daemon = True
    consumer_thread.start()

@app.route('/purchases', methods=['GET'])
def get_purchases():
    purchases = list(purchases_history_collection.find({}, {'_id': 0}))
    return jsonify(purchases), 200

if __name__ == '__main__':
    start_purchase_consumer()
    start_inventory_consumer()
    app.run(debug=True, host='0.0.0.0', port=5001) 
