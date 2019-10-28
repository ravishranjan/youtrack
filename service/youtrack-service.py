import datetime
import json
import logging
import os
import sys
from urllib.parse import quote as urlquote

import cherrypy
import entitiesschema
import paste.translogger
import requests
from flask import Flask, request, Response
from requests.exceptions import Timeout
from sesamutils import VariablesConfig

app = Flask(__name__)

logger = logging.getLogger("YouTrack-Service")

# Default
required_env_vars = ["token"]
optional_env_vars = [("LOG_LEVEL", "INFO")]
config = VariablesConfig(required_env_vars, optional_env_vars=optional_env_vars)
if not config.validate():
    sys.exit(1)


@app.route('/issues')  # Limit set 4000 issues, tested and working within Sesam.
def get_issues():
    try:
        if request.args.get('since') is None:
            last_update_date = '2015-09-25'  # Starting from beginning :-)
            logger.debug(f"since value set from ms: {last_update_date}")
        else:
            last_update_date = request.args.get('since')
            logger.debug(f"since value sent from sesam: {last_update_date}")
        with requests.Session() as session:
            fields = entitiesschema.make_issues_fields_query()
            query = urlquote(f'updated: {last_update_date} .. Today')
            skip = 0
            top = 4000
            url = f'https://sesam.myjetbrains.com/youtrack/api/issues?query={query}&{fields}&$skip={skip}&$top={top}'
            response = session.get(url, timeout=180, headers={'Authorization': 'Bearer ' + config.token})
            result = list()
            if response.ok:
                data = response.json()
                result = [dict(item, _updated=datetime.datetime.fromtimestamp(item['updated'] / 1e3).
                               strftime('%Y-%m-%dT%H:%M'), _id=item['idReadable']) for item in data]
                result = result[::-1]
        return Response(json.dumps(result), mimetype='application/json')
    except Timeout as e:
        logger.error(f"Timeout issue while fetching YouTrack Issues {e}")
    except ConnectionError as e:
        logger.error(f"ConnectionError issue while fetching YouTrack Issues {e}")
    except Exception as e:
        logger.error(f"Issue while fetching YouTrack Issues: {e}")


@app.route(
    '/get_all_issues')  # Will combine all paged lists and send it to Sesam, needs to be streamed because it takes up too much memory.
def get_all_issues():
    try:
        if request.args.get('since') is None:
            last_update_date = '2015-09-25'  # Starting from beginning :-)
            logger.debug(f"since value set from ms: {last_update_date}")
        else:
            last_update_date = request.args.get('since')
            logger.debug(f"since value sent from sesam: {last_update_date}")
        with requests.Session() as session:
            fields = entitiesschema.make_issues_fields_query()
            query = urlquote(f'updated: {last_update_date} .. Today')
            data_set = []
            skip = 0
            top = 1000
            uri = f'https://sesam.myjetbrains.com/youtrack/api/issues?query={query}&{fields}'

            while True:
                param = '&$skip={}&$top={}'.format(skip, top)
                r = requests.get(uri + param, headers={'Authorization': 'Bearer ' + config.token})
                logger.info('Fetching issues with values: Skip: {} & Top: {}'.format(skip, top))
                raw = r.json()
                if len(raw) != 0:
                    top = top + 1000
                    skip = skip + 1000
                    result = [dict(item, _updated=datetime.datetime.fromtimestamp(item['updated'] / 1e3).
                                   strftime('%Y-%m-%dT%H:%M'), _id=item['idReadable']) for item in raw]
                    result = result[::-1]
                    for entities in result:
                        data_set.append(entities)
                else:
                    break
            return Response(json.dumps(data_set), mimetype='application/json')
    except Timeout as e:
        logger.error(f"Timeout issue while fetching YouTrack Issues {e}")
    except ConnectionError as e:
        logger.error(f"ConnectionError issue while fetching YouTrack Issues {e}")
    except Exception as e:
        logger.error(f"Issue while fetching YouTrack Issues: {e}")


@app.route('/users')
def get_users():
    try:
        with requests.Session() as session:
            fields = entitiesschema.make_users_fields_query()
            url = f'https://sesam.myjetbrains.com/youtrack/api/admin/users?{fields}'
            response = session.get(url, timeout=180, headers={'Authorization': 'Bearer ' + config.token})
            result = list()
            if response.ok:
                data = response.json()
                result = [dict(item, _id=str(item['id'])) for item in data]
        return Response(json.dumps(result), mimetype='application/json')
    except Timeout as e:
        logger.error(f"Timeout issue while fetching YouTrack users {e}")
    except ConnectionError as e:
        logger.error(f"ConnectionError issue while fetching YouTrack users {e}")
    except Exception as e:
        logger.error(f"Issue while fetching YouTrack users: {e}")


@app.route('/roles')
def get_roles():
    try:
        with requests.Session() as session:
            url = f'https://sesam.myjetbrains.com/hub/api/rest/roles'
            response = session.get(url, timeout=180, headers={'Authorization': 'Bearer ' + config.token})
            result = list()
            if response.ok:
                data = response.json()['roles']
                result = [dict(item, _id=str(item['id'])) for item in data]
        return Response(json.dumps(result), mimetype='application/json')
    except Timeout as e:
        logger.error(f"Timeout issue while fetching YouTrack roles {e}")
    except ConnectionError as e:
        logger.error(f"ConnectionError issue while fetching YouTrack roles {e}")
    except Exception as e:
        logger.error(f"Issue while fetching YouTrack roles: {e}")


@app.route('/projects')
def get_projects():
    try:
        with requests.Session() as session:
            fields = entitiesschema.make_projects_fields_query()
            url = f'https://sesam.myjetbrains.com/youtrack/api/admin/projects?{fields}'
            response = session.get(url, timeout=180, headers={'Authorization': 'Bearer ' + config.token})
            result = list()
            if response.ok:
                projects = response.json()
                custom_field_query = entitiesschema.make_projects_fields_query_customfields()
                for project in projects:
                    url_project = f"https://sesam.myjetbrains.com/youtrack/api/admin/" \
                        f"projects/{project['id']}/fields?{custom_field_query}"
                    response = session.get(url_project, timeout=180,
                                           headers={'Authorization': 'Bearer ' + config.token})
                    project['customFields'] = response.json()
                result = [dict(item, _id=str(item['id'])) for item in projects]
        return Response(json.dumps(result), mimetype='application/json')
    except Timeout as e:
        logger.error(f"Timeout issue while fetching YouTrack projects {e}")
    except ConnectionError as e:
        logger.error(f"ConnectionError issue while fetching YouTrack projects {e}")
    except Exception as e:
        logger.error(f"Issue while fetching YouTrack projects: {e}")


if __name__ == '__main__':
    format_string = '%(name)s - %(levelname)s - %(message)s'
    # Log to stdout, change to or add a (Rotating)FileHandler to log to a file
    stdout_handler = logging.StreamHandler()
    stdout_handler.setFormatter(logging.Formatter(format_string))
    logger.addHandler(stdout_handler)

    # Comment these two lines if you don't want access request logging
    app.wsgi_app = paste.translogger.TransLogger(app.wsgi_app, logger_name=logger.name,
                                                 setup_console_handler=False)
    app.logger.addHandler(stdout_handler)

    logger.propagate = False
    log_level = logging.getLevelName(os.environ.get('LOG_LEVEL', 'INFO'))  # default log level = INFO
    logger.setLevel(level=log_level)
    cherrypy.tree.graft(app, '/')
    # Set the configuration of the web server to production mode
    cherrypy.config.update({
        'environment': 'production',
        'engine.autoreload_on': False,
        'log.screen': True,
        'server.socket_port': 5000,
        'server.socket_host': '0.0.0.0'
    })

    # Start the CherryPy WSGI web server
    cherrypy.engine.start()
    cherrypy.engine.block()

