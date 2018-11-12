import os
import gevent.monkey
gevent.monkey.patch_all()
import multiprocessing
bind='0.0.0.0:5000'
workers=multiprocessing.cpu_count()*2 + 1
backlog=2048
worker_class="gevent"
# threads = 20
daemon=True
# debug=True
reload = True
pidfile='./gunicore.pid'
loglevel='debug'
accesslog='log/gunicorn.log'
errorlog='log/gunicorn.err.log'
timeout = 500