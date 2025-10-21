import asyncio
import json
from datetime import datetime
from typing import Callable

import pytest
from aiokafka.errors import KafkaConnectionError, TopicAlreadyExistsError
from pytest_mock import MockerFixture
from services.kafka import KafkaProducer

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_start_starts_producer_and_sets_running(
    mocker: MockerFixture,
    test_producer: Callable[[bool], KafkaProducer],
) -> None:
    mock_producer = mocker.AsyncMock()
    mock_admin = mocker.AsyncMock()
    mocker.patch("services.kafka.AIOKafkaProducer", return_value=mock_producer)
    mocker.patch("services.kafka.AIOKafkaAdminClient", return_value=mock_admin)
    mock_producer.client = mocker.AsyncMock()
    metadata_mock = mocker.MagicMock()
    metadata_mock.topics.return_value = {"existing-topic"}
    mock_producer.client.fetch_all_metadata.return_value = metadata_mock

    producer = test_producer(True)
    await producer.start()

    assert producer._running is True
    mock_producer.start.assert_awaited_once()


@pytest.mark.asyncio
async def test_start_handles_connection_error(
    mocker: MockerFixture,
    test_producer: Callable[[bool], KafkaProducer],
) -> None:
    mock_producer = mocker.AsyncMock()
    mock_admin = mocker.AsyncMock()
    mock_producer.start.side_effect = [KafkaConnectionError("fail"), None]
    mocker.patch("services.kafka.AIOKafkaProducer", return_value=mock_producer)
    mocker.patch("services.kafka.AIOKafkaAdminClient", return_value=mock_admin)
    sleep_mock = mocker.patch(
        "services.kafka.asyncio.sleep", new_callable=mocker.AsyncMock
    )
    mock_producer.client = mocker.AsyncMock()
    metadata_mock = mocker.MagicMock()
    metadata_mock.topics.return_value = {"existing-topic"}
    mock_producer.client.fetch_all_metadata.return_value = metadata_mock

    producer = test_producer(True)
    await producer.start()

    assert mock_producer.start.call_count == 2
    sleep_mock.assert_awaited_with(3)


@pytest.mark.asyncio
async def test_stop_flushes_and_stops_producer(
    mocker: MockerFixture,
    test_producer: Callable[[bool], KafkaProducer],
) -> None:
    mock_producer = mocker.AsyncMock()
    mocker.patch("services.kafka.AIOKafkaProducer", return_value=mock_producer)
    mock_admin = mocker.AsyncMock()
    mocker.patch("services.kafka.AIOKafkaAdminClient", return_value=mock_admin)
    mock_producer.client = mocker.AsyncMock()
    metadata_mock = mocker.MagicMock()
    metadata_mock.topics.return_value = {"existing-topic"}
    mock_producer.client.fetch_all_metadata.return_value = metadata_mock

    producer = test_producer(True)
    await producer.start()
    await producer.stop()

    mock_producer.flush.assert_awaited_once()
    mock_producer.stop.assert_awaited_once()
    assert producer._running is False


@pytest.mark.asyncio
async def test_k_logger_puts_message_to_queue(
    mocker: MockerFixture,
    test_producer: Callable[[bool], KafkaProducer],
) -> None:
    producer = test_producer(True)
    msg_put = mocker.spy(producer.message_queue, "put")

    await producer.k_logger("CREATE", datetime(2025, 10, 18, 12, 0), user_id=123)

    msg_put.assert_called_once()
    msg = json.loads(msg_put.call_args[0][0].decode())
    assert msg["action"] == "CREATE"
    assert msg["user_id"] == "123"


@pytest.mark.asyncio
async def test_k_logger_does_nothing_if_disabled(
    mocker: MockerFixture,
    test_producer: Callable[[bool], KafkaProducer],
) -> None:
    producer = test_producer(False)
    put_spy = mocker.spy(producer.message_queue, "put")

    await producer.k_logger("CREATE", datetime.now(), user_id=1)
    put_spy.assert_not_called()


@pytest.mark.asyncio
async def test_batch_sender_sends_message(
    mocker: MockerFixture,
    test_producer: Callable[[bool], KafkaProducer],
) -> None:
    mock_producer = mocker.AsyncMock()
    mocker.patch("services.kafka.AIOKafkaProducer", return_value=mock_producer)
    producer = test_producer(True)
    producer.producer = mock_producer
    producer._running = True
    await producer.message_queue.put(b"test-message")

    async def stop_after() -> None:
        await asyncio.sleep(0.1)
        producer._running = False

    asyncio.create_task(stop_after())
    await producer._batch_sender()

    mock_producer.send.assert_awaited_with("test-topic", b"test-message")


@pytest.mark.asyncio
async def test_new_topic_creates_topic_if_not_exists(
    mocker: MockerFixture,
    test_producer: Callable[[bool], KafkaProducer],
) -> None:
    mock_admin = mocker.AsyncMock()
    mocker.patch("services.kafka.AIOKafkaAdminClient", return_value=mock_admin)
    producer = test_producer(True)
    producer.admin = mock_admin

    await producer._new_topic()

    mock_admin.start.assert_awaited_once()
    mock_admin.create_topics.assert_awaited_once()
    mock_admin.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_new_topic_handles_already_exists(
    mocker: MockerFixture,
    test_producer: Callable[[bool], KafkaProducer],
) -> None:
    mock_admin = mocker.AsyncMock()
    mock_admin.create_topics.side_effect = TopicAlreadyExistsError("exists")
    mocker.patch("services.kafka.AIOKafkaAdminClient", return_value=mock_admin)
    producer = test_producer(True)
    producer.admin = mock_admin

    await producer._new_topic()

    mock_admin.close.assert_awaited_once()
