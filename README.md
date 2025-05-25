# 🚗 IVMS Installation Certificate Generator
This is a secure Flask-based web application for generating IVMS (In-Vehicle Monitoring System) installation certificates. Designed for authorized users, it fetches vehicle asset data from a database, dynamically fills out a certificate template, and allows the output to be printed or downloaded as a PDF.

# 🌐 Features
🔒 Secure Login with token-based authentication

🧾 Certificate Generation using dynamic HTML templates (Jinja2)

🛠️ Vehicle Data Integration from the backend

📄 Printable & Downloadable PDF View

🌍 Nginx Reverse Proxy with optional SSL (HTTPS) support

🖼️ Custom Branding with logo, stamp, and signature


#🚀 Technologies Used
Python + Flask

HTML/CSS (Jinja2 templating)

Nginx (with SSL support)

Waitress WSGI server

SQLite / SQLAlchemy (or any compatible DB)

Static assets for branding (logos, stamps, signatures)

# 🛠️ Setup Instructions
1. Clone the Repo
git clone https://github.com/your-username/ivms-certificate-generator.git
cd ivms-certificate-generator


2. Install Dependencies
pip install -r requirements.txt

3. Configure Environment Variables
DATABASE_URL=sqlite:///data.db
DEBUG=True

4. Run the Application
python app.py


Disclaimer: App does not contain any live connection to any database or API or personal information.

Or run with Waitress:
waitress-serve --host=127.0.0.1 --port=5000 app:app

5. Configure Nginx (Optional)
Use Nginx to serve the app over https://your-domain:8443 with reverse proxy settings and SSL.
