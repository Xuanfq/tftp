#!/bin/bash
set -x

API_PORT=5000
API_NAME=api
API_AUTH_USERNAME=admin
API_AUTH_PASSWORD=admin

createfolderpath=folder1

uploadpath=$createfolderpath
uploadfile=test-api.sh

downloadpath=$uploadpath/$uploadfile

searchpath=$uploadpath
searchkey=*

listcontentpath=$uploadpath

deletefilepath=$uploadpath/$uploadfile

deletefolderpath=$uploadpath

AUTH_RESULT=$(curl -X POST http://localhost:$API_PORT/$API_NAME/login -d username=$API_AUTH_USERNAME -d password=$API_AUTH_PASSWORD)
AUTH_TOKEN=$(echo $AUTH_RESULT | grep -o '"data":"[^"]*"' | cut -d':' -f2- | tr -d '"')
echo $AUTH_TOKEN

echo create folder
curl http://127.0.0.1:$API_PORT/$API_NAME/add/folder -X POST -d "path=$createfolderpath" -d "token=$AUTH_TOKEN"

echo upload file
curl http://127.0.0.1:$API_PORT/$API_NAME/upload/file -X POST -F "file=@$uploadfile" -F "path=$uploadpath" -F "token=$AUTH_TOKEN"

echo download file
curl http://127.0.0.1:$API_PORT/$API_NAME/download/file?path=$downloadpath\&token=$AUTH_TOKEN

echo search
curl http://127.0.0.1:$API_PORT/$API_NAME/search/file?path=$searchpath\&key=$searchkey\&token=$AUTH_TOKEN

echo list path contents
curl http://127.0.0.1:$API_PORT/$API_NAME/get/list?path=$listcontentpath\&token=$AUTH_TOKEN

echo delete file
curl http://127.0.0.1:$API_PORT/$API_NAME/delete/file -X POST -d "path=$deletefilepath" -d "token=$AUTH_TOKEN"

echo delete folder
curl http://127.0.0.1:$API_PORT/$API_NAME/delete/folder -X POST -d "path=$deletefolderpath" -d "token=$AUTH_TOKEN"








