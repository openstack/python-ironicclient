#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os

import dogpile.cache
import mock

from ironicclient.common import filecache
from ironicclient.tests.unit import utils


class FileCacheTest(utils.BaseTestCase):

    def test__build_key_ok(self):
        result = filecache._build_key('localhost', '5000')
        self.assertEqual('localhost:5000', result)

    def test__build_key_none(self):
        result = filecache._build_key(None, None)
        self.assertEqual('None:None', result)

    @mock.patch.object(os.environ, 'get', autospec=True)
    @mock.patch.object(os.path, 'exists', autospec=True)
    @mock.patch.object(os, 'makedirs', autospec=True)
    @mock.patch.object(dogpile.cache, 'make_region', autospec=True)
    def test__get_cache_mkdir(self, mock_makeregion, mock_makedirs,
                              mock_exists, mock_get):
        cache_val = 6
        # If not present in the env, get will return the defaulted value
        mock_get.return_value = filecache.DEFAULT_EXPIRY
        filecache.CACHE = None
        mock_exists.return_value = False
        cache_region = mock.Mock(spec=dogpile.cache.region.CacheRegion)
        cache_region.configure.return_value = cache_val
        mock_makeregion.return_value = cache_region
        self.assertEqual(cache_val, filecache._get_cache())
        mock_exists.assert_called_once_with(filecache.CACHE_DIR)
        mock_makedirs.assert_called_once_with(filecache.CACHE_DIR)
        mock_get.assert_called_once_with(filecache.CACHE_EXPIRY_ENV_VAR,
                                         mock.ANY)
        cache_region.configure.assert_called_once_with(
            mock.ANY,
            arguments=mock.ANY,
            expiration_time=filecache.DEFAULT_EXPIRY)

    @mock.patch.object(os.environ, 'get', autospec=True)
    @mock.patch.object(os.path, 'exists', autospec=True)
    @mock.patch.object(os, 'makedirs', autospec=True)
    @mock.patch.object(dogpile.cache, 'make_region', autospec=True)
    def test__get_cache_expiry_set(self, mock_makeregion, mock_makedirs,
                                   mock_exists, mock_get):
        cache_val = 5643
        cache_expiry = '78'
        mock_get.return_value = cache_expiry
        filecache.CACHE = None
        mock_exists.return_value = False
        cache_region = mock.Mock(spec=dogpile.cache.region.CacheRegion)
        cache_region.configure.return_value = cache_val
        mock_makeregion.return_value = cache_region
        self.assertEqual(cache_val, filecache._get_cache())
        mock_get.assert_called_once_with(filecache.CACHE_EXPIRY_ENV_VAR,
                                         mock.ANY)
        cache_region.configure.assert_called_once_with(
            mock.ANY,
            arguments=mock.ANY,
            expiration_time=int(cache_expiry))

    @mock.patch.object(filecache.LOG, 'warning', autospec=True)
    @mock.patch.object(os.environ, 'get', autospec=True)
    @mock.patch.object(os.path, 'exists', autospec=True)
    @mock.patch.object(os, 'makedirs', autospec=True)
    @mock.patch.object(dogpile.cache, 'make_region', autospec=True)
    def test__get_cache_expiry_set_invalid(self, mock_makeregion,
                                           mock_makedirs, mock_exists,
                                           mock_get, mock_log):
        cache_val = 5643
        cache_expiry = 'Rollenhagen'
        mock_get.return_value = cache_expiry
        filecache.CACHE = None
        mock_exists.return_value = False
        cache_region = mock.Mock(spec=dogpile.cache.region.CacheRegion)
        cache_region.configure.return_value = cache_val
        mock_makeregion.return_value = cache_region
        self.assertEqual(cache_val, filecache._get_cache())
        mock_get.assert_called_once_with(filecache.CACHE_EXPIRY_ENV_VAR,
                                         mock.ANY)
        cache_region.configure.assert_called_once_with(
            mock.ANY,
            arguments=mock.ANY,
            expiration_time=filecache.DEFAULT_EXPIRY)
        log_dict = {'curr_val': cache_expiry,
                    'default': filecache.DEFAULT_EXPIRY,
                    'env_var': filecache.CACHE_EXPIRY_ENV_VAR}
        mock_log.assert_called_once_with(mock.ANY, log_dict)

    @mock.patch.object(os.path, 'exists', autospec=True)
    @mock.patch.object(os, 'makedirs', autospec=True)
    def test__get_cache_dir_already_exists(self, mock_makedirs, mock_exists):
        cache_val = 5552368
        mock_exists.return_value = True
        filecache.CACHE = cache_val
        self.assertEqual(cache_val, filecache._get_cache())
        self.assertEqual(0, mock_exists.call_count)
        self.assertEqual(0, mock_makedirs.call_count)

    @mock.patch.object(dogpile.cache.region, 'CacheRegion', autospec=True)
    @mock.patch.object(filecache, '_get_cache', autospec=True)
    def test_save_data_ok(self, mock_get_cache, mock_cache):
        mock_get_cache.return_value = mock_cache
        host = 'fred'
        port = '1234'
        hostport = '%s:%s' % (host, port)
        data = 'some random data'
        filecache.save_data(host, port, data)
        mock_cache.set.assert_called_once_with(hostport, data)

    @mock.patch.object(os.path, 'isfile', autospec=True)
    @mock.patch.object(dogpile.cache.region, 'CacheRegion', autospec=True)
    @mock.patch.object(filecache, '_get_cache', autospec=True)
    def test_retrieve_data_ok(self, mock_get_cache, mock_cache, mock_isfile):
        s = 'spam'
        mock_isfile.return_value = True
        mock_cache.get.return_value = s
        mock_get_cache.return_value = mock_cache
        host = 'fred'
        port = '1234'
        hostport = '%s:%s' % (host, port)
        result = filecache.retrieve_data(host, port)
        mock_cache.get.assert_called_once_with(hostport, expiration_time=None)
        self.assertEqual(s, result)

    @mock.patch.object(os.path, 'isfile', autospec=True)
    @mock.patch.object(dogpile.cache.region, 'CacheRegion', autospec=True)
    @mock.patch.object(filecache, '_get_cache', autospec=True)
    def test_retrieve_data_ok_with_expiry(self, mock_get_cache, mock_cache,
                                          mock_isfile):
        s = 'spam'
        mock_isfile.return_value = True
        mock_cache.get.return_value = s
        mock_get_cache.return_value = mock_cache
        host = 'fred'
        port = '1234'
        expiry = '987'
        hostport = '%s:%s' % (host, port)
        result = filecache.retrieve_data(host, port, expiry)
        mock_cache.get.assert_called_once_with(hostport,
                                               expiration_time=expiry)
        self.assertEqual(s, result)

    @mock.patch.object(os.path, 'isfile', autospec=True)
    @mock.patch.object(dogpile.cache.region, 'CacheRegion', autospec=True)
    @mock.patch.object(filecache, '_get_cache', autospec=True)
    def test_retrieve_data_not_found(self, mock_get_cache, mock_cache,
                                     mock_isfile):
        mock_isfile.return_value = True
        mock_cache.get.return_value = dogpile.cache.api.NO_VALUE
        mock_get_cache.return_value = mock_cache
        host = 'fred'
        port = '1234'
        hostport = '%s:%s' % (host, port)
        result = filecache.retrieve_data(host, port)
        mock_cache.get.assert_called_once_with(hostport, expiration_time=None)
        self.assertIsNone(result)

    @mock.patch.object(os.path, 'isfile', autospec=True)
    def test_retrieve_data_no_cache_file(self, mock_isfile):
        mock_isfile.return_value = False
        self.assertIsNone(filecache.retrieve_data(host='spam', port='eggs'))
