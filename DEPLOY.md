# Deployment

This document describes how to deploy the EPV Research Platform to AWS ECS.

## Prerequisites

- Docker
- AWS CLI
- An AWS account

## Build and Push Docker Images

1.  **Build the images:**

    ```bash
    docker-compose build
    ```

2.  **Tag the images:**

    ```bash
    docker tag epv_research_platform_warptest_api:latest <your-aws-account-id>.dkr.ecr.<your-aws-region>.amazonaws.com/epv-api:latest
    docker tag epv_research_platform_warptest_web:latest <your-aws-account-id>.dkr.ecr.<your-aws-region>.amazonaws.com/epv-web:latest
    ```

3.  **Push the images to ECR:**

    ```bash
    aws ecr get-login-password --region <your-aws-region> | docker login --username AWS --password-stdin <your-aws-account-id>.dkr.ecr.<your-aws-region>.amazonaws.com
    docker push <your-aws-account-id>.dkr.ecr.<your-aws-region>.amazonaws.com/epv-api:latest
    docker push <your-aws-account-id>.dkr.ecr.<your-aws-region>.amazonaws.com/epv-web:latest
    ```

## Deploy to AWS ECS

1.  **Create an ECS cluster:**

    ```bash
    aws ecs create-cluster --cluster-name epv-cluster
    ```

2.  **Create a task definition:**

    Create a `task-definition.json` file with the following content:

    ```json
    {
        "family": "epv-task",
        "containerDefinitions": [
            {
                "name": "epv-api",
                "image": "<your-aws-account-id>.dkr.ecr.<your-aws-region>.amazonaws.com/epv-api:latest",
                "cpu": 256,
                "memory": 512,
                "portMappings": [
                    {
                        "containerPort": 8000,
                        "hostPort": 8000
                    }
                ]
            },
            {
                "name": "epv-web",
                "image": "<your-aws-account-id>.dkr.ecr.<your-aws-region>.amazonaws.com/epv-web:latest",
                "cpu": 256,
                "memory": 512,
                "portMappings": [
                    {
                        "containerPort": 80,
                        "hostPort": 80
                    }
                ]
            }
        ]
    }
    ```

    Register the task definition:

    ```bash
    aws ecs register-task-definition --cli-input-json file://task-definition.json
    ```

3.  **Create a service:**

    ```bash
    aws ecs create-service --cluster epv-cluster --service-name epv-service --task-definition epv-task --desired-count 1
    ```
