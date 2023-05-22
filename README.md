- To run the tests:
```
$ cd EXPLOIT/3.3.3_test
$ source bin/activate
$ pip install -r requrements.txt # This step will install the needed version of python_jwt
$ python3 testcase-3.3.3.py 
```
The 3.3.3 should result in failed test, because no exceptions were risen

Same process goes with 3.3.4 test only do not forget to `deactive` python venv.

- To launch the app:
```
$ cd EXPLOIT/app
$ source bin/activate
$ pip install -r requrements.txt
$ pip install -r src/requirements.txt
$ pip install flask_session
$ python3 app.py
```

The app will run on `localhost:5000` and you can create a new user and after try to steal somebodys account! :)))
