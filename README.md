###About
A tool to make a report about the number of tags of images in the GitLab docker registry.


###Installation
```shell script
git clone git@github.com:14DF397FCA/gitlab_registry_reporter.git
cd gitlab_registry_reporter
python3 -m venv ./venv
source ./venv/bin/activate
./venv/bin/pip install -r requirements.txt
./venv/bin/python3 main.py -s https://gitlab.example.com -t yourprivatetoken
```

###Usage
```shell script
usage: main.py [-h] -s SERVER -t TOKEN [-l LEVEL]

optional arguments:
  -h, --help            show this help message and exit
  -s SERVER, --server SERVER
                        Address of your Gitlab server, with proto (http or https)
  -t TOKEN, --token TOKEN
                        Your private API token to your Gitlab server
  -l LEVEL, --level LEVEL
                        Log level
```