```markdown
# FatMug - Vendor Management System

## Setup Instructions

1. **Database Setup:** Create a PostgreSQL database with the following details (modify as per your requirements):

    ```python
    //SNIPPET FROM SETTINGS.PY, you will need to edit this
    
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'postgres', 
            'USER': 'postgres',
            'PASSWORD': 'root',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }
    ```

2. **Install Dependencies:** Run the following command to install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. **Create a User and Get Authentication Token:** Before running the server, you can create a new user and obtain an authentication token by running the following command:

    ```bash
    python manage.py create_user_with_token <username>
    ```

    Replace `<username>` with the desired username for the new user. This command will create a user with the specified username and return an authentication token.

4. **Migrate Database:** If it's the first time running the app, migrate the data models into the database using the following commands:

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

    *(If migrate is not working, delete the `.py` files from the migration folder and try again)*

## Running the Server

Use the following command to run the server:

```bash
python manage.py runserver
```

## Running Tests

To run the tests, execute the following command:

```bash
python manage.py test
```

## API Endpoints

All endpoints have the prefix `http://127.0.0.1:8000/`.

- `/api/vendors/` - GET, POST
- `/api/vendors/<str:vendor_code>/` - GET, PUT, DELETE
- `/api/vendors/<str:vendor_code>/performance/` - GET
- `/api/purchase_orders/` - GET, POST
- `/api/purchase_orders/<str:vendor_code>` - GET
- `/api/purchase_orders/<str:po_number>/` - GET, PUT, DELETE
- `/api/historical_performance/` - GET, POST
- `/api/purchase_orders/<str:po_number>/acknowledge/` - POST
```
