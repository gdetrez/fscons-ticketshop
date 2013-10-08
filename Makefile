unittest:
	coverage run ticketshop/manage.py test --settings=ticketshop.settings.test ticketapp

test:
	coverage run ticketshop/manage.py test --settings=ticketshop.settings.test

resetdb:
	rm -rf ticketshop/default.db
	python ticketshop/manage.py syncdb --noinput
	python ticketshop/manage.py loaddata admin.json

REMOTE = gregoire@fs.fscons.org
REMOTE_ROOT = /srv/ticketshop
remote_django = ssh $(REMOTE) "$(REMOTE_ROOT)/env/bin/python $(REMOTE_ROOT)/ticketshop/manage.py $(1)"
remote = ssh $(REMOTE) $(1)
deploy:
	rsync -r --exclude env/ --delete . $(REMOTE):$(REMOTE_ROOT)/
	$(call remote, $(REMOTE_ROOT)/env/bin/pip install -r $(REMOTE_ROOT)/requirements/production.txt)
	$(call remote_django, syncdb --noinput)
	$(call remote_django, migrate)
	$(call remote_django, loaddata $(REMOTE_ROOT)/sites.json)
	$(call remote, sudo supervisorctl restart ticketshop)

.PHONY: test
