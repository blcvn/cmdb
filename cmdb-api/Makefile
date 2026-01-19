.PHONY: cmdb-api cmdb-celery-worker cmdb-acl-celery-worker

cmdb-api:
	/bin/bash -c "source .venv/bin/activate && flask run -h 0.0.0.0"

cmdb-celery-worker:
	/bin/bash -c "source .venv/bin/activate && celery -A celery_worker.celery worker -E -Q one_cmdb_async --autoscale=5,2 --logfile=one_cmdb_async.log"

cmdb-acl-celery-worker:
	/bin/bash -c "source .venv/bin/activate && celery -A celery_worker.celery worker -E -Q acl_async --autoscale=2,1 --logfile=one_acl_async.log"