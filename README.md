# Marta: ChatGPT 4 Job Coach

## Virtual Environment

1) Create virtual environment in Root directory

- Format: `[py/python3/python] -m venv .{venv_name}`
- Example (PowerShell): `python -m venv .myvenv`

2) Activate virtual environment
   
- PowerShell: ```.myvenv\Scripts\activate.ps1```
- Windows Command Prompt: ```cd myvenv\Scripts; activate```
- Linux/macOS: ```source myvenv/bin/activate```

3) Install from requirements.txt

- ```pip install -r requirements.txt```

4) Update requirements.txt after ```pip install...```
- ```pip freeze > requirements.txt```

## Localhost

Run all four steps after cloning the repository. You can skip steps 2 and 3 after hosting the application for the first time, unless fields in tables in any `/models.py` file are edited. 

1) ```cd application``
2) ```python manage.py makemigrations```
3) ```python manage.py migrate```
4) ```python manage.py runserver```

## Guidelines and Limitations



The Learn module and Oz control panel must be accessed from the same user session on localhost.

## Further Improvements

- Django REST Framework for more complex model querying