from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)  # <-- Added Flask-Migrate support

# -----------------------------
# Database Models
# -----------------------------
class Product(db.Model):
    product_id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    threshold = db.Column(db.Integer, default=5)  # Low-stock threshold

class Location(db.Model):
    location_id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class ProductMovement(db.Model):
    movement_id = db.Column(db.String(50), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    from_location = db.Column(db.String(50), db.ForeignKey('location.location_id'), nullable=True)
    to_location = db.Column(db.String(50), db.ForeignKey('location.location_id'), nullable=True)
    product_id = db.Column(db.String(50), db.ForeignKey('product.product_id'), nullable=False)
    qty = db.Column(db.Integer, nullable=False)

# -----------------------------
# Routes
# -----------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/products')
def products():
    all_products = Product.query.all()
    return render_template('products.html', products=all_products)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        product_id = request.form['product_id']
        name = request.form['name']
        threshold = int(request.form['threshold'])
        db.session.add(Product(product_id=product_id, name=name, threshold=threshold))
        db.session.commit()
        return redirect(url_for('products'))
    return render_template('product_form.html')

@app.route('/delete_product/<product_id>', methods=['POST'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    ProductMovement.query.filter_by(product_id=product_id).delete()
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('products'))

@app.route('/locations')
def locations():
    all_locations = Location.query.all()
    return render_template('locations.html', locations=all_locations)

@app.route('/add_location', methods=['GET', 'POST'])
def add_location():
    if request.method == 'POST':
        location_id = request.form['location_id']
        name = request.form['name']
        db.session.add(Location(location_id=location_id, name=name))
        db.session.commit()
        return redirect(url_for('locations'))
    return render_template('location_form.html')

@app.route('/delete_location/<location_id>', methods=['POST'])
def delete_location(location_id):
    location = Location.query.get_or_404(location_id)
    ProductMovement.query.filter(
        (ProductMovement.from_location == location_id) |
        (ProductMovement.to_location == location_id)
    ).delete()
    db.session.delete(location)
    db.session.commit()
    return redirect(url_for('locations'))

@app.route('/movements')
def movements():
    all_movements = ProductMovement.query.all()
    products = {p.product_id: p.name for p in Product.query.all()}
    locations = {l.location_id: l.name for l in Location.query.all()}
    return render_template('movements.html', movements=all_movements, products=products, locations=locations)

@app.route('/add_movement', methods=['GET', 'POST'])
def add_movement():
    products = Product.query.all()
    locations = Location.query.all()
    if request.method == 'POST':
        movement_id = request.form['movement_id']
        product_id = request.form['product_id']
        from_location = request.form.get('from_location') or None
        to_location = request.form.get('to_location') or None
        qty = int(request.form['qty'])
        db.session.add(ProductMovement(
            movement_id=movement_id,
            product_id=product_id,
            from_location=from_location,
            to_location=to_location,
            qty=qty
        ))
        db.session.commit()
        return redirect(url_for('movements'))
    return render_template('movement_form.html', products=products, locations=locations)

@app.route('/delete_movement/<movement_id>', methods=['POST'])
def delete_movement(movement_id):
    movement = ProductMovement.query.get_or_404(movement_id)
    db.session.delete(movement)
    db.session.commit()
    return redirect(url_for('movements'))

@app.route('/report')
def report():
    products = Product.query.all()
    locations = Location.query.all()
    report_data = []

    for product in products:
        for location in locations:
            qty_in = db.session.query(db.func.sum(ProductMovement.qty)) \
                .filter_by(product_id=product.product_id, to_location=location.location_id) \
                .scalar() or 0
            qty_out = db.session.query(db.func.sum(ProductMovement.qty)) \
                .filter_by(product_id=product.product_id, from_location=location.location_id) \
                .scalar() or 0
            balance = qty_in - qty_out
            if balance != 0:
                report_data.append({
                    'product': product.name,
                    'warehouse': location.name,
                    'qty': balance,
                    'low_stock': balance < product.threshold
                })

    return render_template('report.html', report_data=report_data)

# -----------------------------
# Run App
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)
