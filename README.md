Prerequisites
-------------

Ensure you have Python and pip installed on your machine. You can verify your installation by running:

bash

Copy code

`python --version
pip --version`

Setting Up a Virtual Environment
--------------------------------

Using a virtual environment is recommended to manage the project dependencies separately. Here's how you can set it up:

### Install virtualenv

If you do not have `virtualenv` installed, you can install it using pip:

bash

Copy code

`pip install virtualenv`

### Create and Activate a Virtual Environment

Navigate to your project directory and create a new virtual environment:

bash

Copy code

`virtualenv venv`

Activate the virtual environment:

-   On Windows:

    bash

    Copy code

    `venv\Scripts\activate`

-   On macOS and Linux:

    bash

    Copy code

    `source venv/bin/activate`

Install Dependencies
--------------------

With the virtual environment activated, install the project dependencies from the `requirements.txt` file:

bash

Copy code

`pip install -r requirements.txt`

Database Migrations
-------------------

Before you can run the server, ensure that your database is up to date with the latest migrations:

1.  Navigate to the directory containing `manage.py`.
2.  Run the following commands to make and apply migrations:


`python manage.py makemigrations`
`python manage.py migrate`


Running the Django Server
-------------------------

To start the Django development server, execute:

bash

Copy code

`python manage.py runserver`

This command starts the server on the default port `8000`. If you want to use a different port:

bash

Copy code

`python manage.py runserver 8080`

Accessing the Application
-------------------------

Open your web browser and navigate to `http://127.0.0.1:8000/` to view the application.
