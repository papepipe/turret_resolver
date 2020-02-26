#
# Copyright 2019 University of Technology, Sydney
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
# to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#   * The above copyright notice and this permission notice shall be included in all copies or substantial portions of
#     the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import logging

import urllib
from urlparse import urlparse

from pgtk import client

PATH_VAR_REGEX = r'[$]{1}[A-Z_]*'
VERSION_REGEX = r'v[0-9]{3}'
ZMQ_NULL_RESULT = "NOT_FOUND"
VERBOSE = False

_logger = logging.getLogger(__file__)


class Resolver(object):
    path_var_regex = r'[$]{1}[A-Z_]*'
    version_regex = r'v[0-9]{3}'
    zmq_null_result = "NOT_FOUND"
    verbose = False
    _instance = None

    def __init__(self):
        self._client = client.Client()

    @property
    def client(self):
        return self._client

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Resolver, cls).__new__(cls, *args, **kwargs)
        return cls._instance


def uri_to_filepath(uri):
    _resolver = Resolver()

    # this is necessary for katana - for some reason katana ships with it's own
    # modified version of urlparse which only works for some protocols,
    # so switch to http
    if uri.startswith('tank://'):
        uri = uri.replace('tank://', 'http:/')
    elif uri.startswith('tank:/'):
        uri = uri.replace('tank:/', 'http:/')

    uri_tokens = urlparse(uri)
    query = uri_tokens.query
    path_tokens = uri_tokens.path.split('/')

    template = path_tokens[2]

    query_tokens = query.split('&')
    fields = {}

    for field in query_tokens:
        key, value = field.split('=')
        fields[key] = value

    path_template = _resolver.client.tk.templates[template]
    _logger.debug(
        "turret_resolver found sgtk template {}".format(path_template))

    fields_ = {}
    for key in fields:
        if key == 'version':
            if fields[key] == 'latest':
                continue
            fields_[key] = int(fields[key])
        else:
            fields_[key] = fields[key]

    publishes = _resolver.client.tk.paths_from_template(path_template, fields_)

    if len(publishes) == 0:
        return ZMQ_NULL_RESULT

    publishes.sort()

    _logger.debug("turret_resolver found publishes: {}".format(publishes))

    result = publishes[-1]
    return result


def filepath_to_uri(filepath, version_flag="latest", proj=""):
    _resolver = Resolver()
    path_template = _resolver.client.tk.template_from_path(filepath)

    fields = path_template.get_fields(filepath)
    fields['version'] = version_flag

    return _generate_uri(fields, path_template, proj)


def _generate_uri(fields, path_template, proj):
    query = urllib.urlencode(fields)
    uri = 'tank:/{}/{}?{}'.format(proj, path_template.name, query)
    return uri


def filepath_to_template(filepath):
    _resolver = Resolver()
    return _resolver.client.tk.template_from_path(filepath)


def uri_to_template(uri):
    path = urlparse(uri).path.split('/')
    if len(path) == 2:
        return str(path[1])
    return str(path[2])


def uri_to_fields(uri):
    uri_tokens = urlparse(uri)
    query = uri_tokens.query
    query_tokens = query.split('&')
    fields = {}

    for field in query_tokens:
        key, value = field.split('=')
        fields[key] = value

    return fields


def template_from_name(name):
    _resolver = Resolver()
    return _resolver.client.tk.templates.get(name)


def filepath_to_fields(filepath):
    _resolver = Resolver()
    return _resolver.client.tk.template_from_path(filepath).get_fields(filepath)


def fields_to_uri(proj, templ_name, fields):
    _resolver = Resolver()
    path_template = _resolver.client.tk.templates[templ_name]
    _generate_uri(fields, path_template, proj)


def is_tank_asset(filepath, tk):
    templ = tk.template_from_path(filepath)
    return True if templ else False


def resolve(path):
    """
    :param str path: it might be path or uri
    :return: uri or real path
    """
    if path.startswith('tank:'):
        return uri_to_filepath(path)
    else:
        return filepath_to_uri(path)
