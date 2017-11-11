# Backend API for Sivmetrics Dashboard

## Running Application

```console
$ gunicorn --reload 'backend.app:create_app()'
```

### Sending HTTP Requests via HTTPie

```console
$ http GET http://127.0.0.1:8000/stops/1066
```

## Running Tests

```console
$ py.test --cov=backend tests/
```

