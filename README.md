# 🛒 Ecommerce Social Media App - Mobile Backend

Ecommerce Social Media App - Backend powers the mobile app by providing robust, secure, and scalable APIs built with Django and Django REST Framework.
It handles everything from user authentication, product management, post interactions, to account handling.

## 🚀 Key Features
🔑 User Authentication: Secure registration, login, and JWT token-based authentication.

🛍️ Product Management: Post, update, and retrieve products.

💬 Social Media Features: Post creation, likes, comments, and reactions.

📦 Order and Cart API (planned for future).

🧑‍💼 Account Profiles: Manage user details separately from authentication.

📈 Admin Panel: Full management via Django Admin.

🌐 RESTful API: Well-structured and documented APIs (with Swagger).

## 🛠️ Tech Stack
Python - Core programming language.

Django - High-level Python web framework.

Django REST Framework (DRF) - For building APIs easily and securely.

SimpleJWT - Token-based authentication.

Swagger - Auto-generated API documentation.

SQL Server - Database support.

CORS Headers - Cross-origin requests for mobile frontend integration.

## 📜 API Documentation
After running the server locally, access full API documentation via:

http://localhost:8000/swagger/
You can explore endpoints like:

/users/

/posts/

/products/

/comments/

/reactions/

/accounts/

and more.

## ⚙️ Installation Guide
Step 1: Clone the repository
git clone https://github.com/hapthinh/Ecommerce-Social-Media-App-Mobile-BE.git

Step 2: Set up virtual environment
python -m venv env
source env/bin/activate    # On Windows: env\Scripts\activate

Step 3: Install dependencies
pip install -r requirements.txt

Step 4: Apply database migrations
python manage.py migrate

Step 5: Run the development server
python manage.py runserver

## 👥 Project Contributors

Name	/  Role
Hà Phúc Thịnh /	Project Owner, Backend Developer
# 🌟 Thank you for supporting Ecommerce-Social-Media-App-Mobile-BE!
