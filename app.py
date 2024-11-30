from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
from models import *
from flask_migrate import Migrate
from models import db, User, Service, Review, Rating, Booking, Payment, Notification  # Correct import of models
import click
app = Flask(__name__)

# Configuration for the database and Flask
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'  # Secret key for sessions and flash messages
app.config['SESSION_TYPE'] = 'filesystem'


db.init_app(app)
migrate = Migrate(app, db)

# Flask-Login Setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Define the User model
'''class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'customer', 'professional', 'admin'
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<User {self.username}>" '''


# @app.cli.command("create-admin")
# @click.argument("username")
# @click.argument("email")
# @click.argument("password")
# def create_admin(username, email, password):
#     """Create an admin user."""
#     if User.query.filter_by(username=username).first():
#         print(f"Admin user '{username}' already exists.")
#         return
#     hashed_password = generate_password_hash(password)
#     admin_user = User(
#         username=username,
#         email=email,
#         password=hashed_password,
#         role="admin",
#         name="Administrator",
#         active=True
#     )
#     db.session.add(admin_user)
#     db.session.commit()
#     print(f"Admin user '{username}' created successfully!")

# @app.cli.command("add-services")
# def add_services():
#     """Add demo services."""
#     services = [
#         {"name": "Cleaning Service", "description": "Professional house cleaning service.", "price": 50.0, "rating": 4.5},
#         {"name": "Plumbing Service", "description": "Fixing leaks and plumbing issues.", "price": 80.0, "rating": 4.7},
#         {"name": "Electrical Service", "description": "Electrical repairs and installations.", "price": 100.0, "rating": 4.8},
#     ]
#     for service_data in services:
#         if not Service.query.filter_by(name=service_data["name"]).first():
#             service = Service(**service_data)
#             db.session.add(service)
#             print(f"Service '{service_data['name']}' added successfully!")
#     db.session.commit()


# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    # print("user_id",user_id)
    return User.query.get(int(user_id))

# Route for the Homepage
@app.route('/')
def home():
    return render_template('home.html')

# Route for the Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Look for the user in the database
        user = User.query.filter_by(username=username).first()
        # print(user)
        if user and check_password_hash(user.password, password):  # Check password hash
            if not user.active:
                flash('Your account is blocked. Please contact the administrator.', 'danger')
                return redirect(url_for('login'))
            login_user(user)
            flash('Logged in successfully.', 'success')
            print(f"Current user: {current_user}")
            if user.role == 'customer':
                return redirect(url_for('customer_dashboard'))
            elif user.role == 'professional':
                return redirect(url_for('professional_dashboard'))
            elif user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login_signup.html', action='login')

# Route for the Admin Dashboard
@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('You must be an admin to access this page.', 'danger')
        return redirect(url_for('home'))

    # Fetch all users and services from the database
    users = User.query.all()
    services = Service.query.all()
    return render_template('admin_dashboard.html', users=users, services=services)

# Route for Customer Dashboard
@app.route('/customer_dashboard')
@login_required
def customer_dashboard():
    services = Service.query.all()  # Get all services
    professionals = User.query.filter_by(role='professional').all()  # Get all professionals
    if not services:
        flash('No services available. Please contact the administrator.', 'warning')
    
    # Fetch bookings for the current user
    bookings = Booking.query.filter_by(customer_id=current_user.id).all()
    upcoming_services = [booking for booking in bookings if booking.booking_status == 'upcoming']
    past_services = [booking for booking in bookings if booking.booking_status == 'completed']
    
    reviews = Review.query.filter_by(user_id=current_user.id).all()
    payments = Payment.query.filter_by(user_id=current_user.id).all()
    notifications = Notification.query.filter_by(user_id=current_user.id).all()

    return render_template('customer_dashboard.html', 
                           user=current_user, 
                           services=services,  # Pass the services to template
                           professionals=professionals,  # Pass the professionals to template
                           upcoming_services=upcoming_services,  # Pass the upcoming_services to template
                           past_services=past_services,  # Pass the past_services to template
                           reviews=reviews, 
                           payments=payments, 
                           notifications=notifications)

# Route for Professional Dashboard
@app.route('/professional_dashboard')
@login_required
def professional_dashboard():
    if current_user.role != 'professional':
        flash('You must be a professional to access this page.', 'danger')
        return redirect(url_for('home'))
    # Fetch chosen bookings for the current professional
    chosen_bookings = Booking.query.filter_by(professional_id=current_user.id, booking_status='upcoming').all()
    # Fetch completed bookings for the current professional
    completed_bookings = Booking.query.filter_by(professional_id=current_user.id, booking_status='completed').all()
    return render_template('professional_dashboard.html', user=current_user, chosen_bookings=chosen_bookings, completed_bookings=completed_bookings)

@app.route('/booking_action/<int:booking_id>', methods=['POST'])
@login_required
def booking_action(booking_id):
    if current_user.role != 'professional':
        flash('You must be a professional to take action on bookings.', 'danger')
        return redirect(url_for('home'))
    booking = Booking.query.get_or_404(booking_id)
    if booking.professional_id != current_user.id:
        flash('You can only take action on your own bookings.', 'danger')
        return redirect(url_for('home'))
    action = request.form['action']
    if action == 'complete':
        booking.booking_status = 'completed'
        booking.date_of_completion = datetime.utcnow()
    elif action == 'reject':
        booking.booking_status = 'rejected'
    db.session.commit()
    flash('Booking status updated successfully!', 'success')
    return redirect(url_for('professional_dashboard'))

# Route for the Signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        role = request.form['role']

        if password != confirm_password:
            flash('Passwords do not match', 'danger')
        else:
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, password=hashed_password, role=role, email=request.form['email'],name = request.form['name'])
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))

    return render_template('login_signup.html', action='signup')

# Route to logout the user
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# Route to edit user details (admin only)
@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.role != 'admin':
        flash('You must be an admin to edit user details.', 'danger')
        return redirect(url_for('home'))

    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        user.role = request.form['role']
        db.session.commit()
        flash('User details updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_user.html', user=user)

# Route to delete a user (admin only)
@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        flash('You must be an admin to delete users.', 'danger')
        return redirect(url_for('home'))

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    flash('User deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

# Route to add a new service (admin only)
@app.route('/add_service', methods=['GET', 'POST'])
@login_required
def add_service():
    if current_user.role != 'admin':
        flash('You must be an admin to add services.', 'danger')
        return redirect(url_for('home'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])

        new_service = Service(name=name, description=description, price=price)
        db.session.add(new_service)
        db.session.commit()

        flash('Service added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('add_service.html')

# Route to edit service details (admin only)
@app.route('/edit_service/<int:service_id>', methods=['GET', 'POST'])
@login_required
def edit_service(service_id):
    if current_user.role != 'admin':
        flash('You must be an admin to edit services.', 'danger')
        return redirect(url_for('home'))

    service = Service.query.get_or_404(service_id)

    if request.method == 'POST':
        service.name = request.form['name']
        service.description = request.form['description']
        service.price = float(request.form['price'])
        db.session.commit()
        flash('Service updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_service.html', service=service)

# Route to delete a service (admin only)
@app.route('/delete_service/<int:service_id>', methods=['POST'])
@login_required
def delete_service(service_id):
    if current_user.role != 'admin':
        flash('You must be an admin to delete services.', 'danger')
        return redirect(url_for('home'))

    service = Service.query.get_or_404(service_id)
    db.session.delete(service)
    db.session.commit()

    flash('Service deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

# Route to edit user profile
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = current_user

    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('customer_dashboard'))  # Redirect to customer dashboard or other appropriate route

    return render_template('edit_profile.html', user=user)


@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # Check if the current password is correct
        if not check_password_hash(current_user.password, current_password):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('change_password'))

        # Ensure the new password and confirmation match
        if new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
            return redirect(url_for('change_password'))

        # Update the password in the database
        current_user.password = generate_password_hash(new_password)
        db.session.commit()

        flash('Your password has been updated successfully!', 'success')
        return redirect(url_for('customer_dashboard'))  # Redirect to the dashboard or another page

    return render_template('change_password.html')  # Render the change password form


@app.route('/rate_service/<int:booking_id>', methods=['POST'])
@login_required
def rate_service(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    rating = request.form['rating']
    comment = request.form['comment']
    review = Review(booking_id=booking.id, user_id=current_user.id, rating=rating, comments=comment)
    db.session.add(review)
    db.session.commit()
    flash('Your rating has been submitted successfully!', 'success')
    return redirect(url_for('customer_dashboard'))


# Route to display the list of services
@app.route('/services')
def services():
    services_list = Service.query.all()  # Fetch all services from the database
    return render_template('services.html', services=services_list)

@app.route('/privacy_settings', methods=['GET', 'POST'])
@login_required
def privacy_settings():
    user = current_user

    if request.method == 'POST':
        user.settings.account_private = 'account_private' in request.form
        db.session.commit()
        flash('Privacy settings updated successfully!', 'success')
        return redirect(url_for('customer_dashboard'))

    return render_template('privacy_settings.html', user=user)


# Route to create a new user (admin only)
@app.route('/create_user', methods=['POST'])
@login_required
def create_user():
    if current_user.role != 'admin':
        flash('You must be an admin to create users.', 'danger')
        return redirect(url_for('home'))

    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    role = request.form['role']

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, email=email, password=hashed_password, role=role)
    db.session.add(new_user)
    db.session.commit()

    flash('User created successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

# Route to choose a service and create a booking
@app.route('/choose_service', methods=['POST'])
@login_required
def choose_service():
    service_id = request.form['service_id']
    professional_id = request.form['professional_id']
    service = Service.query.get_or_404(service_id)
    professional = User.query.get_or_404(professional_id)
    
    # Create a new booking
    new_booking = Booking(
        service_id=service.id,
        customer_id=current_user.id,
        professional_id=professional.id,
        booking_status='upcoming'
    )
    db.session.add(new_booking)
    db.session.commit()

    flash(f'You have chosen the service: {service.name} with professional: {professional.name}', 'success')
    return redirect(url_for('customer_dashboard'))

# Route for Admin to approve a service professional
@app.route('/approve_professional/<int:professional_id>', methods=['POST'])
@login_required
def approve_professional(professional_id):
    if current_user.role != 'admin':
        flash('You must be an admin to approve professionals.', 'danger')
        return redirect(url_for('home'))

    professional = User.query.get_or_404(professional_id)
    professional.active = True
    db.session.commit()
    flash('Professional approved successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

# Route for Admin to block a user
@app.route('/block_user/<int:user_id>', methods=['POST'])
@login_required
def block_user(user_id):
    if current_user.role != 'admin':
        flash('You must be an admin to block users.', 'danger')
        return redirect(url_for('home'))

    user = User.query.get_or_404(user_id)
    user.active = False
    db.session.commit()
    flash('User blocked successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

# Route for Admin to unblock a user
@app.route('/unblock_user/<int:user_id>', methods=['POST'])
@login_required
def unblock_user(user_id):
    if current_user.role != 'admin':
        flash('You must be an admin to unblock users.', 'danger')
        return redirect(url_for('home'))

    user = User.query.get_or_404(user_id)
    user.active = True
    db.session.commit()
    flash('User unblocked successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

# Route for Professional to accept/reject a service request
@app.route('/service_request/<int:request_id>/action', methods=['POST'])
@login_required
def service_request_action(request_id):
    if current_user.role != 'professional':
        flash('You must be a professional to take action on service requests.', 'danger')
        return redirect(url_for('home'))
    service_request = ServiceRequest.query.get_or_404(request_id)
    action = request.form['action']
    if action == 'accept':
        service_request.service_status = 'assigned'
        service_request.professional_id = current_user.id
    elif action == 'reject':
        service_request.service_status = 'rejected'
    db.session.commit()
    flash('Service request updated successfully!', 'success')
    return redirect(url_for('professional_dashboard'))

@app.route('/complete_service_request/<int:request_id>', methods=['POST'])
@login_required
def complete_service_request(request_id):
    if current_user.role != 'professional':
        flash('You must be a professional to complete service requests.', 'danger')
        return redirect(url_for('home'))
    service_request = ServiceRequest.query.get_or_404(request_id)
    if service_request.professional_id != current_user.id:
        flash('You can only complete your own service requests.', 'danger')
        return redirect(url_for('home'))
    service_request.service_status = 'completed'
    service_request.date_of_completion = datetime.utcnow()
    db.session.commit()
    flash('Service request marked as completed successfully!', 'success')
    return redirect(url_for('professional_dashboard'))

# Route for Customer to close a service request
@app.route('/close_service_request/<int:request_id>', methods=['POST'])
@login_required
def close_service_request(request_id):
    service_request = ServiceRequest.query.get_or_404(request_id)
    if service_request.customer_id != current_user.id:
        flash('You can only close your own service requests.', 'danger')
        return redirect(url_for('home'))

    service_request.service_status = 'closed'
    service_request.date_of_completion = datetime.utcnow()
    db.session.commit()
    flash('Service request closed successfully!', 'success')
    return redirect(url_for('customer_dashboard'))

# Route for Customer to create a new service request
@app.route('/create_service_request', methods=['POST'])
@login_required
def create_service_request():
    service_id = request.form['service_id']
    new_request = ServiceRequest(
        service_id=service_id,
        customer_id=current_user.id,
        service_status='requested'
    )
    db.session.add(new_request)
    db.session.commit()
    flash('Service request created successfully!', 'success')
    return redirect(url_for('customer_dashboard'))

# Route for searching services
@app.route('/search_services', methods=['GET'])
def search_services():
    query = request.args.get('query')
    services = Service.query.filter(Service.name.contains(query)).all()
    return render_template('services.html', services=services)

# Route for searching professionals (admin only)
@app.route('/search_professionals', methods=['GET'])
@login_required
def search_professionals():
    if current_user.role != 'admin':
        flash('You must be an admin to search professionals.', 'danger')
        return redirect(url_for('home'))

    query = request.args.get('query')
    professionals = User.query.filter(User.role == 'professional', User.name.contains(query)).all()
    return render_template('admin_dashboard.html', professionals=professionals)

@app.cli.command("populate-data")
def populate_data():
    """Populate the database with initial data."""
    # Add initial users
    users = [
        {"username": "admin2", "email": "admin2@example.com", "password": generate_password_hash("adminpass"), "role": "admin", "active": True,"name":"admin1"},
        {"username": "customer1", "email": "customer1@example.com", "password": generate_password_hash("customerpass"), "role": "customer", "active": True,"name":"customer1"},
        {"username": "professional1", "email": "professional1@example.com", "password": generate_password_hash("professionalpass"), "role": "professional", "active": True,"name":"professional1"},
    ]
    for user_data in users:
        if not User.query.filter_by(username=user_data["username"]).first():
            user = User(**user_data)
            db.session.add(user)
            print(f"User '{user_data['username']}' added successfully!")
    
    # Add initial services
    services = [
        {"name": "Cleaning Service", "description": "Professional house cleaning service.", "price": 50.0, "rating": 4.5},
        {"name": "Plumbing Service", "description": "Fixing leaks and plumbing issues.", "price": 80.0, "rating": 4.7},
        {"name": "Electrical Service", "description": "Electrical repairs and installations.", "price": 100.0, "rating": 4.8},
    ]
    for service_data in services:
        if not Service.query.filter_by(name=service_data["name"]).first():
            service = Service(**service_data)
            db.session.add(service)
            print(f"Service '{service_data['name']}' added successfully!")
    
    db.session.commit()

    # Add initial bookings and service requests
    customer = User.query.filter_by(username="customer1").first()
    professional = User.query.filter_by(username="professional1").first()
    service = Service.query.filter_by(name="Cleaning Service").first()

    if customer and professional and service:
        booking = Booking(
            service_id=service.id,
            customer_id=customer.id,
            professional_id=professional.id,
            booking_status='upcoming'
        )
        db.session.add(booking)
        print(f"Booking for service '{service.name}' added successfully!")

        service_request = ServiceRequest(
            service_id=service.id,
            customer_id=customer.id,
            professional_id=professional.id,
            service_status='requested'
        )
        db.session.add(service_request)
        print(f"Service request for service '{service.name}' added successfully!")

        db.session.commit()
        print("Database populated with initial bookings and service requests successfully!")

# Running the Flask app
if __name__ == '__main__':
    app.run(debug=False )
    app.run(port=5001)