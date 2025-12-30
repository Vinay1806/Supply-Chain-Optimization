from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import pandas as pd

app= Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Vinay@1806'
app.config['MYSQL_DB'] = 'supply_chain_erp'
app.config['SECRET_KEY'] = 'secret-key'

mysql = MySQL(app)

@app.route('/')
def dashboard():
    cur= mysql.connection.cursor()

    cur.execute("select COUNT(*) from inventory")
    inventory_count= cur.fetchone()[0]

    cur.execute("select COUNT(*) from purchase_orders where status = 'pending'")
    pending_orders= cur.fetchone()[0]

    cur.execute("select COUNT(*) from suppliers")
    suppliers_count= cur.fetchone()[0]

    cur.close()

    return render_template('dashboard.html', inventory_count=inventory_count,
                                            pending_orders= pending_orders,
                                            suppliers_count= suppliers_count)

@app.route('/inventory')
def inventory():
    cur= mysql.connection.cursor()
    cur.execute("select * from inventory")
    inventory_items= cur.fetchall()

    cur.execute("select supplier_id, name from suppliers")
    all_suppliers= cur.fetchall()

    cur.close()
    return render_template('inventory.html', inventory= inventory_items, all_suppliers= all_suppliers)

from MySQLdb.cursors import DictCursor

@app.route('/orders')
def orders():
    cur = mysql.connection.cursor()

    # Suppliers for dropdown
    cur.execute("SELECT supplier_id, name FROM suppliers")
    all_suppliers = cur.fetchall()

    # Inventory for dropdown
    cur.execute("SELECT id, name, quantity FROM inventory")
    inventory = cur.fetchall()

    cur.execute("""
        SELECT po.order_id, po.created_at, po.status,
               s.name AS supplier, i.name AS item, oi.quantity
        FROM purchase_orders po
        JOIN suppliers s ON po.supplier_id = s.supplier_id
        JOIN order_items oi ON po.order_id = oi.order_id
        JOIN inventory i ON oi.item_id = i.id
        ORDER BY po.created_at DESC
    """)
    orders = cur.fetchall()

    # Show only recent 10
    recent_orders = orders[:10]

    cur.close()

    return render_template(
        'orders.html',
        orders=recent_orders,
        all_suppliers=all_suppliers,
        inventory=inventory
    )

@app.route("/create_order", methods=["POST"])
def create_order():
    if request.method== 'POST':
        cur = mysql.connection.cursor()

        supplier_id = request.form["supplier_id"]
        item_id = request.form["item_id"] 
        quantity = request.form["quantity"]

        cur.execute("""
            INSERT INTO purchase_orders (supplier_id, item_id, quantity, status, created_at)
            VALUES (%s, %s, %s, %s, NOW())
        """, (supplier_id, item_id, quantity, "pending"))
        order_id= cur.lastrowid

        cur.execute("""
            INSERT INTO order_items (order_id, item_id, quantity)
            VALUES (%s, %s, %s)
        """, (order_id, item_id,quantity))


        mysql.connection.commit()
        cur.close()

    return redirect(url_for("orders"))

@app.route('/update_order_status/<int:order_id>/<status>')
def update_order_status(order_id, status):
    cur = mysql.connection.cursor()

    cur.execute("UPDATE purchase_orders SET status = %s WHERE order_id = %s", (status, order_id))

    if status == "completed":
        cur.execute("""
            SELECT oi.item_id, oi.quantity, i.price
            FROM order_items oi
            JOIN inventory i ON oi.item_id = i.id
            WHERE oi.order_id = %s
        """, (order_id,))
        order_items = cur.fetchall()

        for item_id, qty, price in order_items:
            cur.execute("""
                UPDATE inventory
                SET quantity = quantity + %s
                WHERE id = %s
            """, (qty, item_id))

    mysql.connection.commit()
    cur.close()

    flash(f"Order {order_id} marked as {status}")
    return redirect(url_for('orders'))

    
@app.route('/suppliers')
def suppliers():
    cur= mysql.connection.cursor()

    cur.execute("select * from suppliers")
    suppliers= cur.fetchall()
    cur.close()
    return render_template('suppliers.html',suppliers= suppliers)


@app.route('/add_supplier',methods= ['POST'])
def add_supplier():
    if request.method== 'POST':
        name= request.form['name']
        contact= request.form['contact']
        email= request.form['email']
        address= request.form['address']

        cur= mysql.connection.cursor()
        cur.execute("""insert into suppliers (name,contact,email,address)
                    values (%s, %s, %s, %s)""", (name,contact,email,address))
        
        mysql.connection.commit()
        cur.close()

        flash('Supplier added successfully!')
        return redirect(url_for('suppliers'))

@app.route('/production', methods=['GET', 'POST'])
def production():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute("SELECT * FROM productts")
    products = cursor.fetchall()

    if request.method == 'POST':
        product_id = request.form['product_id']
        product_qty = int(request.form['product_qty'])  

        cursor.execute("""
            SELECT pc.item_id, pc.quantity_required AS required_qty, 
            i.name, i.quantity AS available_qty
            FROM product_components pc
            JOIN inventory i ON pc.item_id = i.id
            WHERE pc.product_id = %s
        """, (product_id,))

        components = cursor.fetchall()

        enough_stock = True
        for c in components:
            required = c['required_qty'] * product_qty
            if c['available_qty'] < required:
                enough_stock = False
                break

        if not enough_stock:
            flash("Not enough stock to produce this product!", "error")
        else:
            for c in components:
                required = c['required_qty'] * product_qty
                cursor.execute(
                    "UPDATE inventory SET quantity = quantity - %s WHERE id = %s",
                    (required, c['item_id'])
                )

            cursor.execute(
                "INSERT INTO production_log (product_id, product_name, quantity) VALUES (%s, %s, %s)",
                (product_id, next(p['product_name'] for p in products if str(p['product_id']) == str(product_id)), product_qty)
            )

            mysql.connection.commit()
            flash("Product manufactured successfully!", "success")

        return redirect(url_for('production'))
    
    query = "select * from production_log order by manufactured_at desc limit 10"
    df= pd.read_sql(query,mysql.connection)

    history_html = df.to_html(classes= "table table-stripped", index=False)

    return render_template('production.html', products=products,history_html = history_html)

if __name__ == '__main__':
    app.run(debug= True)
    
