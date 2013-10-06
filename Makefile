test:
	coverage run ticketshop/manage.py test --settings=ticketshop.settings.test

resetdb:
	rm -rf ticketshop/default.db
	python ticketshop/manage.py syncdb --noinput
	python ticketshop/manage.py loaddata admin.json

deploy:
	rsync -r --exclude env/ --delete . fs.fscons.org:/srv/ticketshop/
	ssh fs.fscons.org "/srv/ticketshop/env/bin/pip install -r /srv/ticketshop/requirements/production.txt"
	ssh fs.fscons.org "export SECRET_KEY=aaa ; /srv/ticketshop/env/bin/python /srv/ticketshop/ticketshop/manage.py syncdb --settings=ticketshop.settings.production --noinput"
	ssh fs.fscons.org "export SECRET_KEY=aaa ; /srv/ticketshop/env/bin/python /srv/ticketshop/ticketshop/manage.py migrate --settings=ticketshop.settings.production --noinput"
	ssh fs.fscons.org "export SECRET_KEY=aaa ; /srv/ticketshop/env/bin/python /srv/ticketshop/ticketshop/manage.py loaddata --settings=ticketshop.settings.production /srv/ticketshop/sites.json"

.PHONY: test
