## Create virtual enviroment 

```
python3 -m venv venv 
```

Active enviroment 
```
source ./venv/bin/activate
```

Install package
```
pip install -r requirements.txt
```

## HOW TO RUN:
1. Edit .env
- Edit: DB_HOST, DB_NAME, DB_USER, DB_PASSWORD in .env

2. Follow migration intruction in migrations/README.md

3. Run local
- python run.py

# HOW TO RUN TESTING API
 ```
    pytest
```
    
    - pytest will run all files of the form test_*.py or *_test.py in the current directory and its subdirectories.

# HOW TO RUN WITH MYPY
 
 - Once mypy is installed, run it by using the mypy tool:
    ```
    $ mypy run.py    
    ```
    + This command makes mypy type check run.py file and print out any errors it finds. Mypy will type check your code statically: this means that it will check for errors without ever running your code, just like a linter.
    + This also means that you are always free to ignore the errors mypy reports, if you so wish. You can always use the Python interpreter to run your code, even if mypy reports errors.
    + However, if you try directly running mypy on your existing Python code, it will most likely report little to no errors

 - If you want mypy to ignore all missing imports, to run:
    ```
    $ mypy --ignore-missing-imports run.py    
    ```
- If you want tells mypy that top-level packages will be based in either the current directory, or a member of the MYPYPATH environment variable or mypy_path config option, to run:
    ```
    $ mypy --explicit-package-bases run.py    
    ```