# RAG Applications

This project has implementations of RAG in different use cases.

## Requirements

- python 3.8 or later

### Installing python using Miniconda

1) Downloading and installing Miniconda from [here](https://docs.anaconda.com/free/miniconda/#quick-command-line-install)
2) Creating a new environment using the following command:
```bash
$ conda create -n env_name python=3.8
```
3) Activating your environment using following command:
```bash
$ conda activate env_name
```

### Installation Neccessary Libraries
```bash
$ pip install -r requirements.txt
```
### Setup the environment variables
```bash
$ copy .env.example .env
```
Set your environment variables as your own variables like they're showed in `.env.example`

## Run Docker Compose Services

```bash
$ cd docker
$ cp .env.example .env
```
- Update `.env` with your credentials

- Use the below commands to run the services:
```bash 
$ cd docker
$ docker compose -f "docker-compose.yml" up -d
```

## Run FastAPI server
```bash
$ uvicorn main:app --reload --host 0.0.0.0 --port 5000
```


