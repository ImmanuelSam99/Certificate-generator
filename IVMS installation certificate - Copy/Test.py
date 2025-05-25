from flask import Flask, request, render_template_string
import requests
import json
from requests.auth import HTTPBasicAuth
import mysql.connector
app = Flask(__name__)

HTML_TEMPLATE = """
<!doctype html>
<html>
<head><title>Login</title></head>
<body>
  <h2>Login to API</h2>
  <form method="POST">
    <label>User ID:</label><br>
    <input type="text" name="username" required><br><br>
    <label>Password:</label><br>
    <input type="password" name="password" required><br><br>

    <button type="submit">Login</button>
  </form>

  {% if response %}
    <h3>Full API Response (Status: {{ status_code }})</h3>
    <pre>{{ response }}</pre>
  {% endif %}

  {% if token %}
    <h3>Extracted Token:</h3>
    <pre>{{ token }}</pre>
  {% endif %}

  {% if output %}
    <h3>Message:</h3>
    <p>{{ output }}</p>
  {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def login():
    response_text = None
    status_code = None
    token = None
    output = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        api_url = ""

        try:
            # Send both Basic Auth and JSON body
            response = requests.post(
                api_url,
                auth=HTTPBasicAuth(username, password),
                json={"user_id": username, "password": password},
            )
            status_code = response.status_code

            try:
                data = response.json()
                response_text = json.dumps(data, indent=4)
                token = data.get("response", {}).get("token")
                output = data.get("response", {}).get("output")
            except Exception:
                response_text = response.text

        except Exception as e:
            response_text = f"Error connecting to API or parsing response: {str(e)}"
            status_code = "N/A"

    return render_template_string(
        HTML_TEMPLATE,
        response=response_text,
        status_code=status_code,
        token=token,
        output=output,
    )

if __name__ == "__main__":
    app.run(debug=True)
