from typing import Callable

import pytest
from core import settings
from pytest_mock import MockerFixture
from services.kafka import KafkaProducer


@pytest.fixture
def test_producer(mocker: MockerFixture) -> Callable[[bool], KafkaProducer]:
    def _producer(enabled: bool = True) -> KafkaProducer:
        mocker.patch.object(settings.kafka_logger, "enable", enabled)
        return KafkaProducer("kafka:9092", "test-topic")

    return _producer
