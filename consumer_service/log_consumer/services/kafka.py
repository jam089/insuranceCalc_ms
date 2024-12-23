import logging
import asyncio
import json

from aiokafka import AIOKafkaConsumer, TopicPartition
from aiokafka.errors import KafkaConnectionError, KafkaError

from log_consumer.crud import logs as logs_crud
from log_consumer.db.db_helper import db_helper
from log_consumer.core import settings

logger = logging.getLogger("uvicorn")


class KafkaConsumer:
    def __init__(
        self,
        bootstrap_servers: str,
        topics: list[str],
        max_records: int,
        fetch_min_bytes: int,
    ):
        self.bootstrap_servers = bootstrap_servers
        self.topics = topics
        self.max_records = max_records
        self.fetch_min_bytes = fetch_min_bytes
        self.consumer: AIOKafkaConsumer | None = None
        self.topics_partitions_list = []

    async def start(self):
        self.consumer = AIOKafkaConsumer(
            *self.topics,
            bootstrap_servers=self.bootstrap_servers,
            fetch_min_bytes=self.fetch_min_bytes,
        )
        for counter in range(0, 10):
            try:
                await self.consumer.start()
                asyncio.create_task(self.get_batches())
                for topic in self.topics:
                    partitions = self.consumer.partitions_for_topic(topic)
                    self.topics_partitions_list.extend(
                        [
                            TopicPartition(topic=topic, partition=partition)
                            for partition in partitions
                        ]
                    )
                break
            except KafkaConnectionError as ex:
                await self.stop()
                logger.error(f"{counter}: {ex.args}")
                await asyncio.sleep(delay=3)

    async def stop(self):
        await self.consumer.stop()

    async def get_batches(self):
        try:
            while True:
                messages = await self.consumer.getmany(
                    *self.topics_partitions_list,
                    max_records=self.max_records,
                    timeout_ms=20000,
                )

                for index, (topic, batch) in enumerate(messages.items()):
                    batch_load_status = await logs_crud.bulk_load_logs(
                        db_sess=db_helper.session_factory(),
                        logs=[
                            json.loads(consumer_record.value)
                            for consumer_record in batch
                        ],
                    )
                    logger.debug(f"butch {index}status: {batch_load_status}")

        except KafkaError as ex:
            await self.stop()
            logger.error(f"KafkaError: {ex}")


consumer = KafkaConsumer(
    bootstrap_servers=settings.kafka.bootstrap_servers,
    topics=settings.kafka.topics,
    max_records=settings.kafka.max_records,
    fetch_min_bytes=settings.kafka.fetch_min_bytes,
)
