### Prerequisites

1. Install the docker engine: https://docs.docker.com/engine/install/ubuntu/
2. Install docker-compose: https://docs.docker.com/compose/install/

### Run the application

All services are automatically started (and built if necessary) with the following command: 

`docker-compose up --build`

### Note

The Kubernetes Cluster is not included in the docker-compose services. To run a local single-node
kubernetes cluster on your machine that can be controlled by the services defined in this
application, you can install minikube: https://kubernetes.io/de/docs/tasks/tools/install-minikube/

Afterwards, start your local Kubernetes cluster with `minikube start` and start a new deployment with 
`kubectl create deployment kubernetes-bootcamp --image=gcr.io/google-samples/kubernetes-bootcamp:v1`

After the deployment was scaled, check the replica count locally with `kubectl get deployments`

#### Django example

The django backend `example_backend` has a request to scale kubernetes that is available
at `http://localhost:8000/api/demo/scale-kubernetes/`. But in order to get the request working,
the django backend must be run locally and not within the container, because the kubernetes sdk
won't find valid configuration otherwise. The configuration only exists on the local machine where
`minikube` is also running.

First, stop the instance started by docker-compose with `docker-compose stop django-web`

To install all dependencies run `pip install -r requirements.txt` from `docker/example_backend`

You also need to set all the environment variables that would normally be included by docker from
`.env.django.dev`. After that execute the django backend with:

Then start the django backend with `python manage.py runserver [::1]:8000`

#### Kafka example

To install all dependencies run `pip install -r requirements.txt` from `docker/kafka-consumer`

Then start the kafka client with `python kafka_consumer.py`
