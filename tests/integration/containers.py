from pathlib import Path
from typing import Generator

import pytest
from testcontainers.compose import ComposeContainer, DockerCompose
from testcontainers.core.wait_strategies import LogMessageWaitStrategy

PROJECT_PATH = Path(__file__).parent.parent.parent


@pytest.fixture(scope="package")
def compose_containers() -> Generator[DockerCompose, None, None]:
    compose = DockerCompose(context=PROJECT_PATH, wait=False)
    compose.waiting_for(
        {
            "pg": LogMessageWaitStrategy(
                "database system is ready to accept connections"
            ),
            "insurance_calc_ms": LogMessageWaitStrategy("Application startup complete"),
        }
    )
    compose.start()
    yield compose
    compose.stop()


@pytest.fixture(scope="package")
def kafka_broker_container(compose_containers: DockerCompose) -> dict[str, str | int]:
    kafka_broker: ComposeContainer = compose_containers.get_container("kafka-broker")
    host = kafka_broker.get_container_host_ip()
    port = kafka_broker.get_exposed_port(port=9092)
    return {"host": host, "port": port}


@pytest.fixture(scope="package")
def pg_container(compose_containers: DockerCompose) -> dict[str, str | int]:
    pg: ComposeContainer = compose_containers.get_container("pg")
    envs: str = compose_containers.exec_in_container(
        command=["env"], service_name="pg"
    )[0]
    envs_dict = dict(
        line.split("=", 1) for line in envs.strip().splitlines() if "=" in line
    )
    user = envs_dict["INSURANCE__DB__LOGIN"]
    password = envs_dict["INSURANCE__DB__PASS"]
    db_name = envs_dict["INSURANCE__DB__DB_SCHEMA"]
    host = pg.get_container_host_ip()
    port = pg.get_exposed_port(port=5432)
    url = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}"

    return {"url": url, "host": host, "port": port}


@pytest.fixture(scope="package")
def app_container(compose_containers: DockerCompose) -> str:
    app: ComposeContainer = compose_containers.get_container("insurance_calc_ms")
    host = app.get_container_host_ip()
    port = app.get_exposed_port(port=8000)
    return f"http://{host}:{port}"
