# Formatting and style
Code can be auto-formatted using [`black`](https://black.readthedocs.io/en/stable/):

## Docker

```bash
docker run -it -v $PWD:/app "{{cookiecutter.image_organization}}/{{cookiecutter.image_name}}:latest" black
```
## Anaconda

```bash
source activate {{cookiecutter.repo_name}}
# execute the following command from the project root:
black
```

# Typehints

The code makes use of Python type hints.


## Docker

To perform type checking, run the following command:

```bash
docker run -it -v $PWD:/app "{{cookiecutter.image_organization}}/{{cookiecutter.image_name}}:latest" mypy --ignore-missing-imports --follow-imports=skip --strict-optional .
```

## Anaconda

```bash
source activate {{cookiecutter.repo_name}}
# execute the following command from the project root:
mypy --ignore-missing-imports --follow-imports=skip --strict-optional .
```