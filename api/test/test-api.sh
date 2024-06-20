#!/bin/bash
set -x

API_PORT=5000
API_NAME=api


createfolderpath=folder1

uploadpath=$createfolderpath
uploadfile=test-api.sh

downloadpath=$uploadpath/$uploadfile

searchpath=$uploadpath
searchkey=*

listcontentpath=$uploadpath

deletefilepath=$uploadpath/$uploadfile

deletefolderpath=$uploadpath


echo create folder
curl http://127.0.0.1:$API_PORT/$API_NAME/add/folder -X POST -d "path=$createfolderpath"

echo upload file
curl http://127.0.0.1:$API_PORT/$API_NAME/upload/file -X POST -F "file=@$uploadfile" -F "path=$uploadpath"

echo download file
curl http://127.0.0.1:$API_PORT/$API_NAME/download/file?path=$downloadpath

echo search
curl http://127.0.0.1:$API_PORT/$API_NAME/search/file?path=$searchpath\&key=$searchkey

echo list path contents
curl http://127.0.0.1:$API_PORT/$API_NAME/get/list?path=$listcontentpath

echo delete file
curl http://127.0.0.1:$API_PORT/$API_NAME/delete/file -X POST -d "path=$deletefilepath"

echo delete folder
curl http://127.0.0.1:$API_PORT/$API_NAME/delete/folder -X POST -d "path=$deletefolderpath"








