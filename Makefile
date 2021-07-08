venv:
	virtualenv venv
	source venv/bin/activate && pip install flake8-black black

styling: venv
	@source venv/bin/activate && black --config=.black src
	@source venv/bin/activate && flake8 src
