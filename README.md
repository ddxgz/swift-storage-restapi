swift-webstorage-restapi
================

API v1:
---------------
####GET

> /v1/disk/
>> return a json contains metadate and all the files and folds

> /v1/disk/{path2file or path}
>> return a tempo_url which can download the file

####PUT

> /v1/disk/{path2file or path}
>> return a storage_url and auth_token which can be used to PUT the file to the storage_url with auth_token in the header

####DELETE
> /v1/disk/{path2file or path}
>> return an info tells whether the delete success or not






TODO
---------------
- Separate login
- Verify if the request if ok, such as if the file exists when get,
	or the path2file is a fold
- set the temp_key expires time based on the size of target file


BUG
---------------


Functions
---------------
- Download/upload files from/to Swift
- Share files with links
- Provide API for Android client

Requirements
---------------
- Python >= 2.7 or 3.4
- python-swiftclient >= 2.4.0
- Gunicorn or uWsgi
- Falcon >= 0.3.0
- peewee
