bind = 'unix:/run/slgunicorn.sock'
workers = 4
chdir = '/root/backend_sl/streetlight'
module = 'streetlight.wsgi:application'
