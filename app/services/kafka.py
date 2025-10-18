import asyncio
import json
import logging
from datetime import datetime
from random import choice

from aiokafka import AIOKafkaProducer
from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from aiokafka.errors import KafkaConnectionError, TopicAlreadyExistsError
from aiokafka.producer.message_accumulator import BatchBuilder
from core import settings

logger = logging.getLogger("uvicorn.kafka")


class KafkaProducer:
    def __init__(
        self,
        bootstrap_servers: str,
        topic: str,
    ):
        self.bootstrap_servers = bootstrap_servers
        self.producer: AIOKafkaProducer | None = None
        self.admin: AIOKafkaAdminClient | None = None
        self.topic = topic
        self.batch: BatchBuilder | None = None
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.max_batch_size = settings.kafka_logger.max_batch_size
        self.linger_ms = settings.kafka_logger.linger_ms
        self._running = False
        self.enabled = settings.kafka_logger.enable

    async def start(self) -> None:
        if not self.enabled:
            return
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            max_batch_size=self.max_batch_size,
            linger_ms=self.linger_ms,
        )
        self.admin = AIOKafkaAdminClient(bootstrap_servers=self.bootstrap_servers)
        for counter in range(10):
            try:
                await self.producer.start()
                self._running = True
                asyncio.create_task(self._batch_sender(), name="kafka_log_worker")
                break
            except KafkaConnectionError as ex:
                logger.error(f"[Kafka] connection attempt {counter} failed: {ex}")
                await asyncio.sleep(3)

        await self._ensure_topic()
        logger.info("[Kafka] started")

    async def stop(self) -> None:
        if not self.enabled:
            return
        self._running = False
        if self.producer:
            await self.producer.flush()
            await self.producer.stop()
            logger.info("[Kafka] stoped")

    async def _batch_sender(self) -> None:
        if not self.producer:
            return
        while self._running:
            try:
                msg = await asyncio.wait_for(self.message_queue.get(), timeout=10)
                await self.producer.send(self.topic, msg)
                logger.debug(f"[Kafka] message sent: {msg}")
            except asyncio.TimeoutError:
                logger.debug("[Kafka] queue is empty (timeout)")

    async def _send_batch(self) -> None:
        if self.producer:
            partitions = await self.producer.partitions_for(self.topic)
            chosen_partition = choice(tuple(partitions))
            await self.producer.send_batch(
                self.batch,
                self.topic,
                partition=chosen_partition,
            )
            logger.info("[Kafka] batch sent")
            self.batch = self.producer.create_batch()

    async def _ensure_topic(self) -> None:
        if not self.enabled or not self.producer:
            return
        await self.producer.client.bootstrap()
        metadata = await self.producer.client.fetch_all_metadata()
        if self.topic not in metadata.topics():
            await self._new_topic()

    async def k_logger(
        self,
        crud_action: str,
        date_time: datetime,
        user_id: int | None = None,
    ) -> None:
        logger.debug("[Kafka] action was logged")
        if not self.enabled:
            logger.debug("[Kafka] enable setting is false")
            return
        msg = {
            "action": crud_action,
            "date_time": date_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        if user_id:
            msg["user_id"] = str(user_id)
        await self.message_queue.put(json.dumps(msg).encode(encoding="utf-8"))
        logger.debug("[Kafka] message in queue")

    async def _new_topic(self) -> None:
        if self.admin:
            try:
                await self.admin.start()

                new_topic = NewTopic(
                    name=self.topic,
                    num_partitions=3,
                    replication_factor=1,
                )

                await self.admin.create_topics([new_topic])
            except KeyError as ex:
                logger.error(f"[Kafka] {ex.args}")
            except TopicAlreadyExistsError:
                logger.error(f"[Kafka] Topic {self.topic} already exists")
            finally:
                await self.admin.close()


producer = KafkaProducer(
    bootstrap_servers=str(settings.kafka_logger.bootstrap_servers),
    topic=settings.kafka_logger.topic,
)
