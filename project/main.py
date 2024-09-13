import json
import os
import socket
import threading
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for

# Create Flask app
app = Flask(__name__)

# Create storage directory if it doesn't exist
if not os.path.exists('storage'):
    os.makedirs('storage')

# Flask Routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/message.html', methods=['GET', 'POST'])
def message():
    if request.method == 'POST':
        username = request.form['username']
        message = request.form['message']

        # Send data to UDP server
        udp_client_send(username, message)

        return redirect(url_for('index'))

    return render_template('message.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404


# UDP Client: Send data to UDP server
def udp_client_send(username, message):
    server_address = ('localhost', 5000)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        data = json.dumps({'username': username, 'message': message}).encode('utf-8')
        sock.sendto(data, server_address)


# UDP Server: Receive and store data
def udp_server():
    server_address = ('localhost', 5000)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(server_address)

    print("UDP server started on port 5000")

    while True:
        data, address = sock.recvfrom(4096)
        if data:
            message_data = json.loads(data.decode('utf-8'))
            timestamp = str(datetime.now())
            store_message(timestamp, message_data)


# Store message in JSON file
def store_message(timestamp, message_data):
    storage_file = 'storage/data.json'
    if not os.path.exists(storage_file):
        with open(storage_file, 'w') as f:
            json.dump({}, f)

    with open(storage_file, 'r+') as f:
        data = json.load(f)
        data[timestamp] = message_data
        f.seek(0)
        json.dump(data, f, indent=4)


# Run Flask and UDP server in parallel
if __name__ == "__main__":
    udp_thread = threading.Thread(target=udp_server)
    udp_thread.daemon = True
    udp_thread.start()

    app.run(host='0.0.0.0', port=3000)

