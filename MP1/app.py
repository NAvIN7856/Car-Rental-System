from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
import json
from datetime import datetime, timedelta


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Load initial data from JSON files
with open('MP1/data/users.json', 'r') as users_file:
    users = json.load(users_file)

# Load car data from cars.json
with open('MP1/data/cars.json', 'r') as json_file:
    cars_data = json.load(json_file)
    
    
with open('MP1/data/history.json', 'r') as history_file:
    history_data = json.load(history_file)



# User Registration and Authentication
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Validate and store the user data (you should add more validation and hashing)
        users[username] = {'password': password}
        with open('MP1/data/users.json', 'w') as users_file:
            json.dump(users, users_file)
        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))
    return render_template('registration.html')





@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if users.get(username) and users[username]['password'] == password:
            session['username'] = username
            flash('Login successful.')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html')





@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))




# Browse and Rent Cars
@app.route('/')
def home():
    if 'username' in session:
        return render_template('home.html', cars=cars_data)
    else:
        return redirect(url_for('login'))
    
    
@app.route('/cars')
def cars():
    if 'username' in session:
        return render_template('cars.html', cars=cars_data)
    else:
        flash('Please log in to rent a car', 'warning')
        return redirect(url_for('login'))


















# Check car availability for a given date range
def is_car_available(car_id, start_date, end_date):
    # Check if the car is available for the given dates
    for car in cars_data:
        if car['id'] == int(car_id):
            availability = car['availability']
            for reservation in availability:
                reservation_start = datetime.strptime(reservation['start_date'], '%Y-%m-%d')
                reservation_end = datetime.strptime(reservation['end_date'], '%Y-%m-%d')
                if start_date < reservation_end and end_date > reservation_start:
                    return False
            return True

@app.route('/reserve/<car_id>', methods=['POST'])
def reserve(car_id):
    if request.method == 'POST':
        car = next(car for car in cars_data if car['id'] == int(car_id))
        name = request.form['name']
        email = request.form['email']
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')

        # Check car availability
        if is_car_available(car_id, start_date, end_date):
            # Update car availability
            update_car_availability(car_id, start_date, end_date)
            
            # Generate reservation history
            reservation_data = {
                'car_id': car['id'],
                'name': name,
                'email': email,
                'make': car['make'],
                'model': car['model'],
                'year': car['year'],
                'price': car['price'],
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
            }
            history_data.append(reservation_data)
            with open('MP1/data/history.json', 'w') as f:
                json.dump(history_data, f, indent=2)
            
            return redirect(url_for('history'))
        else:
            return "Car is unavailable for the selected dates"

def update_car_availability(car_id, start_date, end_date):
    # Update car availability for the reserved dates
    for car in cars_data:
        if car['id'] == int(car_id):
            availability = {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d')
            }
            car['availability'].append(availability)
            with open('MP1/data/cars.json', 'w') as f:
                json.dump(cars_data, f, indent=2)

@app.route('/history')
def history():
    if 'username' in session:
        return render_template('history.html', history=history_data)
    else:
        flash('Please log in to rent a car', 'warning')
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
