# saus
SAUS = Such A URL Shortener :)

## Local Development Environment
### Dependencies
- mysql/mariadb, check [saus/settings.py](saus/settings.py)
- redis, check [saus/settings.py](saus/settings.py)
- python 3.8

### Setup Dev Server
```
pip3 install --user -r requirements.txt
python3 manage.py migrate
python3 manage.py runserver
curl http://localhost:8000
```

## CI
See GitHub Actions pipeline [.github/workflow/main.yaml](.github/workflow/main.yaml)
