from __future__ import absolute_import, division, print_function

from wsgiref import simple_server
import falcon
import json
import Queue
import sys, os
import datetime
import logging

from swiftutils import get_temp_key, get_temp_url

import swiftclient
# from swiftclient import client
import peewee

from config import Config
from models import AccountModel, database
from myexceptions import UserNotExistException, PasswordIncorrectException
import keystonewrap
import swiftwrap

# logging.basicConfig(format='===========My:%(levelname)s:%(message)s=========', 
#     level=logging.DEBUG)
#sys.path.append('.')


class PathListener:
    def __init__(self):
        self.conf = Config()

    def on_get(self, req, resp, path, thefile):
        """
        unuseful at present
        """
        try:
            username = req.get_header('username') or 'un'
            password = req.get_header('password') or 'pw'
            logging.debug('username:%s, password:%s' % (username, password))
        except:
            raise falcon.HTTPBadRequest('bad req', 
                'when read from req, please check if the req is correct.')
        try:
            # if path2file:
            logging.debug('path2file:%s, file:%s' % (path, thefile))
            # logging.debug('self.conf.auth_url: %s,  conf.auth_version: %s' % (
            #     self.conf.auth_url, self.conf.auth_version))
            # conn = swiftclient.Connection(self.conf.auth_url,
            #                       self.conf.account_username,
            #                       self.conf.password,
            #                       auth_version=self.conf.auth_version or 1)
            # meta, objects = conn.get_container(self.conf.container)
            # meta, obj = conn.get_object(self.conf.container, path2file)
            # logging.debug('meta: %s,   obj: %s' % (meta, obj))

            storage_url, auth_token = swiftclient.client.get_auth(
                                    self.conf.auth_url,
                                    self.conf.account_username,
                                  self.conf.password,
                                  auth_version=1)
            # logging.debug('rs: %s'% swiftclient.client.get_auth(
            #                         self.conf.auth_url,
            #                         self.conf.account_username,
            #                       self.conf.password,
            #                       auth_version=1))
            logging.debug('url:%s, toekn:%s' % (storage_url, auth_token))
         
            temp_url = get_temp_url(storage_url, auth_token,
                                          self.conf.disk_container, path2file)
            resp_dict = {}
            # resp_dict['meta'] = meta
            # objs = {}
            # for obj in objects:
            #     logging.debug('obj:%s' % obj.get('name'))
            #     objs[obj.get('name')] = obj
            resp_dict['temp_url'] = temp_url
            logging.debug('resp_dict:%s' % resp_dict)

        except:
            raise falcon.HTTPBadRequest('bad req', 
                'username or password not correct!')
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(resp_dict, encoding='utf-8', 
            sort_keys=True, indent=4)
        resp.body = temp_url
        # resp.stream = obj
        # resp.head = meta


class HomeListener:
    def __init__(self):
        self.conf = Config()

    def on_get(self, req, resp):
        """
        :param req.header.username: the username, should be tenant:user when dev
        :param req.header.password: password 

        :returns: a json contains all objects in disk container, and metameata
                {"meta":{}, "objects":{"obj1": {}}}
        """
        resp_dict = {}
        try:
            username = req.get_header('username') or 'un'
            password = req.get_header('password') or 'pw'
            logging.debug('username:%s, password:%s' % (username, password))
        except:
            raise falcon.HTTPBadRequest('bad req', 
                'when read from req, please check if the req is correct.')
        try:
            # if path2file:
            logging.debug('self.conf.auth_url: %s,  conf.auth_version: %s' % (
                self.conf.auth_url, self.conf.auth_version))
            conn = swiftclient.Connection(self.conf.auth_url,
                                  self.conf.account_username,
                                  self.conf.password,
                                  auth_version=self.conf.auth_version)
            meta, objects = conn.get_container(username+'_'+
                self.conf.container)
            logging.debug('meta: %s,   objects: %s' % (meta, objects))
            resp_dict = {}
            resp_dict['meta'] = meta
            logging.debug('resp_dict:%s' % resp_dict)
            objs = {}
            for obj in objects:
                logging.debug('obj:%s' % obj.get('name'))
                objs[obj.get('name')] = obj
            resp_dict['objects'] = objs
        except:
            raise falcon.HTTPBadRequest('bad req', 
                'username or password not correct!')

        # try:
        #     logging.debug('self.conf.auth_url: %s,  conf.auth_version: %s' % (
        #         self.conf.auth_url, self.conf.auth_version))
        #     # user = AccountModel.get(AccountModel.username==username, 
        #     #                             AccountModel.password==password)
        #     user = AccountModel.auth(username, password)
        #     # logging.debug('1st resp_dict:%s' % resp_dict)

        #     resp_dict['info'] = 'successfully get user:%s' % username
        #     resp_dict['username'] = user.username
        #     resp_dict['email'] = user.email
        #     resp_dict['account_level'] = user.account_level
        #     resp_dict['join_date'] = user.join_date
        #     resp_dict['keystone_info'] = user.keystone_info
        #     logging.debug('1st resp_dict:%s' % resp_dict)
        #     conn = swiftclient.Connection(self.conf.auth_url,
        #                           user.keystone_tenant+':'+user.keystone_username,
        #                           user.password,
        #                           auth_version=self.conf.auth_version or 1)
        #     meta, objects = conn.get_container(self.conf.disk_container)
        #     logging.debug('meta: %s,   objects: %s' % (meta, objects))
        #     resp_dict = {}
        #     resp_dict['meta'] = meta
        #     logging.debug('resp_dict:%s' % resp_dict)
        #     objs = {}
        #     for obj in objects:
        #         logging.debug('obj:%s' % obj.get('name'))
        #         objs[obj.get('name')] = obj
        #     resp_dict['objects'] = objs        
        # except UserNotExistException:
        #     logging.debug('in UserNotExistException')

        #     resp_dict['info'] = 'user:%s does not exist' % username
        #     resp.body = json.dumps(resp_dict, encoding='utf-8')
        # except PasswordIncorrectException:
        #     logging.debug('in PasswordIncorrectException')
        #     resp_dict['info'] = 'user:%s password not correct' % username
        #     resp.body = json.dumps(resp_dict, encoding='utf-8')
        
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(resp_dict, encoding='utf-8', 
            sort_keys=True, indent=4)


    def on_post(self, req, resp):
        """
        unuseful at present
        """
        try:
            username = req.get_header('username') or 'un'
            password = req.get_header('password') or 'pw'
            logging.debug('username:%s, password:%s' % (username, password))
        except:
            raise falcon.HTTPBadRequest('bad req', 
                'when read from req, please check if the req is correct.')
        try:
            # post_data = req.env
            logging.debug('env:%s , \nstream:%s, \ncontext:%s, \ninput:%s' % (
                req.env, req.stream.read(), req.context, req.env['wsgi.input'].read()))
            # logging.debug('self.conf.auth_url: %s,   conf.auth_version: %s' % (
            #     self.conf.auth_url, self.conf.auth_version))
            conn = swiftclient.Connection(self.conf.auth_url,
                                  self.conf.account_username,
                                  self.conf.password,
                                  auth_version=self.conf.auth_version or 1)
            conn.put_object('disk', 'testfile', req.stream, 
                chunk_size=65536)
            # meta, objects = conn.get_container(self.conf.container)
            # logging.debug('meta: %s,   objects: %s' % (meta, objects))
            # resp_dict = {}
            # resp_dict['meta'] = meta
            # logging.debug('resp_dict:%s' % resp_dict)
            # objs = {}
            # for obj in objects:
            #     logging.debug('obj:%s' % obj.get('name'))
            #     objs[obj.get('name')] = obj
            # resp_dict['objects'] = objs
        except:
            raise falcon.HTTPBadRequest('bad req', 
                'username or password not correct!')
        # resp.status = falcon.HTTP_202
        # resp.body = json.dumps(resp_dict, encoding='utf-8', sort_keys=True, indent=4)

        resp.status = falcon.HTTP_201
        resp.body = json.dumps({}, encoding='utf-8')

    def on_delete(self, req, resp):
        pass


class DiskSinkAdapter(object):
    conf = Config()

    def __call__(self, req, resp, path2file):
        """
        :param req.header.username: the username, should be tenant:user when dev
        :param req.header.password: password 
        :path2file the part in the request url /v1/disk/(?P<path2file>.+?), to 
            identify the resource to manipulate 

        :returns: a json contains correspond response info
            GET: the temp_url of the file in a resp dict
            PUT: the auth_token and storage_url in a resp dict for uploading file
            DELETE: description of if the operation success or fail
        """
        logging.debug('in sink req.method:%s  path2file:%s' % (
            req.method, path2file))
        try:
            username = req.get_header('username') or 'un'
            password = req.get_header('password') or 'pw'
            logging.debug('username:%s, password:%s' % (username, password))
        except:
            raise falcon.HTTPBadRequest('bad req', 
                'when read from req, please check if the req is correct.')

        if req.method == 'GET':
            try:
                storage_url, auth_token = swiftclient.client.get_auth(
                                        self.conf.auth_url,
                                        self.conf.account_username,
                                      self.conf.password,
                                      auth_version=1)
                logging.debug('url:%s, toekn:%s' % (storage_url, auth_token))
                temp_url = get_temp_url(storage_url, auth_token,
                                    username+'_'+self.conf.disk_container, 
                                    path2file)
                resp_dict = {}
                # resp_dict['meta'] = meta
                resp_dict['temp_url'] = temp_url
                resp_dict['path2file'] = path2file
                resp.status = falcon.HTTP_200
                # logging.debug('resp_dict:%s' % resp_dict)

            except:
                raise falcon.HTTPBadRequest('bad req', 
                    'username or password not correct!')

        elif req.method == 'PUT':
            try:
                # if path2file:
                logging.debug(' path2file:%s' % (path2file))

                logging.debug('env:%s , \nstream:%s, \ncontext:, \ninput:' % (
                req.env, req.stream.read()))

                storage_url, auth_token = swiftclient.client.get_auth(
                                        self.conf.auth_url,
                                        self.conf.account_username,
                                      self.conf.password,
                                      auth_version=self.conf.auth_version)
      
                logging.debug('url:%s, token:%s' % (storage_url, auth_token))
             
                # temp_url = get_temp_url(storage_url, auth_token,
                #                               self.conf.container, path2file)
                resp_dict = {}
                # resp_dict['meta'] = meta
                # objs = {}
                # for obj in objects:
                #     logging.debug('obj:%s' % obj.get('name'))
                resp_dict['auth_token'] = auth_token
                resp_dict['storage_url'] = storage_url + \
                    +'/'+username+'_'+self.conf.disk_container + path2file
                resp.status = falcon.HTTP_201
                logging.debug('resp_dict:%s' % resp_dict)

            except:
                raise falcon.HTTPBadRequest('bad req', 
                    'username or password not correct!')

        elif req.method == 'DELETE':
            resp_dict = {}

            try:
                # if path2file:
                logging.debug(' path2file:%s' % (path2file))

                logging.debug('env:%s , \nstream:%s, \ncontext:, \ninput:' % (
                req.env, req.stream.read()))

                # storage_url, auth_token = swiftclient.client.get_auth(
                #                         self.conf.auth_url,
                #                         self.conf.account_username,
                #                       self.conf.password,
                #                       auth_version=1)
                # logging.debug('url:%s, token:%s' % (storage_url, auth_token))
             
                # temp_url = get_temp_url(storage_url, auth_token,
                #                               self.conf.container, path2file)
                
                conn = swiftclient.client.Connection(self.conf.auth_url,
                                  self.conf.account_username,
                                  self.conf.password,
                                  auth_version=self.conf.auth_version)
                meta, objects = conn.get_container(
                    username+'_'+self.conf.disk_container, 
                    prefix=path2file)
                logging.debug('meta: %s,  \n objects: %s' % (meta, objects))
                if objects:
                    for obj in objects:
                        conn.delete_object(
                            username+'_'+self.conf.disk_container, 
                            obj['name'])
                    resp_dict['description'] = 'All file have been deleted'
                else:
                    resp_dict['description'] = 'There is no file to be \
                        deleted'
                # resp_dict['meta'] = meta
                # objs = {}
                # for obj in objects:
                #     logging.debug('obj:%s' % obj.get('name'))
                # resp_dict['auth_token'] = auth_token
                # resp_dict['storage_url'] = storage_url + '/' + path2file
                resp.status = falcon.HTTP_204
                logging.debug('resp_dict:%s' % resp_dict)

            except:
                raise falcon.HTTPBadRequest('bad req', 
                    'username or password not correct!')

        resp.body = json.dumps(resp_dict, encoding='utf-8', 
            sort_keys=True, indent=4)


class AccountListener:
    def __init__(self):
        self.conf = Config()

    def on_post(self, req, resp):
        """
        :param req.header.username: the username
        :param req.header.password: password 
        :param req.header.email: email 

        :returns: a json contains info of the operation, if the register is
            success or failed
        """
        logging.debug('in account post')
        resp_dict = {}

        try:
            username = req.get_header('username') or 'un'
            password = req.get_header('password') or 'pw'
            email = req.get_header('email') or 'email'
            # params = req.get_param_as_list()
            # logging.debug('params:%s'%params)
            logging.debug('username:%s, password:%s, email:%s' % 
                (username, password, email))
        except:
            raise falcon.HTTPBadRequest('bad req', 
                'when read from req, please check if the req is correct.')
        
        try:
            logging.debug('in account post create')


            conn = swiftclient.client.Connection(self.conf.auth_url,
                                  self.conf.account_username,
                                  self.conf.password,
                                  auth_version=self.conf.auth_version)
            conn.put_container(username+'_'+self.conf.disk_container)
            resp_dict['info'] = 'successfully create user:%s' % username
            resp.status = falcon.HTTP_201
        except:
            raise falcon.HTTPBadRequest('bad req', 
                'when access to Swift.')
        resp.body = json.dumps(resp_dict, encoding='utf-8')

    def on_get(self, req, resp):
        """
        :returns: info of the user in the req.header
        """
        logging.debug('in account get')
        resp_dict = {}

        try:
            username = req.get_header('username') or 'un'
            password = req.get_header('password') or 'pw'
            # email = req.get_header('email') or 'email'
            # params = req.get_param_as_list()
            # logging.debug('params:%s'%params)
            logging.debug('username:%s, password:%s' % 
                (username, password))
        except:
            raise falcon.HTTPBadRequest('bad req', 
                'when read from req, please check if the req is correct.')
        
        try:
            logging.debug('in account model get')
            conn = swiftclient.client.Connection(self.conf.auth_url,
                                  self.conf.account_username,
                                  self.conf.password,
                                  auth_version=self.conf.auth_version)
            meta, objects = conn.get_container(username+'_'+
                self.conf.container)
            logging.debug('meta: %s,   ' % (meta))
            resp_dict = {}
            resp_dict['meta'] = meta

            resp.status = falcon.HTTP_200
        except UserNotExistException:
            logging.debug('in UserNotExistException')

            resp_dict['info'] = 'user:%s does not exist' % username
            resp.body = json.dumps(resp_dict, encoding='utf-8')

        # except:
        #     # `username` is a unique column, so this username already exists,
        #     # making it safe to call .get().
        #     resp_dict['info'] = 'user:%s does not exist or password not right' % username
        #     logging.debug('user does not exist or password not right...')
        #     resp.status = falcon.HTTP_200
        else:
            resp.body = json.dumps(resp_dict, encoding='utf-8')


    def on_delete(self, req, resp):
        """
        delete the account, and all the files belong to this account
        """
        pass

