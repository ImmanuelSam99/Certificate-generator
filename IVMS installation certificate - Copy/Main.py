from flask import Flask, request, render_template, redirect, url_for, session, jsonify
import requests, random
from requests.auth import HTTPBasicAuth
from datetime import timedelta, datetime
from functools import wraps
from waitress import serve
import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path='info.env')

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_strong_secret_key_here')
app.permanent_session_lifetime = timedelta(minutes=30)
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'


# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "auth_token" not in session:
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/", methods=["GET"])
def login_page():
    token = session.get("auth_token")
    if token:
        try:
            test_url = os.getenv('VEHICLE_API_URL', '')
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(test_url, headers=headers, timeout=5)
            if response.status_code == 200:
                return redirect(url_for("index"))
        except:
            pass

        # Token is invalid or API error, clear session
        session.clear()
        
    return render_template("login.html")


@app.route("/api/login", methods=["POST"])
def handle_login():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400
        
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    
    if not username or not password:
        return jsonify({"success": False, "error": "Username and password are required"}), 400

    try:
        api_url = os.getenv('AUTH_API_URL', '')
        response = requests.post(
            api_url,
            auth=HTTPBasicAuth(username, password),
            headers={'Content-Type': 'application/json'},
            json={"user_id": username, "password": password},
            timeout=10
        )
        
        if response.status_code != 200:
            error_msg = response.json().get("response", {}).get("output", "Invalid credentials")
            return jsonify({"success": False, "error": error_msg}), 401

        api_data = response.json()
        token = api_data.get("response", {}).get("token")
        
        if token:
            session.permanent = True
            session["auth_token"] = token
            session["username"] = username
            return jsonify({"success": True, "redirect": url_for("index")})
        
        return jsonify({"success": False, "error": "No token received"}), 401

    except requests.exceptions.RequestException as e:
        return jsonify({"success": False, "error": "Authentication service unavailable"}), 502
    except Exception as e:
        app.logger.error(f"Login error: {str(e)}")
        return jsonify({"success": False, "error": "An unexpected error occurred"}), 500



@app.route("/index")
@login_required
def index():
    username = session.get("username")
    token = session.get("auth_token")

    vehicles = []
    company_name = None

    try:
        # Call vehicle API using user_id
        vehicle_api_url = os.getenv('VEHICLE_API_URL', '')

        response = requests.get(
            vehicle_api_url,
            auth=HTTPBasicAuth(token, ''),  
            params={'user_id': username},   # Use user_id here
            timeout=10
        )

        if response.status_code != 200:
            raise Exception(f"API error: {response.status_code} - {response.text}")

        vehicles = response.json().get("response", [])

        
        if vehicles and 'company_name' in vehicles[0]:
            company_name = vehicles[0]['company_name']

    except Exception as e:
        app.logger.error(f"Error fetching vehicles for {username}: {e}")
        vehicles = []

    # Generate certificate number
    current_date_str = datetime.now().strftime("%d%m%Y")
    random_nn = f"{random.randint(1, 99):02d}"
    certificate_number = f"MST/{current_date_str}/{random_nn}"

    return render_template(
        "index.html",
        username=username,
        company_name=company_name,
        vehicles=vehicles,
        current_date=datetime.now().strftime("%Y-%m-%d"),
        certificate_number=certificate_number
    )




@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))


@app.route('/generate_certificate', methods=['POST', 'GET'])
@login_required
def generate_certificate():
    if request.method == 'GET':
        vehicle_data = {
            'reg_no': request.args.get('reg_no'),
            'chassis_no': request.args.get('chassis_no', ''),
            'imei': request.args.get('imei', ''),
            'sim_no': request.args.get('sim_no', ''),
            'company_name': request.args.get('company_name', '')
        }
    else:
        vehicle_data = {
            'reg_no': request.form['reg_no'],
            'chassis_no': request.form.get('chassis_no', ''),
            'imei': request.form.get('imei', ''),
            'sim_no': request.form.get('sim_no', ''),
            'company_name': request.form.get('company_name', '')
        }

    current_date = datetime.now().strftime('%Y-%m-%d')
    certificate_number = f"MST/{datetime.now().strftime('%d%m%Y')}/{random.randint(1, 99):02d}"
    
    rendered_html = render_template(
        "page.html",
        vehicle=vehicle_data,
        current_date=current_date,
        certificate_number=certificate_number
    )

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'html': rendered_html,
            'current_date': current_date,
            'certificate_number': certificate_number
        })
    
    return rendered_html


@app.route("/vehicles_json")
@login_required
def vehicles_json():
    username = session.get("username")
    token = session.get("auth_token")
    app.logger.info(f"Fetching vehicles for user: {username} with token: {token}")

    try:
        vehicle_api_url = os.getenv('VEHICLE_API_URL', '')
        response = requests.get(
            vehicle_api_url,
            auth=HTTPBasicAuth(token, ''),
            params={'user_id': username},
            timeout=10
        )
        app.logger.info(f"API response status: {response.status_code}")
        response.raise_for_status()
        return jsonify(response.json())

    except Exception as e:
        app.logger.error(f"Error fetching vehicles JSON for {username}: {e}")
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=os.getenv('DEBUG', 'False') == 'True')
    #serve(app, host='127.0.0.1', port=5000)



