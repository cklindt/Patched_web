import logging
import psycopg2
from .connection import get_db_connection

def create_tables():
    tables = (
        # Create user table
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            username VARCHAR(32) UNIQUE NOT NULL,
            password VARCHAR(32) NOT NULL,
            role VARCHAR(20) CHECK (role IN ('student', 'instructor', 'admin')) NOT NULL
        )
        """,
        # Create session table
        """
        CREATE TABLE IF NOT EXISTS sessions (
            session_id CHAR(32) PRIMARY KEY,
            user_id INTEGER NOT NULL,
            expiration TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
        """,
        # Create courses table
        """
        CREATE TABLE IF NOT EXISTS courses (
            course_id SERIAL PRIMARY KEY,
            title VARCHAR(100) NOT NULL UNIQUE,
            description TEXT,
            instructor_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
            image_path VARCHAR(255)
        )
        """,
        # Create enrollments table
        """
        CREATE TABLE IF NOT EXISTS enrollments (
            enrollment_id SERIAL PRIMARY KEY,
            student_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
            course_id INTEGER REFERENCES courses(course_id) ON DELETE CASCADE,
            UNIQUE (student_id, course_id)
        )
        """,
        # Create admin user
        """
        INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')
        ON CONFLICT (username) DO NOTHING
        """,
        # Create non-admin users
        """
        INSERT INTO users (username, password, role) VALUES 
            ('user1', 'user123', 'student'),
            ('user2', 'user123!', 'student'),
            ('user3', 'user123@', 'student'),
            ('instructor1', 'instructor123', 'instructor')
        ON CONFLICT (username) DO NOTHING
        """,
        # Insert into courses
        """
        INSERT INTO courses (title, description, instructor_id, image_path) VALUES
            ('Intro to Cybersecurity', 'Welcome to Introduction to Cybersecurity, an essential course designed 
            for individuals new to the field of cybersecurity. This course provides a foundational understanding 
            of key concepts and practices critical to protecting digital information and systems from threats and vulnerabilities.', 2, 
            'images/intro.jpg'),
            ('Ethical Hacking and Penetration Testing', 'Explore the techniques and tools used by ethical hackers to identify and exploit 
            vulnerabilities in systems, networks, and applications. Learn about penetration testing methodologies, vulnerability assessment, 
            and how to ethically simulate attacks to enhance security.', 2, 'images/hacking.jpg'),
            ('Incident Response and Management', 'Learn how to effectively respond to and manage cybersecurity incidents. Topics include incident 
            detection, analysis, containment, eradication, and recovery, as well as creating and implementing an incident response plan.',2, 
            'images/incident.jpg'),
            ('Malware Analysis', 'Delve into the techniques used to analyze and understand malware. This course covers malware types, 
            reverse engineering, and how to detect and mitigate malware threats.', 2, 'images/malware.jpg'),
            ('Cybersecurity for IoT Devices', 'Focus on the unique security challenges posed by Internet of Things (IoT) devices. This course 
            covers vulnerabilities, attack vectors, and best practices for securing IoT environments and devices.', 2, 'images/iot.jpg'),
            ('Cloud Security', 'This course provides a foundational understanding of securing cloud environments, focusing on cloud architecture, 
            security controls, and compliance. You will learn to identify and mitigate cloud-specific threats, implement security best practices 
            for cloud services, and manage risks associated with cloud computing.', 2, 'images/cloud.jpg')
        """
    )

    import random

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        for table in tables:
            try:
                cur.execute(table)
            except Exception as e:
                logging.error(f"Error executing query: {e}")

        cur.execute("SELECT course_id FROM courses")
        course_ids = [row[0] for row in cur.fetchall()]

        cur.execute("SELECT user_id FROM users WHERE role = 'student'")
        student_ids = [row[0] for row in cur.fetchall()]

        for student_id in student_ids:
            random_courses = random.sample(course_ids, min(2, len(course_ids)))
            for course_id in random_courses:
                cur.execute(f""" INSERT INTO enrollments (student_id, course_id) 
                    VALUES (%s, %s) ON CONFLICT (student_id, course_id) DO NOTHING"""
                    % (student_id, course_id)
                )
            
        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(f"Database error: {error}")
        if conn is not None:
            conn.rollback()  # Rollback the transaction in case of error
    finally:
        if conn is not None:
            conn.close()