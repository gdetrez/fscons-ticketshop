test:
	coverage run manage.py test --settings=ticketshop.settings.test

resetdb:
	rm -rf ticketshop/default.db
	python manage.py syncdb --noinput
	python manage.py loaddata admin.json

.PHONY: test
