from flask import Flask, jsonify, render_template
from pymongo import MongoClient
import paho.mqtt.client as mqtt
from datetime import datetime

app = Flask(__name__)

mongo_client = MongoClient('mongodb://localhost:27017/')
db = mongo_client['hidroponikDB']
collection = db['sensorData']

mqtt_broker = 'broker.hivemq.com'
mqtt_port = 1883
mqtt_topic_suhu = 'hidroponik/suhu'
mqtt_topic_kelembapan = 'hidroponik/kelembapan'

def on_connect(client, userdata, flags, rc):
    print("Terhubung ke MQTT broker dengan kode: " + str(rc))
    client.subscribe([(mqtt_topic_suhu, 0), (mqtt_topic_kelembapan, 0)])

def on_message(client, userdata, msg):
    topic = msg.topic
    value = float(msg.payload.decode())
    current_time = datetime.now()
    sensor_type = 'temperature' if topic == mqtt_topic_suhu else 'humidity'
    
    document = {
        'sensorType': sensor_type,
        'value': value,
        'timestamp': current_time
    }
    collection.insert_one(document)
    print(f"Data tersimpan: {document}")

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(mqtt_broker, mqtt_port, 60)
mqtt_client.loop_start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/sensorData', methods=['GET'])
def get_sensor_data():
    data = list(collection.find().sort("timestamp", -1).limit(10))
    for item in data:
        item['_id'] = str(item['_id'])
    return jsonify(data)

@app.route('/api/Data', methods=['GET'])
def get_processed_sensor_data():
    sensor_data = collection.find()
    
    suhumax = 30.5
    suhumin = 18.2
    suhurata = 24.4
    
    nilai_suhu_max_humid_max = []
    for item in sensor_data:
        sensor_type = item.get('sensorType')
        if sensor_type == 'temperature':
            nilai_suhu_max_humid_max.append({
                'suhu': item.get('value', 0),
                'humid': item.get('humidity', 0),
                'Kecerahan': item.get('brightness', 0),
                'timestamp': item.get('timestamp', datetime.now().isoformat())
            })

    month_year_max = []
    for item in collection.aggregate([
        {"$group": {
            "_id": {"month": {"$month": "$timestamp"}, "year": {"$year": "$timestamp"}},
            "max_suhu": {"$max": "$value"}
        }},
        {"$sort": {"_id.year": 1, "_id.month": 1}}
    ]):
        month = item['_id'].get('month', None)
        year = item['_id'].get('year', None)
        
        if month is not None and year is not None:
            month_year_max.append({
                "month_year": f"{month:02d}-{year}"
            })

    hasil = {
        "suhumax": suhumax,
        "suhumin": suhumin,
        "suhurata": suhurata,
        "nilai_suhu_max_humid_max": {
            str(idx): {
                "idx": idx,
                "suhu": suhu["suhu"],
                "humid": suhu["humid"],
                "Kecerahan": suhu["Kecerahan"],
                "timestamp": suhu["timestamp"]
            } for idx, suhu in enumerate(nilai_suhu_max_humid_max)
        },
        "month_year_max": {
            str(idx): {
                "month_year": suhu["month_year"]
            } for idx, suhu in enumerate(month_year_max)
        }
    }

    return jsonify(hasil)

if __name__ == '__main__':
    app.run(debug=True)
