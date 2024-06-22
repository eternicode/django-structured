# Django: Structured

This project offers a modern structure for Django projects. It is based on the following principles:

* **Fast start**: A new _Structured_ project goes beyond Django to provide everything you need to skip tedious project configuration and start writing your app immediately.
* **Best practices**: Django projects have common patterns, and common pitfalls. _Structured_ aims to help you keep best practices from the start.
* **Discoverability**: _Structured_ wants your life to be easy, and part of that is not hunting for things you know (or don't know) exist.
* **Flexibility**: _Structured_ tries to use sensible defaults, but every project is different.

Strtuctured supports Django 3.2, 4.2, and 5.0.

## Install

Install `django-structured` with your favorite package manager.

```
pip install django-structured
```

Structured doesn't depend on Django directly. If the `django` module is available to Structured, it will use the version found there as a default for the `--django` option. Otherwise, Django does not need to be installed alongside Structured.

## Usage



## Features

### Pytest plugins

* pytest-cov: Measures and reports code coverage
* pytest-xdist: Run tests in parallel
* pytest-mock: Mocking fixtures
* pytest-randomly: Randomize test order (this helps flush out hidden dependencies between tests)
* pytest-sugar: Show test results in a more readable format
* pytest-clarity: Show test results in a more readable format
