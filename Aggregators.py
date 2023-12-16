from flask import Flask, request, jsonify
import requests
import asyncio
import aiohttp
app = Flask(__name__)

# Add configurations and any necessary initialization here

BUILDING_APP_URL = "http://building-app-ip:port"  
TENANT_APP_URL = "http://tenant-app-ip:port" 

@app.route('/add_new_tenant', methods=['POST'])
def add_new_tenant():
    data = request.json
    room_id = data.get("room_id")
    try:
        building_room_url = f"{BUILDING_APP_URL}/check_room/{room_id}"
        room_response = requests.get(building_room_url)
        if room_response.status_code == 200:
            # Room is available, extract building name and room number
            room_info = room_response.json()
            building_name = room_info.get('building_name')
            room_number = room_info.get('room_number')

            # Add building name and room number to tenant data
            data['building_name'] = building_name
            data['room_name'] = room_number

            # Proceed to create a tenant in the tenant app
            tenant_app_url = f"{TENANT_APP_URL}/api/Tenant"
            tenant_response = requests.post(tenant_app_url, json=data)
            return jsonify(tenant_response.json()), tenant_response.status_code
        else:
            return jsonify({'error': 'Room not available or does not exist'}), room_response.status_code
    except requests.RequestException as e:
        return jsonify({'error': f'Building app request failed: {str(e)}'}), 500

@app.route('/update_tenant/<email>', methods=['POST'])
def add_new_tenant(email):
    data = request.json
    room_id = data.get("room_id")
    try:
        building_room_url = f"{BUILDING_APP_URL}/check_room/{room_id}"
        room_response = requests.get(building_room_url)
        if room_response.status_code == 200:
            # Room is available, extract building name and room number
            room_info = room_response.json()
            building_name = room_info.get('building_name')
            room_number = room_info.get('room_number')

            # Add building name and room number to tenant data
            data['building_name'] = building_name
            data['room_name'] = room_number

            # Proceed to create a tenant in the tenant app
            tenant_app_url = f"{TENANT_APP_URL}/api/Tenant/{email}"
            tenant_response = requests.put(tenant_app_url, json=data)
            return jsonify(tenant_response.json()), tenant_response.status_code
        else:
            return jsonify({'error': 'Room not available or does not exist'}), room_response.status_code
    except requests.RequestException as e:
        return jsonify({'error': f'Building app request failed: {str(e)}'}), 500

app.run(port=5002, debug=True)
