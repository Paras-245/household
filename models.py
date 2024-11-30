from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
db = SQLAlchemy()
from werkzeug.security import generate_password_hash, check_password_hash
class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    price = db.Column(db.Float, nullable=False)
    rating = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), default='pending')
    time_required = db.Column(db.String(50), nullable=True)  # Add time_required column

    def __repr__(self):
        return f"<Service {self.name}, Price {self.price}>"

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    date_of_booking = db.Column(db.DateTime, default=datetime.utcnow)
    date_of_completion = db.Column(db.DateTime, nullable=True)
    booking_status = db.Column(db.String(20), default='booked')
    remarks = db.Column(db.String(500), nullable=True)
    service_status = db.Column(db.String(20), default='requested')  # Add service_status column

    # Relationships
    customer = db.relationship('User', foreign_keys=[customer_id], backref='customer_bookings')
    professional = db.relationship('User', foreign_keys=[professional_id], backref='professional_bookings')
    service = db.relationship('Service', backref='bookings')

    def __repr__(self):
        return f"<Booking {self.id}, Service {self.service_id}, Status {self.booking_status}>"


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)
    profile_picture = db.Column(db.String(200), nullable=True)
    description = db.Column(db.String(500), nullable=True)
    service_type = db.Column(db.String(100), nullable=True)
    experience = db.Column(db.Integer, nullable=True)

    # Relationships
    # reviews = db.relationship('Review', backref='customer', lazy=True)
    documents = db.relationship('ProfessionalDocument', backref='professional', lazy=True)
    ratings = db.relationship('Rating', backref='user', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)
    settings = db.relationship('UserSettings', backref='user', uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"<User {self.username}, Role {self.role}>"


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Foreign key linking to User
    rating = db.Column(db.Integer, nullable=False)  # Rating from 1 to 5
    comments = db.Column(db.String(500), nullable=True)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    booking = db.relationship('Booking', backref='reviews', lazy=True)
    user = db.relationship('User', backref='reviews', lazy=True)  # Backref to User

    def __repr__(self):
        return f"<Review {self.rating} for Booking {self.booking_id}>"



class ProfessionalDocument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    professional_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    document_type = db.Column(db.String(100), nullable=False)
    document_url = db.Column(db.String(200), nullable=False)
    date_uploaded = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ProfessionalDocument {self.document_type}>"


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date_of_payment = db.Column(db.DateTime, default=datetime.utcnow)
    payment_method = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationship
    booking = db.relationship('Booking', backref='payments', lazy=True)
    user = db.relationship('User', backref='payments', lazy=True) 
    def __repr__(self):
        return f"<Payment {self.id} for Booking {self.booking_id}>"


class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer, db.ForeignKey('payment.id'), nullable=False)
    invoice_date = db.Column(db.DateTime, default=datetime.utcnow)
    invoice_url = db.Column(db.String(200), nullable=False)

    # Relationship
    payment = db.relationship('Payment', backref='invoice', lazy=True)

    def __repr__(self):
        return f"<Invoice {self.id}>"


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    date_sent = db.Column(db.DateTime, default=datetime.utcnow)
    notification_type = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<Notification {self.notification_type}>"


class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(500))

    def __repr__(self):
        return f"<Rating {self.rating}>"


class UserSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    dark_mode = db.Column(db.Boolean, default=False)
    two_factor_enabled = db.Column(db.Boolean, default=False)
    account_private = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    last_ip = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"<UserSettings {self.id}>"


class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    date_of_request = db.Column(db.DateTime, default=datetime.utcnow)
    date_of_completion = db.Column(db.DateTime, nullable=True)
    service_status = db.Column(db.String(20), default='requested')
    remarks = db.Column(db.String(500), nullable=True)
    # Relationships
    customer = db.relationship('User', foreign_keys=[customer_id], backref='customer_requests')
    professional = db.relationship('User', foreign_keys=[professional_id], backref='professional_requests')
    service = db.relationship('Service', backref='requests')
    def __repr__(self):
        return f"<ServiceRequest {self.id}, Service {self.service_id}, Status {self.service_status}>"
