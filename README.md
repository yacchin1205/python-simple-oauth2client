# python-simple-oauth2client

This is based on https://github.com/orcasgit/python-misfit .

## Requirements

* Python >= 2.6, Python >= 3.3, or PyPy. You can download it from `here <https://www.python.org/>`_
* Pip. If you have Python >= 2.7.9 or >= 3.4 then you already have ``pip``. Otherwise, please follow `these instructions <https://pip.pypa.io/en/latest/installing.html>`_

## Installing

```
pip install -r requirements.txt
```

## Usage

See help:

```
python -m simple_oauthclient.cli -h
```

Get OAuth token by execution the following command:

```
python -m simple_oauthclient.cli authorize \
  --client_id=<client_id> \
  --client_secret=<client_secret> \
  --authorize_uri=<authorize_uri> \
  --fetch_token_uri=<fetch_token_uri> \
  --scope=<scope1> --scope=<scope2> \
  --redirect_uri=<redirect_uri>
```

For example,

```
python -m simple_oauthclient.cli authorize \
  --client_id=******************* \
  --client_secret=************************************ \
  --authorize_uri="https://github.com/login/oauth/authorize" \
  --fetch_token_uri="https://github.com/login/oauth/access_token" \
  --scope=user --scope=repo \
  --redirect_uri="http://127.0.0.1:8080/"
```

Then, `simple_oauthclient.cfg` file including `access_token` was created.

```
cat simple_oauthclient.cfg
```
