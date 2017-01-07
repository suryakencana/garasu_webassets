"""
 # Copyright (c) 06 2016 | suryakencana
 # 6/13/16 nanang.ask@kubuskotak.com
 # This program is free software; you can redistribute it and/or
 # modify it under the terms of the GNU General Public License
 # as published by the Free Software Foundation; either version 2
 # of the License, or (at your option) any later version.
 #
 # This program is distributed in the hope that it will be useful,
 # but WITHOUT ANY WARRANTY; without even the implied warranty of
 # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 # GNU General Public License for more details.
 #
 # You should have received a copy of the GNU General Public License
 # along with this program; if not, write to the Free Software
 # Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
 #  __init__.py.py
"""
from contextlib import closing
import fileinput
import logging
from os import path
import os
from pyramid.path import AssetResolver
from pyramid.settings import asbool
import six
from webassets import Environment, Bundle
from webassets.loaders import YAMLLoader


LOG = logging.getLogger(__name__)


def includeme(config):
    """pyramid include. declare the add_thumb_view"""
    here = os.path.dirname(__file__)
    settings = config.registry.settings
    conf_assets = settings['garasu_webassets']

    config_dir = conf_assets.get('config', '{}/configs'.format(here))
    LOG.debug(config_dir)
    # config_dir = AssetResolver(None).resolve(config_dir).abspath()
    asset_dir = conf_assets.get('assets', '{}/assets'.format(here))
    LOG.debug(asset_dir)
    # asset_dir = AssetResolver(None).resolve(asset_dir).abspath()

    env = Environment(directory=asset_dir, url=conf_assets['url'])
    env.manifest = conf_assets['manifest']
    env.debug = asbool(conf_assets['debug'])
    env.cache = asbool(conf_assets['cache'])
    env.auto_build = asbool(conf_assets['auto_build'])

    def text(value):
        if type(value) is six.binary_type:
            return value.decode('utf-8')
        else:
            return value

    def yaml_stream(fname, mode):
        if path.exists(fname):
            return open(fname, mode)
        raise FileNotFoundError

    fin = fileinput.input('/'.join([config_dir, conf_assets['bundles']]),
                          openhook=yaml_stream)
    with closing(fin):
        lines = [text(line).rstrip() for line in fin]

    stream_yaml = six.StringIO('\n'.join(lines))
    loader = YAMLLoader(stream_yaml)
    result = loader.load_bundles()
    env.register(result)

    # for item in env:
    #     LOG.debug(item.output)
    #     path_file = '/'.join([public_dir, item.output])
    #     src_file = '/'.join([asset_dir, item.output])
    #     shutil.copy(src_file, path_file)

    def _get_assets(request, *args, **kwargs):
        bundle = Bundle(*args, **kwargs)
        with bundle.bind(env):
            urls = bundle.urls()
        return urls
    config.add_request_method(_get_assets, 'web_assets')

    def _get_assets_env(request):
        return env
    config.add_request_method(_get_assets_env, 'web_env', reify=True)
