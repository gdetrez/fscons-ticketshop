test:
	coverage run ticketshop/manage.py test --settings=ticketshop.settings.test

resetdb:
	rm -rf ticketshop/default.db
	python ticketshop/manage.py syncdb --noinput
	python ticketshop/manage.py loaddata admin.json

.PHONY: test
