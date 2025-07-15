# 💬 Real-Time Django Chat App – Therapist-Client Messaging

This is an extension of the **Mental Health APP** from **Group C year2 Makerere University.** This project uses **Django**, **WebSockets**, and **SQLite**, where users can sign up and chat with **therapists** (who are added by the admin). The chat is made real-time using Django Channels.

---

## 📸 Features

- 🔐 User authentication (login/signup)
- 👨‍⚕️ Therapists are added by admin only
- 💬 Real-time 1-on-1 chat between user and therapist
- 🧠 Therapists see users who have messaged them
- 📱 WhatsApp-style UI for mobile and desktop
- 🔍 Therapist search
- 📨 Messages stored in database

---

## 🛠 Tech Stack

- **Python 3.12+**
- **Django 5.2**
- **Django Channels**
- **SQLite3**
- **Uvicorn (ASGI Server)**
- **HTML + Tailwind CSS**

---

## 🚀 Getting Started

### ✅ 1. Clone the repo

```bash
git clone https://github.com/your-username/chatapp.git
cd chatapp
```

> Make sure you're in the correct project root (the one containing `manage.py` and the `core/`, `chatapp/` folders).

---

### ✅ 2. Set up a virtual environment

```bash
python -m venv venv
venv\Scripts\activate  # On Windows
```

---

### ✅ 3. Install all dependencies

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install django
pip install channels
pip install uvicorn
```

---

### ✅ 4. Apply migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

### ✅ 5. Create a superuser (to add therapists)

```bash
python manage.py createsuperuser
```

---

### ✅ 6. Run the server (ASGI)

```bash
python -m uvicorn core.asgi:application --reload
```

---

## 🧪 Sample Data (Optional)

You can quickly add some sample therapists via the Django shell:

```bash
python manage.py shell
```

```python
from chatapp.models import User

therapists = [
    {"username": "musa", "email": "musa@gmail.com"},
    {"username": "susan", "email": "susan@example.com"},
]

for t in therapists:
    user = User.objects.create_user(username=t["username"], email=t["email"], password="pass1234")
    user.is_therapist = True
    user.save()
```

---

## 🗂 Folder Structure (simplified)

```
chatapp/
│
├── chatapp/           # Main app
│   ├── models.py
│   ├── views.py
│   ├── consumers.py
│   ├── routing.py
│   └── templates/chatapp/
│
├── core/              # Project settings
│   ├── asgi.py
│   ├── settings.py
│   └── urls.py
│
├── manage.py
└── db.sqlite3
```

---

## ⚡ Notes

- Messages are stored in the `Message` model
- WebSocket routing is handled in `core/asgi.py` and `chatapp/routing.py`
- Tailwind can be added manually or via CDN for styling
- Therapists **only appear to users**, and **users appear to therapists if they’ve messaged**

---

## 📬 Contact / Help

Feel free to reach out if you face any issues. Happy building! 🚀
