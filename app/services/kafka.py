import asyncio
import logging
import json
from datetime import datetime
from random import choice

from aiokafka import AIOKafkaProducer
from aiokafka.producer.message_accumulator import BatchBuilder
from aiokafka.admin import AIOKafkaAdminClient, NewTopic

from core import settings

logger = logging.getLogger("uvicorn")


class KafkaProducer:
    def __init__(
        self,
        bootstrap_servers: str,
        topic: str,
    ):
        self.bootstrap_servers = bootstrap_servers
        self.producer = None
        self.admin = None
        self.topic = topic
        self.batch: BatchBuilder | None = None
        self.massage_queue = asyncio.Queue()

    async def start(self):
        self.producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers)
        self.admin = AIOKafkaAdminClient(bootstrap_servers=self.bootstrap_servers)
        await self.producer.start()
        metadata = await self.producer.client.fetch_all_metadata()
        if self.topic not in metadata.topics():
            await self._new_topic()
        self.batch = self.producer.create_batch()

    async def stop(self):
        await self.producer.stop()

    async def batch_sender(self):
        while True:
            try:
                msg = await asyncio.wait_for(self.massage_queue.get(), timeout=15)
                metadata = self.batch.append(key=None, value=msg, timestamp=None)
                if metadata is None:
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
    ):
        msg = {
            "action": crud_action,
            "date_time": date_time.strftime("%Y-%m-%d"),
        }
        if user_id:
            msg.update({"user_id": user_id})
        await self.massage_queue.put(json.dumps(msg).encode(encoding="utf-8"))

    async def _new_topic(self):
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
)
