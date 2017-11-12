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

### Note

* [can't patch C type objects](https://stackoverflow.com/questions/4481954/python-trying-to-mock-datetime-date-today-but-not-working)
* [do partial mocking](http://www.voidspace.org.uk/python/mock/examples.html#partial-mocking)
