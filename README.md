# UBR

# UBR Property Management System - Setup Instructions

## Overview
Multi-user property management and inspection system with three user roles: Owner, Inspector, and Admin.

## Prerequisites
- Python 3.8+
- MySQL 8.0+
- Django 6.0
- MySQL Workbench (for database management)

## Database Setup

### 1. Create Database
```sql
CREATE DATABASE ubr CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. Create Database User
```sql
CREATE USER 'ubr_user'@'localhost' IDENTIFIED BY 'ubr_nsm123';
GRANT ALL PRIVILEGES ON ubr.* TO 'ubr_user'@'localhost';
FLUSH PRIVILEGES;
```

### 3. Create Tables (Run in order)
```sql
USE ubr;

-- User table
CREATE TABLE user (
    u_id INT AUTO_INCREMENT PRIMARY KEY,
    user_type VARCHAR(50),
    nid VARCHAR(50),
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(255),
    phone VARCHAR(20),
    license VARCHAR(50),
    approved_inspect_id INT,
    FOREIGN KEY (approved_inspect_id) REFERENCES user(u_id) ON DELETE SET NULL
);

-- Property table
CREATE TABLE property (
    p_id INT AUTO_INCREMENT PRIMARY KEY,
    type VARCHAR(50),
    locations VARCHAR(255),
    owner_id INT,
    FOREIGN KEY (owner_id) REFERENCES user(u_id) ON DELETE CASCADE
);

-- Inspection Request table
CREATE TABLE inspection_request (
    req_id INT AUTO_INCREMENT PRIMARY KEY,
    req_type VARCHAR(100),
    property_id INT,
    FOREIGN KEY (property_id) REFERENCES property(p_id) ON DELETE CASCADE
);

-- Report table
CREATE TABLE report (
    r_id INT AUTO_INCREMENT PRIMARY KEY,
    owner_id INT,
    inspector_id INT,
    property_id INT,
    inspection_request_id INT,
    report_content TEXT,
    is_approved BOOLEAN DEFAULT FALSE,
    has_issues BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES user(u_id) ON DELETE CASCADE,
    FOREIGN KEY (inspector_id) REFERENCES user(u_id) ON DELETE CASCADE,
    FOREIGN KEY (property_id) REFERENCES property(p_id) ON DELETE CASCADE,
    FOREIGN KEY (inspection_request_id) REFERENCES inspection_request(req_id) ON DELETE SET NULL
);

-- Transaction table
CREATE TABLE transaction (
    t_id INT AUTO_INCREMENT PRIMARY KEY,
    details TEXT,
    amount DECIMAL(10, 2),
    payment_status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Message table
CREATE TABLE message (
    m_id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT,
    receiver_id INT,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES user(u_id) ON DELETE CASCADE
);

-- Submits table (links transactions to requests)
CREATE TABLE submits (
    t_id INT,
    req_id INT,
    owner_id INT,
    PRIMARY KEY (t_id, req_id, owner_id),
    FOREIGN KEY (t_id) REFERENCES transaction(t_id) ON DELETE CASCADE,
    FOREIGN KEY (req_id) REFERENCES inspection_request(req_id) ON DELETE CASCADE,
    FOREIGN KEY (owner_id) REFERENCES user(u_id) ON DELETE CASCADE
);

-- Assigns table (links inspectors to requests)
CREATE TABLE assigns (
    req_id INT,
    admin_id INT,
    inspector_id INT,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (req_id, admin_id, inspector_id),
    FOREIGN KEY (req_id) REFERENCES inspection_request(req_id) ON DELETE CASCADE,
    FOREIGN KEY (admin_id) REFERENCES user(u_id) ON DELETE CASCADE,
    FOREIGN KEY (inspector_id) REFERENCES user(u_id) ON DELETE CASCADE
);
```

## Django Project Setup

### 1. Install Required Packages
```bash
pip install django mysqlclient
```

### 2. Project Structure
```
ubr/
├── manage.py
├── ubr/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── myapp/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── backends.py
    ├── models.py
    ├── views.py
    ├── urls.py
    ├── migrations/
    └── templates/
        ├── registration/
        │   ├── login.html
        │   └── signup.html
        ├── owner_dashboard.html
        ├── inspector_dashboard.html
        ├── admin_dashboard.html
        ├── my_properties.html
        ├── add_property.html
        ├── property_detail.html
        ├── view_report.html
        ├── generate_report.html
        ├── request_reinspection.html
        ├── payment_success.html
        ├── inspector_pending.html
        ├── manage_users.html
        └── assign_inspector.html
```

### 3. Update settings.py
Add these configurations to your existing settings.py:

```python
# Authentication
AUTHENTICATION_BACKENDS = [
    'myapp.backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
]

AUTH_USER_MODEL = 'myapp.CustomUser'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'
```

### 4. Create Superuser (Admin)
```bash
python manage.py createsuperuser
# Enter email, name, and password when prompted
```

## Running the Application

### 1. Start Development Server
```bash
cd ubr
python manage.py runserver
```

### 2. Access the Application
- Main URL: http://localhost:8000/
- Admin Panel: http://localhost:8000/admin/

## User Roles & Features

### Owner
- Register with basic information
- Add/Delete properties
- View inspection reports
- Request re-inspections with payment
- Dashboard with property overview

### Inspector
- Register with license number (required)
- **Must be approved by admin before access**
- View assigned inspections
- Generate inspection reports (checkbox format)
- Dashboard with assigned tasks

### Admin
- Full system access
- Approve inspector accounts
- Assign inspectors to inspection requests
- Manage all users and properties
- View system statistics

## Workflow

### 1. Inspector Registration & Approval
1. Inspector signs up with license number
2. Inspector sees "Pending Approval" page
3. Admin reviews and approves inspector
4. Inspector gains dashboard access

### 2. Property Inspection Process
1. Owner adds property
2. Owner views report and identifies issues
3. Owner requests re-inspection (selects type & pays)
4. Admin assigns inspector to request
5. Inspector completes inspection checklist
6. Inspector generates report
7. Owner views completed report

## Testing the System

### 1. Create Test Users

**Create Admin:**
```bash
python manage.py createsuperuser
```

**Create Owner:**
- Go to /signup/
- Fill form with user_type="owner"
- Login and add properties

**Create Inspector:**
- Go to /signup/
- Fill form with user_type="inspector" + license number
- Will see pending approval page
- Admin must approve via /admin/users/

### 2. Test Complete Flow
1. Login as Owner → Add property
2. Login as Admin → Create inspection request and assign inspector
3. Login as Inspector → Generate report
4. Login as Owner → View report → Request re-inspection
5. Payment confirmation page appears

## Troubleshooting

### Database Connection Error
```python
# Check settings.py DATABASES configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ubr',
        'USER': 'ubr_user',
        'PASSWORD': 'ubr_nsm123',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### Template Not Found
- Ensure templates are in `myapp/templates/`
- Check TEMPLATES 'DIRS' in settings.py

### Authentication Issues
- Verify EmailBackend in settings.py
- Check CustomUser model in models.py
- Ensure 'myapp' is in INSTALLED_APPS

### Inspector Can't Login
- Verify inspector has been approved by admin
- Check approved_inspect_id field is not NULL

## Important Notes

1. **Inspector Approval**: Inspectors CANNOT access the system until approved by admin
2. **License Requirement**: License number is mandatory for inspector registration
3. **Payment Simulation**: No actual payment gateway - just records transaction
4. **Database Managed=False**: Models use existing database schema
5. **Raw SQL**: Some views use raw SQL for complex queries

## API Endpoints

### Authentication
- `/signup/` - User registration
- `/login/` - User login
- `/logout/` - User logout

### Owner Routes
- `/dashboard/` - Owner dashboard
- `/properties/` - List properties
- `/properties/add/` - Add property
- `/properties/<id>/` - Property details
- `/properties/<id>/delete/` - Delete property
- `/report/<id>/` - View report
- `/report/<id>/reinspection/` - Request re-inspection

### Inspector Routes
- `/inspector/dashboard/` - Inspector dashboard
- `/inspection/<id>/generate-report/` - Generate report

### Admin Routes
- `/admin/dashboard/` - Admin dashboard
- `/admin/users/` - Manage users
- `/admin/inspector/<id>/approve/` - Approve inspector
- `/admin/assign-inspector/` - Assign inspector to request

## Database Schema Summary

```
user (u_id, user_type, nid, name, email, password, phone, license, approved_inspect_id)
property (p_id, type, locations, owner_id)
inspection_request (req_id, req_type, property_id)
report (r_id, owner_id, inspector_id, property_id, inspection_request_id, report_content, is_approved, has_issues, created_at)
transaction (t_id, details, amount, payment_status, created_at)
message (m_id, sender_id, receiver_id, user_id)
submits (t_id, req_id, owner_id)
assigns (req_id, admin_id, inspector_id, assigned_at)
```

## Support
For issues or questions, contact the development team.

## License
MIT License - See LICENSE file for details