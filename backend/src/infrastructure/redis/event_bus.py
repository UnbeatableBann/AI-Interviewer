import asyncio
import json
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Dict, List, Optional
from redis.asyncio import Redis

from src.core.events import BaseEvent, deserialize_event
from src.core.observability.logging import get_logger

logger = get_logger("src.infrastructure.redis.event_bus")


class RedisEventBus:
    """Production-grade Redis Streams-backed Event Bus with Consumer Groups, Retries, and DLQ."""

    def __init__(
        self,
        redis_client: Redis,
        stream_name: str = "platform_events",
        dlq_stream_name: str = "platform_events:dlq",
    ) -> None:
        self.client = redis_client
        self.stream_name = stream_name
        self.dlq_stream_name = dlq_stream_name
        self.handlers: Dict[str, List[Callable[[BaseEvent], Awaitable[None]]]] = {}
        self.is_running = False

    def register_handler(
        self, event_type: str, handler: Callable[[BaseEvent], Awaitable[None]]
    ) -> None:
        """Registers a consumer callback handler for a specific event type."""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
        logger.info(
            "Registered event handler", event_type=event_type, handler=handler.__name__
        )

    async def publish(self, event: BaseEvent) -> str:
        """Publishes an event to the Redis Stream, returns the generated message ID."""
        payload_str = event.model_dump_json()
        fields = {
            "event_type": event.event_type,
            "payload": payload_str,
            "tenant_id": event.tenant_id,
        }
        # Add message to the stream
        msg_id: str = await self.client.xadd(self.stream_name, fields)
        logger.info(
            "Published event to stream",
            event_type=event.event_type,
            msg_id=msg_id,
            tenant_id=event.tenant_id,
        )
        return msg_id

    async def create_consumer_group(self, group_name: str) -> None:
        """Creates a consumer group. Gracefully handles if group already exists."""
        try:
            # ID "0" reads from the beginning of the stream.
            # mkstream=True automatically creates the stream if it does not exist yet.
            await self.client.xgroup_create(
                self.stream_name, group_name, id="0", mkstream=True
            )
            logger.info(
                "Created consumer group successfully",
                group_name=group_name,
                stream_name=self.stream_name,
            )
        except Exception as e:
            if "BUSYGROUP" in str(e):
                logger.debug("Consumer group already exists", group_name=group_name)
            else:
                logger.error(
                    "Error creating consumer group",
                    error=str(e),
                    group_name=group_name,
                )
                raise e

    async def process_message(
        self,
        group_name: str,
        message_id: str,
        fields: Dict[str, Any],
        max_retries: int = 3,
    ) -> None:
        """Deserializes event, runs registered handlers, and manages acknowledgement/DLQ fallback."""
        event_type = fields.get("event_type")
        payload_str = fields.get("payload")
        tenant_id = fields.get("tenant_id")

        if not event_type or not payload_str:
            logger.warning(
                "Malformed stream message: missing event_type or payload. Acknowledging to clear.",
                msg_id=message_id,
            )
            await self.client.xack(self.stream_name, group_name, message_id)
            return

        try:
            payload = json.loads(payload_str)
            event = deserialize_event(event_type, payload)
        except Exception as e:
            logger.error(
                "Deserialization failed for event. Moving to DLQ.",
                error=str(e),
                msg_id=message_id,
            )
            await self.send_to_dlq(
                message_id,
                event_type,
                payload_str,
                tenant_id,
                f"Deserialization failed: {e}",
            )
            await self.client.xack(self.stream_name, group_name, message_id)
            return

        handlers = self.handlers.get(event_type, [])
        if not handlers:
            # If no consumer registered for this event, acknowledge it so it doesn't stay pending
            await self.client.xack(self.stream_name, group_name, message_id)
            return

        success = True
        error_msg = ""
        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                success = False
                error_msg = f"Handler '{handler.__name__}' failed: {e}"
                logger.error(
                    "Error executing event handler",
                    error=str(e),
                    event_type=event_type,
                    msg_id=message_id,
                )
                break

        if success:
            await self.client.xack(self.stream_name, group_name, message_id)
        else:
            # Query the pending list to find delivery attempts
            try:
                pending_info = await self.client.xpending_range(
                    self.stream_name,
                    group_name,
                    minval=message_id,
                    maxval=message_id,
                    count=1,
                )
                times_delivered = (
                    pending_info[0].get("times_delivered", 1) if pending_info else 1
                )
            except Exception:
                times_delivered = 1

            if times_delivered >= max_retries:
                logger.warning(
                    "Exceeded maximum delivery attempts. Moving to DLQ.",
                    msg_id=message_id,
                    event_type=event_type,
                    times_delivered=times_delivered,
                )
                await self.send_to_dlq(
                    message_id,
                    event_type,
                    payload_str,
                    tenant_id,
                    f"Max retries exceeded. Last error: {error_msg}",
                )
                # Acknowledge to clear from original stream's PEL
                await self.client.xack(self.stream_name, group_name, message_id)

    async def process_pending_messages(
        self, group_name: str, consumer_name: str, max_retries: int = 3
    ) -> None:
        """Processes any pending messages assigned to this consumer in the PEL."""
        try:
            # Reading with ID "0" returns all pending messages in group PEL for this consumer
            response = await self.client.xreadgroup(
                groupname=group_name,
                consumername=consumer_name,
                streams={self.stream_name: "0"},
                count=50,
                block=10,
            )
            if response:
                for _, messages in response:
                    for msg_id, fields in messages:
                        await self.process_message(
                            group_name, msg_id, fields, max_retries
                        )
        except Exception as e:
            logger.error("Failed to process pending messages on startup", error=str(e))

    async def claim_and_retry_idle_messages(
        self,
        group_name: str,
        consumer_name: str,
        min_idle_time_sec: float = 10.0,
        max_retries: int = 3,
    ) -> None:
        """Claims messages pending for other consumers that have timed out (idle) and retries/DLQs them."""
        try:
            # Query details of up to 50 pending messages in the group
            pending_list = await self.client.xpending_range(
                self.stream_name, group_name, minval="-", maxval="+", count=50
            )
            min_idle_time_ms = int(min_idle_time_sec * 1000)

            for pending in pending_list:
                msg_id = pending["message_id"]
                owner = pending["consumer"]
                idle_time_ms = pending["time_since_delivered"]
                times_delivered = pending["times_delivered"]

                if idle_time_ms >= min_idle_time_ms:
                    if times_delivered >= max_retries:
                        logger.warning(
                            "Idle pending message exceeded retries. Claiming to send to DLQ.",
                            msg_id=msg_id,
                            owner=owner,
                            times_delivered=times_delivered,
                        )
                        claimed = await self.client.xclaim(
                            self.stream_name,
                            group_name,
                            consumer_name,
                            min_idle_time=min_idle_time_ms,
                            message_ids=[msg_id],
                        )
                        if claimed:
                            for c_msg_id, fields in claimed:
                                event_type = fields.get("event_type", "Unknown")
                                payload_str = fields.get("payload", "{}")
                                tenant_id = fields.get("tenant_id")
                                await self.send_to_dlq(
                                    c_msg_id,
                                    event_type,
                                    payload_str,
                                    tenant_id,
                                    f"Claimed from idle owner '{owner}' after exceeding retry limit.",
                                )
                                await self.client.xack(
                                    self.stream_name, group_name, c_msg_id
                                )
                    else:
                        logger.info(
                            "Claiming idle message for reprocessing",
                            msg_id=msg_id,
                            owner=owner,
                            idle_time_sec=idle_time_ms / 1000.0,
                        )
                        claimed = await self.client.xclaim(
                            self.stream_name,
                            group_name,
                            consumer_name,
                            min_idle_time=min_idle_time_ms,
                            message_ids=[msg_id],
                        )
                        if claimed:
                            for c_msg_id, fields in claimed:
                                await self.process_message(
                                    group_name, c_msg_id, fields, max_retries
                                )
        except Exception as e:
            logger.error("Failed claiming/retrying idle pending messages", error=str(e))

    async def send_to_dlq(
        self,
        original_msg_id: str,
        event_type: str,
        payload_str: str,
        tenant_id: Optional[str],
        error_message: str,
    ) -> str:
        """Pushes a failed message description to the Dead Letter Queue stream."""
        fields = {
            "original_msg_id": original_msg_id,
            "event_type": event_type,
            "payload": payload_str,
            "tenant_id": tenant_id or "unknown",
            "error": error_message,
            "failed_at": datetime.now(timezone.utc).isoformat(),
        }
        try:
            dlq_msg_id: str = await self.client.xadd(self.dlq_stream_name, fields)
            logger.info(
                "Moved failed event to DLQ",
                original_msg_id=original_msg_id,
                dlq_msg_id=dlq_msg_id,
            )
            return dlq_msg_id
        except Exception as e:
            logger.error(
                "CRITICAL: Failed to publish error payload to DLQ stream",
                error=str(e),
                original_msg_id=original_msg_id,
            )
            raise e

    async def start_consumer_loop(
        self,
        group_name: str,
        consumer_name: str,
        batch_size: int = 10,
        block_ms: int = 1000,
        max_retries: int = 3,
        poll_interval_sec: float = 1.0,
    ) -> None:
        """Starts a blocking read loop. Use cancel/stop_consumer to terminate."""
        await self.create_consumer_group(group_name)

        # 1. Process local consumer PEL records from previous runs
        await self.process_pending_messages(group_name, consumer_name, max_retries)

        self.is_running = True
        logger.info(
            "Event bus consumer loop started",
            group=group_name,
            consumer=consumer_name,
        )

        last_claim_check = datetime.now(timezone.utc)

        while self.is_running:
            try:
                # Read new messages (STREAMS platform_events >)
                response = await self.client.xreadgroup(
                    groupname=group_name,
                    consumername=consumer_name,
                    streams={self.stream_name: ">"},
                    count=batch_size,
                    block=block_ms,
                )
                if response:
                    for _, messages in response:
                        for msg_id, fields in messages:
                            await self.process_message(
                                group_name, msg_id, fields, max_retries
                            )

                # Periodically claim idle messages from crashed/stuck consumers (every 30s)
                now = datetime.now(timezone.utc)
                if (now - last_claim_check).total_seconds() >= 30:
                    await self.claim_and_retry_idle_messages(
                        group_name,
                        consumer_name,
                        min_idle_time_sec=10.0,
                        max_retries=max_retries,
                    )
                    last_claim_check = now

            except asyncio.CancelledError:
                self.is_running = False
                break
            except Exception as e:
                logger.error("Error encountered in consumer loop", error=str(e))
                await asyncio.sleep(poll_interval_sec)

    def stop_consumer(self) -> None:
        """Halts the running loop."""
        self.is_running = False
        logger.info("Signaled consumer loop to stop.")
