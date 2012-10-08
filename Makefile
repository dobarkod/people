MANAGE=python manage.py
APPS=core pm hr track

.PHONY: all test coverage clean requirements

all: coverage

test:
	$(MANAGE) test $(APPS) --settings=people.settings.test

coverage:
	$(MANAGE) test $(APPS) --settings=people.settings.test \
		--with-coverage --with-xunit --cover-html  --cover-erase

clean:
	rm -rf .coverage cover
	find . -name '*.pyc' -exec rm '{}' ';'

requirements:
	pip install -r requirements.txt
