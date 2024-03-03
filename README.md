# Beauty Parlor Salon

backen API Server

## premise

### local

- Docker Container
  - Python: 3.12.1, FastAPI
  - MySQL: 8.0
  - MariaDB: 11.3
- Mac M1

### AWS

- AWS IMA Account
- aws configure
  - AWS: aws-cli/2.2.36 Python/3.8.8 Darwin/20.6.0 exe/x86_64 prompt/off
  - serverless: Framework Core: 3.2.1, Plugin: 6.1.0, SDK: 4.3.1
  - node: v16.8.0

## local Flow

```bash
# 1
add `.env`
# 2. build. MariaDB, Python
docker-compose up -d --build
# 3. exec
docker-compose exec beauty-parlor-salon-dev bash
# 4. Run test
## all
python3 -m pytest -sv
## single
python3 -m pytest -sv tests/test_app.py::test_read_main
```

## ECR Flow

1. Create ECR Repository
2. add `.env`
3. `docker-compose build`
4. `docker push {ECR_IMAGE}:latest`
   - ex: ECR_IMAGE: `123456789123.dkr.ecr.{region}.amazonaws.com/lambda-container`
5. Create Lambda Function
6. `sls deploy`
7. test API endpoint

## .env list

The list of `.env` is raised below

```bash
# aws
ECR_IMAGE=xxx
ECR_DIGEST=sha256:xxx
REGION=ap-northeast-1

# mariadb
TAG=11.3

DB_PORT=3306
DATABASE=beauty_salon
MYSQL_DATABASE=mariadb
TEST_DATABASE=test_beauty_salon

## user
MYSQL_USER=user
MYSQL_PASSWORD=password

MYSQL_ROOT_USER=root
MYSQL_ROOT_PASSWORD=password

# const
SECRET_KEY=xxx
```

## Reference

- [mysql 8.0 で deadlock を再現する](https://kazusabook.notion.site/mysql-8-0-deadlock-1f22005aec42495a987057fffe9671a7)
