## Question 3

In Lab 3, the inference container had to use `host.docker.internal` because MLflow was running on the host machine outside Docker.

In Lab 4, Docker Compose creates a private network for all services in the Compose project.

Each service can be reached by its service name through Docker's internal DNS. Therefore, the inference service can reach MLflow using:

`http://mlflow:5000`

The hostname `mlflow` resolves because it is the Compose service name.

## Question 4

The frontend reads `INFERENCE_URL` from an environment variable so that the same frontend image can be used in different environments.

Inside Docker Compose, the value can be set to:

`http://inference:8000`

because `inference` is the service name on the Compose network.

If the frontend container is run on its own outside Compose, it can instead use another URL such as:

`http://127.0.0.1:8000`

This avoids hardcoding the frontend to one deployment environment.

## Question 5

Only MLflow and the frontend publish ports to the host because those are the services a user needs to access directly.

The inference service does not need a published host port because the frontend communicates with it inside the private Docker Compose network using:

`http://inference:8000`

Docker's internal DNS resolves `inference` to the inference container, so service-to-service communication does not require exposing port 8000 to the host.

## Question 6

`depends_on` only controls the order in which Docker Compose starts containers. It does not guarantee that the MLflow tracking server is fully ready to accept requests.

If the inference service starts and immediately tries to load its model before MLflow is ready, model loading can fail and the inference container may exit.

The failure can be inspected using:

`docker compose logs inference`

A more robust production setup would use health checks, retries, or startup logic that waits until MLflow is actually available.

## Question 7

Running `docker compose ps` showed:

- `mlflow` publishes port `5001` on the host to port `5000` in the container.
- `frontend` publishes port `8501` on the host.
- `inference` does not publish a host port; it only exposes port `8000` inside the Compose network.

This matches the `docker-compose.yml` configuration. The frontend can still reach the inference service using the internal service hostname:

`http://inference:8000`


## Question 8

Changing the registered model version or moving the `champion` alias does not immediately change predictions from the running inference service.

The reason is that `serve.py` loads the model once when the inference container starts. The model then stays in memory.

To pick up the newly promoted model version without rebuilding any Docker image, I can run:

```bash
docker compose restart inference
``` 

## Question 9

`docker compose restart inference` works without rebuilding because the inference image already contains the serving code and dependencies.

The actual model is not baked into the image. It is resolved and loaded from MLflow at container startup.

Therefore, restarting the container is enough to fetch the model currently referenced by the `champion` alias.

## Question 10

After running:

```bash
docker compose down
docker compose up
```
