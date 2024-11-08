import psycopg2
import time
from flask import Flask, request, jsonify

app = Flask(__name__)

# Database connection configuration
DB_CONFIG = {
    "dbname": "crud_app",
    "user": "postgres",
    "password": "test123",
    "host": "db",  # Use "db" here if you're using Docker containers and the db container name
    "port": "5432",
}

# Max retries for the connection attempt
MAX_RETRIES = 5
RETRY_DELAY = 3  # Seconds between retries

# Ensure a fresh connection if needed
def get_db_connection():
    global conn
    if conn.closed:
        retry_count = 0
        while retry_count < MAX_RETRIES:
            try:
                conn = psycopg2.connect(**DB_CONFIG)
                print("Database connection established")
                break  # Connection successful, exit the loop
            except psycopg2.OperationalError as e:
                retry_count += 1
                print(f"Connection attempt {retry_count} failed: {e}")
                if retry_count < MAX_RETRIES:
                    print(f"Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    print("Max retries reached. Could not connect to the database.")
                    raise  # Re-raise the error if max retries are reached

# Establish initial connection
conn = psycopg2.connect(**DB_CONFIG)

# Function to create the items table if it doesn't exist
def initialize_database():
    get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT
            )
        """)
        conn.commit()
        print("Table 'items' is ready")

# Run database initialization at application start
initialize_database()

@app.route('/')
def index():
    return app.send_static_file('index.html')

def create_item(name, description):
    get_db_connection()
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO items (name, description) VALUES (%s, %s) RETURNING id",
            (name, description)
        )
        conn.commit()
        item_id = cur.fetchone()[0]
        return item_id

def get_all_items():
    get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM items")
        items = cur.fetchall()
        items_list = [{'id': item[0], 'name': item[1], 'description': item[2]} for item in items]
        return items_list

def update_item(item_id, name, description):
    get_db_connection()
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE items SET name = %s, description = %s WHERE id = %s",
            (name, description, item_id)
        )
        conn.commit()

def delete_item(item_id):
    get_db_connection()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM items WHERE id = %s", (item_id,))
        conn.commit()

# Flask Routes
@app.route('/items', methods=['GET'])
def api_get_items():
    items = get_all_items()
    return jsonify(items)

@app.route('/items', methods=['POST'])
def api_create_item():
    data = request.get_json()
    item_id = create_item(data['name'], data['description'])
    return jsonify({'message': 'Item created', 'item_id': item_id})

@app.route('/items/<int:item_id>', methods=['PUT'])
def api_update_item(item_id):
    data = request.get_json()
    update_item(item_id, data['name'], data['description'])
    return jsonify({'message': 'Item updated'})

@app.route('/items/<int:item_id>', methods=['DELETE'])
def api_delete_item(item_id):
    delete_item(item_id)
    return jsonify({'message': 'Item deleted'})

# Close the database connection when the application context ends
@app.teardown_appcontext
def close_connection(exception):
    global conn
    if conn and not conn.closed:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
