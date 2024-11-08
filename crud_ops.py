def create_item(name, description, cur, conn):
    cur.execute(
        "INSERT INTO items (name, description) VALUES (%s, %s) RETURNING id",
        (name, description)
    )
    conn.commit()
    item_id = cur.fetchone()[0]
    print(f"Item created with ID: {item_id}")

def get_all_items(cur):
    cur.execute("SELECT * FROM items")
    items = cur.fetchall()
    for item in items:
        print(item)

def get_item_by_id(item_id, cur):
    cur.execute("SELECT * FROM items WHERE id = %s", (item_id,))
    item = cur.fetchone()
    print(item)

def update_item(item_id, name, description, cur, conn):
    cur.execute(
        "UPDATE items SET name = %s, description = %s WHERE id = %s",
        (name, description, item_id)
    )
    conn.commit()
    print(f"Item with ID {item_id} updated.")

def delete_item(item_id, cur, conn):
    cur.execute("DELETE FROM items WHERE id = %s", (item_id,))
    conn.commit()
    print(f"Item with ID {item_id} deleted.")

def reset_table(cur, conn):
    cur.execute("TRUNCATE items RESTART IDENTITY;")
    conn.commit()
    print("Table cleared, and ID sequence reset to start from 1.")

