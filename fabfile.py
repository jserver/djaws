import os

from fabric.api import local


def init():
    if os.path.exists('db/sql.db'):
        local('rm db/sql.db')
    local('./manage.py syncdb')
    local('./manage.py migrate')
    local('./manage.py load_keys')
    local('./manage.py load_security_groups')
    local('./manage.py loaddata db/starter.json')
