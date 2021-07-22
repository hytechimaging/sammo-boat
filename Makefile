venv:
	virtualenv venv
	. venv/bin/activate && pip install flake8-black black

styling: venv
	@source venv/bin/activate && black --config=.black src sammo.py __init__.py
	@source venv/bin/activate && flake8 src sammo.py __init__.py
