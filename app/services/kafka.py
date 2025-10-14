import asyncio
import logging
import json
from datetime import datetime
from random import choice

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaConnectionError
from aiokafka.producer.message_accumulator import BatchBuilder
from aiokafka.admin import AIOKafkaAdminClient, NewTopic

from core import settings

logger = logging.getLogger("uvicorn")


class KafkaProducer:
    def __init__(
        self,
        bootstrap_servers: str,
        topic: str,
        max_batch_size: int = 16384,
        linger_ms: int = 0,
    ):
        self.bootstrap_servers = bootstrap_servers
        self.producer: AIOKafkaProducer | None = None
        self.admin: AIOKafkaAdminClient | None = None
        self.topic = topic
        self.batch: BatchBuilder | None = None
        self.massage_queue: asyncio.Queue = asyncio.Queue()
        self.max_batch_size = max_batch_size
        self.linger_ms = linger_ms

    async def start(self) -> None:
        if settings.kafka_logger.enable:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                max_batch_size=self.max_batch_size,
                linger_ms=self.linger_ms,
            )
            self.admin = AIOKafkaAdminClient(bootstrap_servers=self.bootstrap_servers)
            for counter in range(0, 10):
                try:
                    await self.producer.start()
                    asyncio.create_task(self.batch_sender())
                    break
                except KafkaConnectionError as ex:
                    await self.stop()
                    logger.error(f"{counter}: {ex.args}")
                    await asyncio.sleep(delay=3)
            metadata = await self.producer.client.fetch_all_metadata()
            if self.topic not in metadata.topics():
                await self._new_topic()
            self.batch = self.producer.create_batch()

    async def stop(self) -> None:
        if settings.kafka_logger.enable and self.producer:
            await self.producer.stop()

    async def batch_sender(self) -> None:
        while True:
            try:
                msg = await asyncio.wait_for(self.massage_queue.get(), timeout=15)

                metadata = (
                    self.batch.append(key=None, value=msg, timestamp=None)
                    if self.batch
                    else None
                )
                if metadata is None and self.producer:
                    partitions = await self.producer.partitions_for(self.topic)
                    chosen_partition = choice(tuple(partitions))
                    await self.producer.send_batch(
                        self.batch,
                        self.topic,
                        partition=chosen_partition,
                    )
                    self.batch = self.producer.create_batch()
            except TimeoutError:
                logger.debug("message queue for kafka logging is empty")

    async def k_logger(
        self,
        crud_action: str,
        date_time: datetime,
        user_id: int | None = None,
    ) -> None:
        if settings.kafka_logger.enable:
            msg = {
                "action": crud_action,
                "date_time": date_time.strftime("%Y-%m-%d"),
            }
            if user_id:
                msg.update(user_id=str(user_id))
            await self.massage_queue.put(json.dumps(msg).encode(encoding="utf-8"))

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
                logger.error(ex.args)
            finally:
                await self.admin.close()


producer = KafkaProducer(
    bootstrap_servers=str(settings.kafka_logger.bootstrap_servers),
    topic=settings.kafka_logger.topic,
    max_batch_size=settings.kafka_logger.max_batch_size,
    linger_ms=settings.kafka_logger.linger_ms,
)
