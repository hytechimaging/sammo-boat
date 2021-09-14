VERSION := "0.0.1"
TMPDIR := "/tmp/sammo-boat-$(VERSION)"

venv:
	virtualenv venv
	. venv/bin/activate && pip install flake8-black black

styling: venv
	@source venv/bin/activate && black --config=.black src sammo.py __init__.py
	@source venv/bin/activate && flake8 src sammo.py __init__.py

clean-archive:
	rm -Rf $(TMPDIR) "./sammo-boat.zip"

archive: clean-archive
	mkdir -p "$(TMPDIR)/sammo-boat"
	rsync -vazC --exclude=".*" . "$(TMPDIR)/sammo-boat/"
	cd "$(TMPDIR)/sammo-boat" && zip -x "Makefile" -r "$(TMPDIR)/sammo-boat.zip" "."
	cp "$(TMPDIR)/sammo-boat.zip" .
