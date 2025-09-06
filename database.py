import mysql.connector
import hashlib
import datetime

DB_CONFIG={
    'host':'localhost',
    'user':'root',
    'password':'ash177125',
    'database':'ruet_hms'
}

def setup_database():
    conn=mysql.connector.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password']
    )
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
    cursor.execute(f"USE {DB_CONFIG['database']}")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        full_name VARCHAR(100) NOT NULL,
        user_type ENUM('admin','student') NOT NULL,
        roll_number VARCHAR(20),
        department VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS halls (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(50) UNIQUE NOT NULL,
        total_rooms INT NOT NULL DEFAULT 10,
        available_rooms INT NOT NULL DEFAULT 10
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS room_allocations (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        hall_id INT NOT NULL,
        room_number INT NOT NULL,
        allocation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT TRUE,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (hall_id) REFERENCES halls(id),
        UNIQUE KEY unique_room (hall_id, room_number, is_active)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        amount DECIMAL(10, 2) NOT NULL,
        payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS meal_tokens (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        hall_id INT NOT NULL,
        meal_type ENUM('lunch', 'dinner') NOT NULL,
        token_date DATE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (hall_id) REFERENCES halls(id),
        UNIQUE KEY unique_meal_token (user_id,hall_id,meal_type,token_date)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        hall_id INT NOT NULL,
        status ENUM('pending','approved','rejected') DEFAULT 'pending',
        application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        approval_date TIMESTAMP NULL,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (hall_id) REFERENCES halls(id)
    )
    """)
    
    hall_names=['Selim','Zia','Hamid','Shahidul','Bonggobondhu']
    for hall_name in hall_names:
        cursor.execute(
            "INSERT IGNORE INTO halls (name,total_rooms,available_rooms) VALUES (%s,%s,%s)",
            (hall_name,10,10)
        )
    
    conn.commit()
    cursor.close()
    conn.close()

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def authenticate_user(username, password):
    conn=get_db_connection()
    cursor=conn.cursor(dictionary=True)
    hashed_password=hashlib.sha256(password.encode()).hexdigest()
    
    cursor.execute(
        "SELECT * FROM users WHERE username=%s AND password= %s",
        (username,hashed_password)
    )
    
    user=cursor.fetchone()
    cursor.close()
    conn.close()
    
    return user



def register_user(username,password,full_name,user_type,roll_number=None,department=None):
    conn=get_db_connection()
    cursor=conn.cursor()
    
    try:
        hashed_password=hashlib.sha256(password.encode()).hexdigest()
        cursor.execute(
            "INSERT INTO users (username,password,full_name,user_type,roll_number,department) VALUES (%s,%s,%s,%s,%s,%s)",
            (username,hashed_password,full_name,user_type,roll_number,department)
        )
        conn.commit()
        success = True
        message = "User registered successfully"
    except mysql.connector.Error as err:
        success = False
        if err.errno == 1062:
            message = "Username already exists"
        else:
            message = f"Database error: {err}"
    
    cursor.close()
    conn.close()
    
    return success,message

def get_halls():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM halls")
    halls=cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return halls
def hall_name(hall_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM halls
        WHERE hall_id = %s
    """, (hall_id,))
    room = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return room

def get_user_allocation(student_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM room_allocations 
        WHERE user_id = %s AND is_active = TRUE
    """, (student_id,))
    room = cursor.fetchone()
    cursor.close()
    conn.close()
    return room

def get_application(stu_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM applications 
        WHERE user_id = %s AND status = 'pending'
    """,(stu_id,))
    room = cursor.fetchone()
    cursor.close()
    conn.close()
    return room

def get_student_room(student_id, hall_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM room_allocations 
        WHERE user_id = %s AND hall_id = %s AND is_active = TRUE
    """, (student_id, hall_id))
    room = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return room


def apply_for_room(student_id, hall_id):
    conn=get_db_connection()
    cursor=conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO applications (user_id, hall_id) VALUES (%s, %s)",
            (student_id, hall_id)
        )
        conn.commit()
        success=True
    except mysql.connector.Error:
        success=False
    cursor.close()
    conn.close()
    
    return success

def get_student_payments(student_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute(
        "SELECT * FROM payments WHERE user_id = %s ORDER BY payment_date DESC",
        (student_id,)
    )
    payments = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return payments

def make_payment(student_id, amount):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO payments (user_id, amount) VALUES (%s,%s)",
            (student_id, amount)
        )
        conn.commit()
        success = True
    except mysql.connector.Error:
        success = False
    
    cursor.close()
    conn.close()
    
    return success

def get_student_meal_tokens(student_id, hall_id,date=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if date:
        cursor.execute(
            "SELECT * FROM meal_tokens WHERE user_id = %s AND hall_id = %s AND token_date = %s",
            (student_id,hall_id,date)
        )
    else:
        cursor.execute(
            "SELECT * FROM meal_tokens WHERE user_id = %s AND hall_id = %s ORDER BY token_date DESC",
            (student_id,hall_id)
        )
    
    tokens = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return tokens

def buy_meal_token(student_id, hall_id, meal_type):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO meal_tokens (user_id, hall_id, meal_type, token_date) VALUES (%s, %s, %s, CURDATE())",
            (student_id, hall_id, meal_type)
        )
        conn.commit()
        success = True
    except mysql.connector.Error:
        success = False
    
    cursor.close()
    conn.close()
    
    return success

def calculate_student_dues(student_id, hall_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT allocation_date FROM room_allocations 
        WHERE user_id = %s AND hall_id = %s AND is_active = TRUE
    """, (student_id, hall_id))
    allocation = cursor.fetchone()
    
    if not allocation:
        return 0
    
    allocation_date = allocation['allocation_date']
    now = datetime.datetime.now()
    months = (now.year - allocation_date.year) * 12 + now.month - allocation_date.month + 1
    room_rent = months * 500
    
    cursor.execute("""
        SELECT COUNT(*) as meal_count FROM meal_tokens 
        WHERE user_id = %s AND hall_id = %s
    """, (student_id, hall_id))
    meal_count = cursor.fetchone()['meal_count']
    meal_cost = meal_count * 40
    
    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0) as total_paid FROM payments 
        WHERE user_id = %s
    """, (student_id,))
    total_paid = cursor.fetchone()['total_paid']
    
    cursor.close()
    conn.close()
    
    return room_rent + meal_cost - total_paid


def get_pending_applications(hall_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT a.*, u.full_name as student_name, u.roll_number, u.department 
        FROM applications a 
        JOIN users u ON a.user_id = u.id 
        WHERE a.hall_id = %s AND a.status = 'pending'
    """, (hall_id,))
    applications = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return applications

def approve_application(application_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT user_id, hall_id FROM applications 
            WHERE id = %s AND status = 'pending'
        """, (application_id,))
        application = cursor.fetchone()
        
        if not application:
            return False
        
        cursor.execute("""
            SELECT MIN(r.room_number) as room_number 
            FROM (SELECT 1 as room_number UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION 
                  SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9 UNION SELECT 10) r 
            LEFT JOIN room_allocations ra ON ra.room_number = r.room_number 
                AND ra.hall_id = %s AND ra.is_active = TRUE 
            WHERE ra.id IS NULL
        """, (application['hall_id'],))
        next_room = cursor.fetchone()
        
        if not next_room or not next_room['room_number']:
            return False
        
        cursor.execute("""
            INSERT INTO room_allocations (user_id, hall_id, room_number) 
            VALUES (%s, %s, %s)
        """, (application['user_id'], application['hall_id'], next_room['room_number']))
        
        cursor.execute("""
            UPDATE applications 
            SET status = 'approved', approval_date = CURRENT_TIMESTAMP 
            WHERE id = %s
        """, (application_id,))
        
        cursor.execute("""
            UPDATE halls 
            SET available_rooms = available_rooms - 1 
            WHERE id = %s
        """, (application['hall_id'],))
        
        conn.commit()
        success = True
    except mysql.connector.Error:
        success = False
    
    cursor.close()
    conn.close()
    
    return success

def reject_application(application_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE applications 
            SET status = 'rejected', approval_date = CURRENT_TIMESTAMP 
            WHERE id = %s AND status = 'pending'
        """, (application_id,))
        conn.commit()
        success = True
    except mysql.connector.Error:
        success = False
    
    cursor.close()
    conn.close()
    
    return success

def get_meal_token_stats(hall_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN meal_type = 'lunch' THEN 1 ELSE 0 END) as lunch_count,
            SUM(CASE WHEN meal_type = 'dinner' THEN 1 ELSE 0 END) as dinner_count
        FROM meal_tokens 
        WHERE hall_id = %s AND token_date = CURDATE()
    """, (hall_id,))
    stats = cursor.fetchone()
    
    stats['lunch_count'] = stats['lunch_count'] or 0
    stats['dinner_count'] = stats['dinner_count'] or 0
    
    cursor.close()
    conn.close()
    
    return stats

def get_payment_stats(hall_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT 
            COALESCE(SUM(CASE WHEN DATE(payment_date) = CURDATE() THEN amount ELSE 0 END), 0) as today_total,
            COALESCE(SUM(CASE WHEN DATE_FORMAT(payment_date, '%Y-%m') = DATE_FORMAT(CURDATE(), '%Y-%m') 
                           THEN amount ELSE 0 END), 0) as month_total
        FROM payments p
        JOIN room_allocations ra ON p.user_id = ra.user_id
        WHERE ra.hall_id = %s AND ra.is_active = TRUE
    """, (hall_id,))
    stats = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return stats

def get_hall_students(hall_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT u.*, ra.room_number 
        FROM users u 
        JOIN room_allocations ra ON u.id = ra.user_id 
        WHERE ra.hall_id = %s AND ra.is_active = TRUE
    """, (hall_id,))
    students = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return students

def remove_student(student_id, hall_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE room_allocations 
            SET is_active = FALSE 
            WHERE user_id = %s AND hall_id = %s AND is_active = TRUE
        """, (student_id, hall_id))
        
        cursor.execute("""
            UPDATE halls 
            SET available_rooms = available_rooms + 1 
            WHERE id = %s
        """, (hall_id,))
        
        conn.commit()
        success = True
    except mysql.connector.Error:
        success = False
    
    cursor.close()
    conn.close()
    
    return success


def get_hall_by_name(hall_name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM halls WHERE name = %s", (hall_name,))
    hall = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return hall

def apply_for_hall(user_id, hall_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT * FROM applications WHERE user_id = %s AND status = 'pending'",
            (user_id,)
        )
        if cursor.fetchone():
            return False, "You already have a pending application"
        
        cursor.execute(
            "SELECT * FROM room_allocations WHERE user_id = %s AND is_active = TRUE",
            (user_id,)
        )
        if cursor.fetchone():
            return False, "You already have an active room allocation"
        
        cursor.execute("SELECT available_rooms FROM halls WHERE id = %s", (hall_id,))
        hall = cursor.fetchone()
        if not hall or hall[0] <= 0:
            return False, "No rooms available in this hall"
        
        cursor.execute(
            "INSERT INTO applications (user_id, hall_id) VALUES (%s, %s)",
            (user_id, hall_id)
        )
        
        conn.commit()
        return True, "Application submitted successfully"
    except mysql.connector.Error as err:
        return False, f"Database error: {err}"
    finally:
        cursor.close()
        conn.close()

def get_pending_applications(hall_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT a.id, a.application_date, u.id as user_id, u.full_name, u.roll_number, u.department 
        FROM applications a 
        JOIN users u ON a.user_id = u.id 
        WHERE a.hall_id = %s AND a.status = 'pending'
        ORDER BY a.application_date
    """, (hall_id,))
    
    applications = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return applications

def approve_application(application_id, room_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT user_id, hall_id FROM applications WHERE id = %s",
            (application_id,)
        )
        application = cursor.fetchone()
        if not application:
            return False, "Application not found"
        
        user_id, hall_id = application
        
        cursor.execute(
            "UPDATE applications SET status = 'approved', approval_date = NOW() WHERE id = %s",
            (application_id,)
        )
        
        cursor.execute(
            "INSERT INTO room_allocations (user_id, hall_id, room_number) VALUES (%s, %s, %s)",
            (user_id, hall_id, room_number)
        )

        cursor.execute(
            "UPDATE halls SET available_rooms = available_rooms - 1 WHERE id = %s",
            (hall_id,)
        )
        
        conn.commit()
        return True, "Application approved and room allocated successfully"
    except mysql.connector.Error as err:
        conn.rollback()
        return False, f"Database error: {err}"
    finally:
        cursor.close()
        conn.close()

def reject_application(application_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "UPDATE applications SET status = 'rejected' WHERE id = %s",
            (application_id,)
        )
        
        conn.commit()
        return True, "Application rejected successfully"
    except mysql.connector.Error as err:
        return False, f"Database error: {err}"
    finally:
        cursor.close()
        conn.close()

def get_student_details(hall_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT u.id, u.full_name, u.roll_number, u.department, r.room_number, r.allocation_date 
        FROM room_allocations r 
        JOIN users u ON r.user_id = u.id 
        WHERE r.hall_id = %s AND r.is_active = TRUE
        ORDER BY r.room_number
    """, (hall_id,))
    
    students = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return students

def remove_student(user_id, hall_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "UPDATE room_allocations SET is_active = FALSE WHERE user_id = %s AND hall_id = %s AND is_active = TRUE",
            (user_id, hall_id)
        )

        cursor.execute(
            "UPDATE halls SET available_rooms = available_rooms + 1 WHERE id = %s",
            (hall_id,)
        )
        
        conn.commit()
        return True, "Student removed successfully"
    except mysql.connector.Error as err:
        conn.rollback()
        return False, f"Database error: {err}"
    finally:
        cursor.close()
        conn.close()

def buy_meal_token(user_id, hall_id, meal_type):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT * FROM room_allocations WHERE user_id = %s AND hall_id = %s AND is_active = TRUE",
            (user_id, hall_id)
        )
        if not cursor.fetchone():
            return False, "You are not currently allocated to this hall"
        
        today = datetime.date.today()

        cursor.execute(
            "SELECT * FROM meal_tokens WHERE user_id = %s AND hall_id = %s AND meal_type = %s AND token_date = %s",
            (user_id, hall_id, meal_type, today)
        )
        if cursor.fetchone():
            return False, f"You already have a {meal_type} token for today"

        cursor.execute(
            "INSERT INTO meal_tokens (user_id, hall_id, meal_type, token_date) VALUES (%s, %s, %s, %s)",
            (user_id, hall_id, meal_type, today)
        )
        
        conn.commit()
        return True, f"{meal_type.capitalize()} token purchased successfully"
    except mysql.connector.Error as err:
        return False, f"Database error: {err}"
    finally:
        cursor.close()
        conn.close()

def get_meal_count(hall_id, date=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if date is None:
        date = datetime.date.today()
    
    cursor.execute("""
        SELECT meal_type, COUNT(*) as count 
        FROM meal_tokens 
        WHERE hall_id = %s AND token_date = %s 
        GROUP BY meal_type
    """, (hall_id, date))
    
    result = cursor.fetchall()

    meal_counts = {'lunch': 0, 'dinner': 0}
    for row in result:
        meal_counts[row['meal_type']] = row['count']
    
    cursor.close()
    conn.close()
    
    return meal_counts

def make_payment(user_id, amount):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO payments (user_id, amount) VALUES (%s, %s)",
            (user_id, amount)
        )
        
        conn.commit()
        return True, f"Payment of {amount} recorded successfully"
    except mysql.connector.Error as err:
        return False, f"Database error: {err}"
    finally:
        cursor.close()
        conn.close()

def get_student_due(user_id, hall_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT allocation_date FROM room_allocations WHERE user_id = %s AND hall_id = %s AND is_active = TRUE",
            (user_id, hall_id)
        )
        allocation = cursor.fetchone()
        if not allocation:
            return 0, "You are not currently allocated to this hall"
        
        allocation_date = allocation[0]

        today = datetime.datetime.now()
        months_diff = (today.year - allocation_date.year) * 12 + today.month - allocation_date.month
        if today.day < allocation_date.day:
            months_diff -= 1
        months_stayed = max(1, months_diff)
        
        room_rent = months_stayed * 500
        
        cursor.execute(
            "SELECT COUNT(*) FROM meal_tokens WHERE user_id = %s AND hall_id = %s",
            (user_id, hall_id)
        )
        meal_count = cursor.fetchone()[0]
        meal_cost = meal_count * 40
        
        total_due = room_rent + meal_cost
        cursor.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM payments WHERE user_id = %s",
            (user_id,)
        )
        total_paid = cursor.fetchone()[0]
        
        remaining_due = total_due - total_paid
        if remaining_due<0:
            remaining_due=0
        return remaining_due, "Due calculated successfully"
    
    except mysql.connector.Error as err:
        return 0, f"Database error: {err}"
    finally:
        cursor.close()
        conn.close()

def get_total_payments(hall_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT COALESCE(SUM(p.amount), 0) 
            FROM payments p 
            JOIN room_allocations r ON p.user_id = r.user_id 
            WHERE r.hall_id = %s AND r.is_active = TRUE
        """, (hall_id,))
        
        total_payments = cursor.fetchone()[0]
        return total_payments
    except mysql.connector.Error as err:
        return 0
    finally:
        cursor.close()
        conn.close()

def check_username_exists(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
    count = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    return count > 0

def get_user_allocation(user_id):
    """
    Get the current hall allocation for a user
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT h.id as hall_id, h.name as hall_name, r.room_number 
        FROM room_allocations r 
        JOIN halls h ON r.hall_id = h.id 
        WHERE r.user_id = %s AND r.is_active = TRUE
    """, (user_id,))
    
    allocation = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return allocation