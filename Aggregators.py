from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import asyncio
import aiohttp
app = Flask(__name__)

# Add configurations and any necessary initialization here

BUILDING_APP_URL = "http://18.204.252.196"  
TENANT_APP_URL = "https://3.220.219.78:5000" 
BILLING_APP_URL = "https://54.167.236.204:5001" 

async def fetch_url(session, url, params=None):
    async with session.get(url, params=params,ssl=False) as response:
        return await response.json()

async def get_data_from_urls(url1, url2, email):
    params = {'email': email}
    async with aiohttp.ClientSession() as session:
        task1 = asyncio.create_task(fetch_url(session, url1, params))
        task2 = asyncio.create_task(fetch_url(session, url2))  # No params needed for url2

        response1, response2 = await asyncio.gather(task1, task2)
        # 合并两个响应
        merged_response = {**response1, **response2}
        return merged_response


@app.route('/add_new_tenant', methods=['POST'])
def add_new_tenant():
    data = request.json
    room_id = data.get("room_id")
    building_name=data.get("building_name")
    try:
        building_room_url = f"{BUILDING_APP_URL}/api/building/{building_name}/check_room/{room_id}"
        room_response = requests.get(building_room_url)
        if room_response.status_code == 200:
            # Room is available, extract building name and room number
            room_info = room_response.json()
            building_name = room_info.get('building_name')
            room_number = room_info.get('room_number')
            #data['building_name'] = building_name
            data['room_name'] = room_number

            # Proceed to create a tenant in the tenant app
            tenant_app_url = f"{TENANT_APP_URL}/api/Tenant"
            tenant_response = requests.post(tenant_app_url, json=data,verify=False)
            return jsonify(tenant_response.json()), tenant_response.status_code
        else:
            return jsonify({'error': 'Room not available or does not exist'}), room_response.status_code
    except requests.RequestException as e:
        return jsonify({'error': f'Building app request failed: {str(e)}'}), 500

@app.route('/update_tenant/<email>', methods=['POST'])
def update_tenant(email):
    data = request.json
    room_id = data.get("room_id")
    building_name=data.get("building_name")
    try:
        building_room_url = f"{BUILDING_APP_URL}/api/building/{building_name}/check_room/{room_id}"
        room_response = requests.get(building_room_url)
        if room_response.status_code == 200:
            # Room is available, extract building name and room number
            room_info = room_response.json()
            building_name = room_info.get('building_name')
            room_number = room_info.get('room_number')

            # Add building name and room number to tenant data
            #data['building_name'] = building_name
            data['room_name'] = room_number

            # Proceed to create a tenant in the tenant app
            tenant_app_url = f"{TENANT_APP_URL}/api/Tenant/{email}"
            tenant_response = requests.put(tenant_app_url, json=data)
            return jsonify(tenant_response.json()), tenant_response.status_code
        else:
            return jsonify({'error': 'Room not available or does not exist'}), room_response.status_code
    except requests.RequestException as e:
        return jsonify({'error': f'Building app request failed: {str(e)}'}), 500

@app.route('/fetch_data/<email>')
def fetch_data(email):
    url1 = f"{BILLING_APP_URL}/api/billing/get_balance"
    url2 = f"{TENANT_APP_URL}/api/Tenant/{email}"

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        merged_response = loop.run_until_complete(get_data_from_urls(url1, url2, email))
        loop.close()
    except Exception as e:
        return jsonify({'error': f'Fetch request failed: {str(e)}'}), 500

    
    return jsonify(merged_response)
if __name__ == '__main__':
    CORS(app)
    app.run(host='0.0.0.0',port=5000,ssl_context='adhoc',debug=True)
