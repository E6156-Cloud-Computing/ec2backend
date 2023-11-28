from flask import Flask, request, jsonify
import sqlite3
app = Flask(__name__)


def init_db():
    conn = sqlite3.connect('tenant.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tenants (
            tenant_id INTEGER PRIMARY KEY, 
            gender TEXT CHECK(gender IN ('Male', 'Female')),
            building_name TEXT, 
            room_name TEXT,      
            phone_number TEXT
        )
    ''')
    conn.close()

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
    tenant_id = data.get('tenant_id')
    gender = data.get('gender')
    building_name = data.get('building_name', None)
    room_name = data.get('room_name', None)
    phone_number = data.get('phone_number')

    # Validate gender
    if gender not in ['Male', 'Female']:
        return jsonify({'error': 'Invalid gender'}), 400

    # Validate phone number
    if not (phone_number.isdigit() and len(phone_number) == 10):
        return jsonify({'error': 'Invalid phone number'}), 400
    try:
        with sqlite3.connect('tenant.db') as conn:
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO tenants (tenant_id, gender, building_name, room_name, phone_number)
                VALUES (?, ?, ?, ?, ?)
            ''', (tenant_id, gender, building_name, room_name, phone_number))
            conn.commit()
            return jsonify({'message': 'Tenant added successfully'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Tenant with this ID already exists'}), 409
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/Tenant/<int:tenant_id>', methods=['GET'])
def get_tenant_by_id(tenant_id):
    try:
        with sqlite3.connect('tenant.db') as conn:
            conn.row_factory = sqlite3.Row  # This will enable column access by name
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM tenants WHERE tenant_id = ?", (tenant_id,))
            row = cursor.fetchone()

            if row is None:
                return jsonify({'error': 'Tenant not found'}), 404

            # Convert row to dictionary
            tenant = dict(row)
            return jsonify(tenant), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@app.route('/api/Tenant/<int:tenant_id>', methods=['PUT'])
def update_tenant(tenant_id):
    data = request.get_json()
    gender = data.get('gender')
    building_name = data.get('building_name', None)
    room_name = data.get('room_name', None)
    phone_number = data.get('phone_number')

    # Validate gender
    if gender not in ['Male', 'Female']:
        return jsonify({'error': 'Invalid gender'}), 400

    # Validate phone number
    if not (phone_number.isdigit() and len(phone_number) == 10):
        return jsonify({'error': 'Invalid phone number'}), 400

    # Update data in the database
    try:
        with sqlite3.connect('tenant.db') as conn:
            cur = conn.cursor()
            cur.execute('''
                UPDATE tenants
                SET gender = ?, building_name = ?, room_name = ?, phone_number = ?
                WHERE tenant_id = ?
            ''', (gender, building_name, room_name, phone_number, tenant_id))
            conn.commit()

            if cur.rowcount == 0:
                return jsonify({'error': 'Tenant not found'}), 404

            return jsonify({'message': 'Tenant updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/Tenant/<int:tenant_id>', methods=['DELETE'])
def delete_tenant(tenant_id):
    try:
        with sqlite3.connect('tenant.db') as conn:
            cursor = conn.cursor()

            cursor.execute("DELETE FROM tenants WHERE tenant_id = ?", (tenant_id,))
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
    app.run(debug=True)