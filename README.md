# Beauty Parlor Salon

## Image

## premise

* Mac M1
* AWS IMA Account
* aws configure
* AWS: aws-cli/2.2.36 Python/3.8.8 Darwin/20.6.0 exe/x86_64 prompt/off
* Docker: 20.10.8, build 3967b7d
* Python: 3.9.1
* serverless: Framework Core: 3.2.1, Plugin: 6.1.0, SDK: 4.3.1
* node: v16.8.0

## Flow

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
TAG=10.7.1

DB_PORT=3306
DATABASE=xxx
MYSQL_DATABASE=xxx

TEST_DATABASE=xxx

## user
MYSQL_USER=xxx
MYSQL_PASSWORD=xxx

MYSQL_ROOT_USER=xxx
MYSQL_ROOT_PASSWORD=xxx

# const
SECRET_KEY=xxx
```

## Reference
