# tftp
A simple tftp server with api management.


## Usage
- tftp service
```sh
sudo python3 -m  tftp.server --tftp-file-dir `pwd`/files/
```



# api


## Environment [dev]

- Python: 3.10
- Flask: 3.0.3


## Usage
- api service
```sh
sudo python3 -m api.server --root-path `pwd`/files/
```


