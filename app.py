from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hostel.db'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['SESSION_COOKIE_SECURE'] = True  # Set to True for production

db = SQLAlchemy(app)


# Define Hostel Model
class Hostel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    single_rooms = db.Column(db.Integer)
    double_rooms = db.Column(db.Integer)
    self_contained = db.Column(db.Boolean)
    image = db.Column(db.String(200))
    price = db.Column(db.Integer)
    
# Define Booking Model
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostel_id = db.Column(db.Integer, db.ForeignKey('hostel.id'), nullable=False)
    name = db.Column(db.String(100))
    contact = db.Column(db.String(100))

# Check if file extension is allowed
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Routes
@app.route('/')
def index():
    # Get the category parameter from the URL
    category = request.args.get('category')

    # Define filter conditions based on the category parameter
    filter_conditions = []

    if category == 'self_contained':
        filter_conditions.append(Hostel.self_contained == True)
    elif category == 'not_self_contained':
        filter_conditions.append(Hostel.self_contained == False)

    # Query hostels based on filter conditions
    if filter_conditions:
        hostels = Hostel.query.filter(*filter_conditions).order_by(Hostel.id.desc()).all()
    else:
        hostels = Hostel.query.order_by(Hostel.id.desc()).all()


    return render_template('index.html', hostels=hostels)

# Route to the dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' in session:
        # Fetch all hostels from the database
        hostels = Hostel.query.order_by(Hostel.id.desc()).all()
        return render_template('dashboard.html', hostels=hostels)
    else:
        return redirect(url_for('login'))

# Route to login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    print("Entered login route")  # Add this line for debugging
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(f"Username entered: {username}")  # Add this line for debugging
        print(f"Password entered: {password}")  # Add this line for debugging
        print(f"Username from .env: {os.getenv('USERNAME')}")  # Add this line for debugging
        print(f"Password from .env: {os.getenv('PASSWORD')}")  # Add this line for debugging
        if username == os.getenv("USERNAME") and password == os.getenv("PASSWORD"):
            print("Login successful")  # Add this line for debugging
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            print("Login failed")  # Add this line for debugging
            flash('Invalid username or password', 'error')
    return render_template('login.html')



# Route to logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# Route to edit an existing hostel
@app.route('/edit_hostel/<int:hostel_id>', methods=['GET', 'POST'])
def edit_hostel(hostel_id):
    if 'username' in session:
        hostel = Hostel.query.get_or_404(hostel_id)
        if request.method == 'POST':
            hostel.name = request.form['name']
            hostel.single_rooms = request.form['single_rooms']
            hostel.double_rooms = request.form['double_rooms']
            hostel.self_contained = True if request.form.get('self_contained') else False
            hostel.price = request.form['price']
            db.session.commit()
            flash('Hostel updated successfully', 'success')
            return redirect(url_for('dashboard'))
        return render_template('edit_hostel.html', hostel=hostel)
    else:
        return redirect(url_for('login'))
    

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/hostel/<int:hostel_id>', methods=['GET', 'POST'])
def hostel_details(hostel_id):
    hostel = Hostel.query.get_or_404(hostel_id)
    if request.method == 'POST':
        name = request.form['name']
        contact = request.form['contact']
        booking = Booking(hostel_id=hostel.id, name=name, contact=contact)
        db.session.add(booking)
        db.session.commit()
        flash('Room booked successfully', 'success')
        return redirect(url_for('index'))  # Redirect to the homepage after booking

    return render_template('hostel_details.html', hostel=hostel)

# Route to delete an existing hostel
@app.route('/delete_hostel/<int:hostel_id>', methods=['POST'])
def delete_hostel(hostel_id):
    if 'username' in session:
        hostel = Hostel.query.get_or_404(hostel_id)
        db.session.delete(hostel)
        db.session.commit()
        flash('Hostel deleted successfully', 'success')
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))
    

@app.route('/add_hostel', methods=['GET', 'POST'])
def add_hostel():
    if 'username' in session:
        if request.method == 'POST':
            name = request.form['name']
            single_rooms = request.form['single_rooms']
            double_rooms = request.form['double_rooms']
            self_contained = True if request.form.get('self_contained') else False

            # Check if the post request has the file part
            if 'image' not in request.files:
                flash('No file part', 'error')
                return redirect(request.url)
            
            file = request.files['image']

            # If user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                flash('No selected file', 'error')
                return redirect(request.url)

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            else:
                flash('Invalid file type', 'error')
                return redirect(request.url)

            price = request.form['price']

            hostel = Hostel(name=name, single_rooms=single_rooms, double_rooms=double_rooms, self_contained=self_contained, image=image_path, price=price)
            db.session.add(hostel)
            db.session.commit()
            flash('Hostel added successfully', 'success')
            return redirect(url_for('index'))
        return render_template('add_hostel.html')
    else:
        return redirect(url_for('login'))
    

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
    

