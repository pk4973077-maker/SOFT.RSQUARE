from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/start-project", methods=["GET", "POST"])
def start_project():

    if request.method == "POST":

        client_name = request.form.get("client_name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        client_type = request.form.get("client_type")
        organization = request.form.get("organization")
        city = request.form.get("city")

        services = request.form.getlist("services")

        project_name = request.form.get("project_name")
        requirements = request.form.get("requirements")
        budget = request.form.get("budget")

        if not all([client_name, email, phone, client_type, city]):
            return render_template(
                "start_project.html",
                error="Please fill all required fields."
            )

        if not services:
            return render_template(
                "start_project.html",
                error="Please select at least one service."
            )

        # Temporary confirmation.
        # Database storage will be added later.

        return render_template(
            "start_project.html",
            success=True,
            client_name=client_name
        )

    return render_template("start_project.html")


@app.route("/test")
def test():
    return {
        "status": "success",
        "message": "SOFT.RSQUARE Backend Connected Successfully!"
    }


if __name__ == "__main__":
    app.run(debug=True)