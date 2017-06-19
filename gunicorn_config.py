from multiprocessing import cpu_count

bind = "unix:/var/run/gunicorn/arum.sock"
workers = cpu_count()
umask = 002
forwarded_allow_ips = "*" 
name = "arum" 
error_logfile = "/var/log/gunicorn/arum.error.log"
pid = "/var/run/gunicorn/arum.pid"
raw_env = ["DJANGO_SETTINGS_MODULE=settings"]
