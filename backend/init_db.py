import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = int(os.environ.get("DB_PORT", 3306))
DB_NAME = os.environ.get("DB_NAME", "smart_meeting_db")

def setup_database():
    print(f">> Checking MySQL Server connection at {DB_HOST}:{DB_PORT} with user '{DB_USER}'...")
    try:
        # Connect to MySQL Server without specifying DB first
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        cursor = conn.cursor()
        print(">> Connected to MySQL Server successfully!")
        
        # Create database if not exists
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        print(f">> Database '{DB_NAME}' created / verified successfully.")
        conn.close()

        # Now import models and create tables
        from app import create_app
        from extensions import db
        app = create_app()
        with app.app_context():
            db.create_all()
            print(">> All 7 tables (users, teams, meetings, meeting_participants, tasks, decisions, notifications) created successfully in MySQL!")
        return True

    except pymysql.err.OperationalError as e:
        code, msg = e.args
        print(f"\n[MySQL Connection Error {code}]: {msg}")
        if code == 2003:
            print("\n>> MySQL Server is not running on port 3306.")
            print(">> Note: MySQL Workbench is only the management interface. You also need MySQL Server (or XAMPP MySQL) running on your PC.")
        elif code in (1045, 1698):
            print(f"\n>> Access denied for user '{DB_USER}'.")
            print(">> If you set a root password during MySQL installation, please add it to 'backend/.env':")
            print("   DB_PASSWORD=your_mysql_password")
        return False
    except Exception as e:
        print(f"\n[Error]: {e}")
        return False

if __name__ == '__main__':
    setup_database()
