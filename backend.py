from flask import Flask, request, jsonify
import sqlite3
import re
from flask_cors import CORS
from datetime import datetime, timedelta
import jwt

def is_valid_email(email):
    """ check email address"""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

app = Flask(__name__)
CORS(app)

#date like YYYY-MM-DD
def init_db():
    conn = sqlite3.connect('tenant.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tenants (
            email TEXT PRIMARY KEY, 
            gender TEXT CHECK(gender IN ('Male', 'Female')),
            building_name TEXT, 
            room_name TEXT,      
            phone_number TEXT,
            rent  INTEGER,
            lease_start_date TEXT, 
            lease_end_date TEXT,  
            identity TEXT CHECK(identity IN('Tenant', 'Manager'))
        )
    ''')
    conn.close()


@app.route('/token/<email>', methods=['GET'])
def generate_token(email):
    SECRET_KEY = '123456'
    token = jwt.encode({
        'sub': email,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(minutes=60)  # Token expires in 60 minutes
    }, SECRET_KEY, algorithm='HS256')   
    return jsonify(token=token), 200


@app.route('/api/Tenant', methods=['GET'])
def get_all_tenants():
    with sqlite3.connect('tenant.db') as conn:
        conn.row_factory = sqlite3.Row  # This enables column access by name: row['column_name']
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tenants')
        rows = cursor.fetchall()

        # Convert rows to dictionary format
        tenants = [dict(row) for row in rows]

    return jsonify(tenants)


@app.route('/api/Tenant', methods=['POST'])
def create_tenant():
    data = request.get_json()
    email = data.get('email')
    gender = data.get('gender')
    building_name = data.get('building_name', None)
    room_name = data.get('room_name', None)
    phone_number = data.get('phone_number')
    rent= data.get('rent',None)
    lease_start_date=data.get('lease_start_date')
    lease_end_date=data.get('lease_end_date',) 
    identity=data.get('identity')
    # Validate gender
    if gender not in ['Male', 'Female']:
        return jsonify({'error': 'Invalid gender'}), 400
    # Validate email
    if not is_valid_email(email):
        return jsonify({'error': 'Invalid email'}), 400
    # Validate identity
    if identity not in ['Tenant', 'Manager']:
        return jsonify({'error': 'Invalid identity'}), 400
    # Validate phone number
    if not (phone_number.isdigit() and len(phone_number) == 10):
        return jsonify({'error': 'Invalid phone number'}), 400
    # Convert lease dates from strings to datetime objects
    try:
        lease_start = datetime.strptime(lease_start_date, '%Y-%m-%d')
        lease_end = datetime.strptime(lease_end_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    # Validate lease
    if lease_end < lease_start:
        return jsonify({'error': 'Invalid lease date'}), 400

    try:
        with sqlite3.connect('tenant.db') as conn:
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO tenants (email, gender, building_name, room_name, phone_number,rent, 
                        lease_start_date, lease_end_date, identity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (email, gender, building_name, room_name, phone_number,rent, 
                  lease_start_date, lease_end_date, identity,))
            conn.commit()
            return jsonify({'message': 'Tenant added successfully'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Tenant with this ID already exists'}), 409
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/Tenant/<email>', methods=['GET'])
def get_tenant_by_id(email):
    try:
        with sqlite3.connect('tenant.db') as conn:
            conn.row_factory = sqlite3.Row  # This will enable column access by name
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM tenants WHERE email = ?", (email,))
            row = cursor.fetchone()

            if row is None:
                return jsonify({}), 200

            # Convert row to dictionary
            tenant = dict(row)
            return jsonify(tenant), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/api/Tenant/<email>', methods=['PUT'])
def update_tenant(email):
    data = request.get_json()
    gender = data.get('gender')
    building_name = data.get('building_name', None)
    room_name = data.get('room_name', None)
    phone_number = data.get('phone_number')
    rent= data.get('rent',None)
    lease_start_date=data.get('lease_start_date')
    lease_end_date=data.get('lease_end_date',) 
    identity=data.get('identity')
    # Validate gender
    if gender not in ['Male', 'Female']:
        return jsonify({'error': 'Invalid gender'}), 400
    # Validate email
    if not is_valid_email(email):
        return jsonify({'error': 'Invalid email'}), 400
    # Validate identity
    if identity not in ['Tenant', 'Manager']:
        return jsonify({'error': 'Invalid identity'}), 400
    # Validate phone number
    if not (phone_number.isdigit() and len(phone_number) == 10):
        return jsonify({'error': 'Invalid phone number'}), 400
    try:
        lease_start = datetime.strptime(lease_start_date, '%Y-%m-%d')
        lease_end = datetime.strptime(lease_end_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    # Validate lease
    if lease_end < lease_start:
        return jsonify({'error': 'Invalid lease date'}), 400
    # Update data in the database
    try:
        with sqlite3.connect('tenant.db') as conn:
            cur = conn.cursor()
            cur.execute('''
                UPDATE tenants
                SET gender = ?, building_name = ?, room_name = ?, phone_number = ?,
                rent = ?, lease_start_date= ?, lease_end_date= ?, identity= ?
                WHERE email= ?
            ''', (gender, building_name, room_name, phone_number, rent,
                  lease_start_date, lease_end_date, identity, email,))
            conn.commit()

            if cur.rowcount == 0:
                return jsonify({'error': 'Tenant not found'}), 404

            return jsonify({'message': 'Tenant updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/Tenant/<email>', methods=['DELETE'])
def delete_tenant(email):
    try:
        with sqlite3.connect('tenant.db') as conn:
            cursor = conn.cursor()

            cursor.execute("DELETE FROM tenants WHERE email = ?", (email,))
            conn.commit()

            if cursor.rowcount == 0:
                return jsonify({'error': 'Tenant not found'}), 404

            return jsonify({'message': 'Tenant deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/building/<string:building_name>/Tenant', methods=['GET'])
def get_tenants_in_building(building_name):
    try:
        with sqlite3.connect('tenant.db') as conn:
            conn.row_factory = sqlite3.Row  # Enable column access by name
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM tenants WHERE building_name = ?", (building_name,))
            rows = cursor.fetchall()

            if not rows:
                return jsonify({'message': 'No tenants found in this building'}), 200

            # Convert rows to dictionary format
            tenants = [dict(row) for row in rows]
            return jsonify(tenants), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0',port='5000',ssl_context='adhoc')
