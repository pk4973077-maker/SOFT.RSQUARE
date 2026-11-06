import os
import json
import logging
import psycopg2

from dotenv import load_dotenv
from flask import Flask, render_template, request

load_dotenv()

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)


def get_db_connection():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured.")

    return psycopg2.connect(
        database_url,
        sslmode="require"
    )


def create_table():
    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS client_requests (
                id SERIAL PRIMARY KEY,
                client_name VARCHAR(150) NOT NULL,
                email VARCHAR(255) NOT NULL,
                phone VARCHAR(30) NOT NULL,
                client_type VARCHAR(100) NOT NULL,
                organization VARCHAR(200),
                city VARCHAR(150) NOT NULL,
                services TEXT NOT NULL,
                project_name VARCHAR(200),
                requirements TEXT,
                budget VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        connection.commit()
        cursor.close()

    finally:
        connection.close()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/start-project", methods=["GET", "POST"])
def start_project():

    if request.method == "POST":

        client_name = request.form.get("client_name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        client_type = request.form.get("client_type", "").strip()
        organization = request.form.get("organization", "").strip()
        city = request.form.get("city", "").strip()

        services = request.form.getlist("services")

        project_name = request.form.get("project_name", "").strip()
        requirements = request.form.get("requirements", "").strip()
        budget = request.form.get("budget", "").strip()

        if not all([
            client_name,
            email,
            phone,
            client_type,
            city
        ]):
            return render_template(
                "start_project.html",
                error="Please fill all required fields."
            )

        if not services:
            return render_template(
                "start_project.html",
                error="Please select at least one service."
            )

        connection = None

        try:
            create_table()

            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute("""
                INSERT INTO client_requests (
                    client_name,
                    email,
                    phone,
                    client_type,
                    organization,
                    city,
                    services,
                    project_name,
                    requirements,
                    budget
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                client_name,
                email,
                phone,
                client_type,
                organization,
                city,
                json.dumps(services),
                project_name,
                requirements,
                budget
            ))

            connection.commit()
            cursor.close()

            return render_template(
                "start_project.html",
                success=True,
                client_name=client_name
            )

        except Exception:
            if connection:
                connection.rollback()

            app.logger.exception(
                "Client request could not be saved."
            )

            return render_template(
                "start_project.html",
                error="Something went wrong. Please try again later."
            )

        finally:
            if connection:
                connection.close()

    return render_template("start_project.html")


@app.route("/test")
def test():
    return {
        "status": "success",
        "message": "SOFT.RSQUARE Backend Connected Successfully!"
    }


@app.route("/test-db")
def test_db():

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT 1")
        cursor.fetchone()

        cursor.close()
        connection.close()

        return {
            "status": "success",
            "message": "Neon Database Connected Successfully!"
        }

    except Exception:
        app.logger.exception("Database connection test failed.")

        return {
            "status": "error",
            "message": "Database connection failed."
        }, 500


if __name__ == "__main__":
    app.run(debug=True)