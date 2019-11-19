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

API_URL = "https://sesam.myjetbrains.com/youtrack/api/"
START = '2015-09-25'


def stream_as_json(generator_function):
    """
    Stream list of objects as JSON array
    :param generator_function:
    :return:
    """
    first = True

    yield '['

    for item in generator_function:
        if not first:
            yield ','
        else:
            first = False

        yield json.dumps(item)

    yield ']'


def datetime_format(dt):
    return '%04d' % dt.year + dt.strftime("-%m-%dT%H:%M:%SZ")


def to_transit_datetime(dt_int):
    return "~t" + datetime_format(dt_int)


def get_all_objects(datatype: str, since=START):
    """
    Fetch and stream back objects from YouTrack API
    :param datatype path to needed resource in YouTrack entity type
    :param since: since value from last request.
    More about delta https://www.jetbrains.com/help/youtrack/standalone/youtrack-rest-api-reference.html
    :return: generated output with all fetched objects
    """
    if datatype in entitiesschema.fields["admin"]:
        url = API_URL + "admin/" + datatype
    else:
        url = API_URL + datatype

    sincequery = ""
    if "updated" in entitiesschema.fields[datatype]:
        sincequery = f"{urlquote(f'updated: {since} .. Today')}&"
    url += f"?{sincequery}{entitiesschema.fields_query(datatype)}"
    skip = 0
    top = 1000

    while True:
        param = '&$skip={}&$top={}'.format(skip, top)
        response = requests.get(url + param, headers={'Authorization': 'Bearer ' + config.token})
        logger.info('Fetching issues with values: Skip: {} & Top: {}'.format(skip, top))
        if response.ok:
            data = response.json()
            if len(data) == 0:
                break

            skip += 1000

            u = 0
            count = 0

            for item in data:

                i = dict(item)
                for date in entitiesschema.fields["dates"]:
                    if date in i:
                        if i[date]:
                            i[date] = to_transit_datetime(datetime.datetime.fromtimestamp(i[date] / 1e3))
                try:
                    i["_id"] = item['id']
                    x = item['updated'] or item['created'] or item['date']
                    u = datetime.datetime.fromtimestamp(x / 1e3).strftime('%Y-%m-%dT%H:%M')
                except Exception as e:
                    logger.error(f"Cant find a date: {i}")
                i["_updated"] = u
                yield i
                count += 1

            logger.info(f'Yielded: {count}')
        else:
            raise ValueError(f'value object expected in response to url: {url} got {response}')
            break


def check_entity(input):
    separator = "/"
    entity_query = separator.join(list(input.values()))

    if input['entity'] in entitiesschema.fields["admin"]:
        url = API_URL + "admin/" + entity_query
    else:
        url = API_URL + entity_query

    response = requests.get(url, timeout=180, headers={'Authorization': 'Bearer ' + config.token})
    if response.ok:
        logger.info(f"found {input['id_name']}")
        res_data = response.json()
        logger.info(json.dumps(res_data))

        return True
    else:
        logger.error(f"{input['id_name']} does not exist")
        return False


# Default
required_env_vars = ["token"]
optional_env_vars = [("LOG_LEVEL", "INFO")]
config = VariablesConfig(required_env_vars, optional_env_vars=optional_env_vars)
if not config.validate():
    sys.exit(1)

headers = {'Authorization': 'Bearer {}'.format(config.token), 'Content-Type': 'application/json',
           'Accept': 'application/json'}


@app.route('/create/<entity>', methods=['POST'])
def create(entity):
    data = request.get_json()
    try:
        url = 'https://sesam.myjetbrains.com/youtrack/api/' + entity

        for i in data:
            response = requests.post(url, data=json.dumps(i), headers=headers)
            logger.info('sesam json {}'.format(json.dumps(i)))
            if response.ok:
                res_data = response.json()
                logger.info(f"successfully created {json.dumps(res_data)}")
            else:
                logger.error('Entity failed with response {}'.format(response))
                break

    except Timeout as e:
        logger.error(f"Timeout issue while creating YouTrack Issue {e}")
    except ConnectionError as e:
        logger.error(f"ConnectionError issue while creating new YouTrack Issue {e}")
    except Exception as e:
        logger.error(f"Error while creating YouTrack Issue: {e}")

    return 'OK'


@app.route('/update/<entity>/<id_name>', methods=['POST'])
def update(entity, id_name):
    try:
        if entity in entitiesschema.fields["admin"]:
            url = API_URL + "admin/" + entity + '/' + id_name
        else:
            url = API_URL + entity + '/' + id_name

        data = request.get_json()
        to_update = {"entity": entity, "id_name": id_name}
        if check_entity(to_update):
            for item in data:
                logger.info(f"{json.dumps(item)}")
                response = requests.post(url, timeout=180, data=json.dumps(item), headers=headers)

                if response.ok:
                    logger.info(f"successfully updated {entity} attributes in {id_name}")
                    res_data = response.json()
                    logger.info(json.dumps(res_data))


    except Timeout as e:
        logger.error(f"Timeout issue while updating YouTrack {entity} {e}")
    except ConnectionError as e:
        logger.error(f"ConnectionError issue while updating YouTrack {entity} {e}")
    except Exception as e:
        logger.error(f"Error while updating YouTrack {entity}: {e}")

    return 'OK'


@app.route(
    '/entities/<datatype>')  # Will access all of the API and stream the result
def entities(datatype):
    try:
        if request.args.get('since') is None:
            last_update_date = '2019-01-01'  # Starting from beginning :-)
            logger.debug(f"since value set from ms: {last_update_date}")
        else:
            last_update_date = request.args.get('since')
            logger.debug(f"since value sent from sesam: {last_update_date}")

        return Response(stream_as_json(get_all_objects(datatype, last_update_date)), mimetype='application/json')
    except Timeout as e:
        logger.error(f"Timeout issue while fetching YouTrack entities {e}")
    except ConnectionError as e:
        logger.error(f"ConnectionError issue while fetching YouTrack Issues {e}")
    except Exception as e:
        logger.error(f"Issue while fetching YouTrack Issues: {e}")


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

