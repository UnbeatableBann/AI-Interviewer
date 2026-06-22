import json
import pytest
from unittest.mock import AsyncMock, call
from datetime import datetime
from redis.exceptions import ResponseError

from src.core.events import (
    BaseEvent,
    InterviewStarted,
    QuestionGenerated,
    AnswerReceived,
    EvaluationCompleted,
    CandidateUpdated,
    AnalyticsUpdated,
    deserialize_event,
)
from src.infrastructure.redis.event_bus import RedisEventBus


def test_event_serialization_and_deserialization() -> None:
    """Verifies that events serialize to JSON and deserialize back to correct classes."""
    # 1. Test InterviewStarted
    event = InterviewStarted(
        tenant_id="tenant_123",
        interview_id="int_999",
        candidate_id="cand_888",
        interviewer_id="user_777",
    )
    assert event.event_type == "InterviewStarted"
    assert event.tenant_id == "tenant_123"
    assert event.interview_id == "int_999"
    assert event.candidate_id == "cand_888"
    assert event.interviewer_id == "user_777"
    assert event.event_id is not None
    assert isinstance(event.timestamp, datetime)

    dumped = event.model_dump_json()
    loaded_dict = json.loads(dumped)
    deserialized = deserialize_event("InterviewStarted", loaded_dict)
    assert isinstance(deserialized, InterviewStarted)
    assert deserialized.interview_id == "int_999"

    # 2. Test QuestionGenerated
    q_event = QuestionGenerated(
        tenant_id="tenant_123",
        interview_id="int_999",
        question_id="q_1",
        question_text="Explain Event-Driven Architecture.",
        category="system_design",
    )
    assert q_event.event_type == "QuestionGenerated"
    assert q_event.question_text == "Explain Event-Driven Architecture."

    # 3. Test AnswerReceived
    a_event = AnswerReceived(
        tenant_id="tenant_123",
        interview_id="int_999",
        question_id="q_1",
        answer_text="Redis Streams are logs.",
        confidence_level=0.9,
    )
    assert a_event.confidence_level == 0.9

    # 4. Test EvaluationCompleted
    e_event = EvaluationCompleted(
        tenant_id="tenant_123",
        evaluation_id="eval_1",
        interview_id="int_999",
        candidate_id="cand_888",
        scores={"Technical Accuracy": 4.5, "Communication": 4.0},
        overall_score=4.25,
        hallucinations_detected=0,
        faithfulness_ratio=1.0,
    )
    assert e_event.overall_score == 4.25

    # 5. Test CandidateUpdated
    c_event = CandidateUpdated(
        tenant_id="tenant_123",
        candidate_id="cand_888",
        profile_changes={"skills": ["Python", "Redis"]},
    )
    assert c_event.profile_changes["skills"] == ["Python", "Redis"]

    # 6. Test AnalyticsUpdated
    an_event = AnalyticsUpdated(
        tenant_id="tenant_123",
        metric_name="candidate_hired_rate",
        value=0.85,
        metadata={"region": "US"},
    )
    assert an_event.metric_name == "candidate_hired_rate"


@pytest.mark.asyncio
async def test_event_bus_publish() -> None:
    """Verifies that publishing an event calls xadd with correct serialization."""
    mock_redis = AsyncMock()
    mock_redis.xadd.return_value = "1626912345678-0"

    event_bus = RedisEventBus(mock_redis)

    event = InterviewStarted(
        tenant_id="tenant_abc",
        interview_id="int_1",
        candidate_id="cand_2",
        interviewer_id="user_3",
    )

    msg_id = await event_bus.publish(event)
    assert msg_id == "1626912345678-0"

    # Verify xadd parameters
    mock_redis.xadd.assert_called_once()
    args, kwargs = mock_redis.xadd.call_args
    assert args[0] == "platform_events"
    fields = args[1]
    assert fields["event_type"] == "InterviewStarted"
    assert fields["tenant_id"] == "tenant_abc"
    payload = json.loads(fields["payload"])
    assert payload["interview_id"] == "int_1"


@pytest.mark.asyncio
async def test_create_consumer_group() -> None:
    """Verifies group creation handles success and already existing groups correctly."""
    mock_redis = AsyncMock()
    event_bus = RedisEventBus(mock_redis)

    # 1. Group creation success
    await event_bus.create_consumer_group("group_new")
    mock_redis.xgroup_create.assert_called_once_with(
        "platform_events", "group_new", id="0", mkstream=True
    )

    # 2. Group already exists (should log and bypass ResponseError BusyGroup)
    mock_redis.xgroup_create.side_effect = ResponseError(
        "BUSYGROUP Consumer Group name already exists"
    )
    # This call should complete without raising an error
    await event_bus.create_consumer_group("group_exists")


@pytest.mark.asyncio
async def test_process_message_success() -> None:
    """Verifies processing a valid event executes registered handlers and acknowledges it."""
    mock_redis = AsyncMock()
    event_bus = RedisEventBus(mock_redis)

    # Setup handler
    handler_called = False
    received_event = None

    async def my_handler(event: BaseEvent) -> None:
        nonlocal handler_called, received_event
        handler_called = True
        received_event = event

    event_bus.register_handler("InterviewStarted", my_handler)

    # Simulated Redis message payload
    event = InterviewStarted(
        tenant_id="tenant_abc",
        interview_id="int_1",
        candidate_id="cand_2",
        interviewer_id="user_3",
    )
    fields = {
        "event_type": "InterviewStarted",
        "payload": event.model_dump_json(),
        "tenant_id": "tenant_abc",
    }

    await event_bus.process_message("my_group", "1-0", fields)

    assert handler_called is True
    assert isinstance(received_event, InterviewStarted)
    assert received_event.interview_id == "int_1"

    # Verified message acknowledged
    mock_redis.xack.assert_called_once_with("platform_events", "my_group", "1-0")


@pytest.mark.asyncio
async def test_process_message_malformed_and_deserialization_failures() -> None:
    """Verifies malformed or bad messages are cleared/DLQ'd and acknowledged."""
    mock_redis = AsyncMock()
    event_bus = RedisEventBus(mock_redis)

    # 1. Malformed fields
    await event_bus.process_message("my_group", "1-0", {})
    mock_redis.xack.assert_called_once_with("platform_events", "my_group", "1-0")
    mock_redis.xack.reset_mock()

    # 2. Deserialization error
    bad_fields = {
        "event_type": "InterviewStarted",
        "payload": "invalid-json-payload",
        "tenant_id": "tenant_abc",
    }
    await event_bus.process_message("my_group", "2-0", bad_fields)
    # Should publish to DLQ and then XACK to remove from stream
    mock_redis.xadd.assert_called_once()
    assert mock_redis.xadd.call_args[0][0] == "platform_events:dlq"
    mock_redis.xack.assert_called_once_with("platform_events", "my_group", "2-0")


@pytest.mark.asyncio
async def test_process_message_handler_exception_and_dlq() -> None:
    """Verifies that handler exceptions increment delivery count and move to DLQ when max retries exceeded."""
    mock_redis = AsyncMock()
    event_bus = RedisEventBus(mock_redis)

    async def failing_handler(event: BaseEvent) -> None:
        raise ValueError("Handler breakdown!")

    event_bus.register_handler("InterviewStarted", failing_handler)

    event = InterviewStarted(
        tenant_id="tenant_abc",
        interview_id="int_1",
        candidate_id="cand_2",
        interviewer_id="user_3",
    )
    fields = {
        "event_type": "InterviewStarted",
        "payload": event.model_dump_json(),
        "tenant_id": "tenant_abc",
    }

    # 1. Handler fails, times_delivered is 1 (less than max_retries = 3).
    # Should NOT XACK and NOT send to DLQ.
    mock_redis.xpending_range.return_value = [{"times_delivered": 1}]
    await event_bus.process_message("my_group", "1-0", fields, max_retries=3)
    mock_redis.xack.assert_not_called()
    mock_redis.xadd.assert_not_called()

    # 2. Handler fails, times_delivered is 3 (equal to max_retries = 3).
    # Should send to DLQ and then XACK to clear from PEL.
    mock_redis.xpending_range.return_value = [{"times_delivered": 3}]
    await event_bus.process_message("my_group", "1-0", fields, max_retries=3)
    mock_redis.xadd.assert_called_once()
    assert mock_redis.xadd.call_args[0][0] == "platform_events:dlq"
    mock_redis.xack.assert_called_once_with("platform_events", "my_group", "1-0")


@pytest.mark.asyncio
async def test_claim_and_retry_idle_messages() -> None:
    """Verifies that idle pending messages are claimed, claimed messages under retry limits are reprocessed, and exhausted idle messages are DLQ'd."""
    mock_redis = AsyncMock()
    event_bus = RedisEventBus(mock_redis)

    # Mock pending list returned by XPENDING details
    # Item 1: idle 15s (>= 10s idle min), times_delivered = 1 (< 3 max retries) -> reprocess
    # Item 2: idle 20s (>= 10s idle min), times_delivered = 3 (>= 3 max retries) -> DLQ
    mock_redis.xpending_range.return_value = [
        {
            "message_id": "1-0",
            "consumer": "c_old",
            "time_since_delivered": 15000,
            "times_delivered": 1,
        },
        {
            "message_id": "2-0",
            "consumer": "c_old",
            "time_since_delivered": 20000,
            "times_delivered": 3,
        },
    ]

    # Setup claim mock
    event_1 = InterviewStarted(
        tenant_id="tenant_abc",
        interview_id="int_1",
        candidate_id="cand_2",
        interviewer_id="user_3",
    )
    claimed_1 = [
        (
            "1-0",
            {
                "event_type": "InterviewStarted",
                "payload": event_1.model_dump_json(),
                "tenant_id": "tenant_abc",
            },
        )
    ]

    claimed_2 = [
        (
            "2-0",
            {
                "event_type": "InterviewStarted",
                "payload": event_1.model_dump_json(),
                "tenant_id": "tenant_abc",
            },
        )
    ]

    # Mock XCLAIM behavior
    async def side_effect_xclaim(*args, **kwargs):
        msg_ids = kwargs.get("message_ids") or args[4]
        if "1-0" in msg_ids:
            return claimed_1
        if "2-0" in msg_ids:
            return claimed_2
        return []

    mock_redis.xclaim.side_effect = side_effect_xclaim

    # Setup handler
    handler_called = False

    async def success_handler(event: BaseEvent) -> None:
        nonlocal handler_called
        handler_called = True

    event_bus.register_handler("InterviewStarted", success_handler)

    await event_bus.claim_and_retry_idle_messages(
        "my_group", "c_new", min_idle_time_sec=10.0, max_retries=3
    )

    # Verify claim calls
    mock_redis.xclaim.assert_has_calls(
        [
            call(
                "platform_events",
                "my_group",
                "c_new",
                min_idle_time=10000,
                message_ids=["1-0"],
            ),
            call(
                "platform_events",
                "my_group",
                "c_new",
                min_idle_time=10000,
                message_ids=["2-0"],
            ),
        ],
        any_order=True,
    )

    # 1-0 was reprocessed successfully
    assert handler_called is True
    # Verify 1-0 was acknowledged after successful processing
    mock_redis.xack.assert_any_call("platform_events", "my_group", "1-0")

    # 2-0 was claimed and directly sent to DLQ
    dlq_calls = [
        c for c in mock_redis.xadd.call_args_list if c[0][0] == "platform_events:dlq"
    ]
    assert len(dlq_calls) == 1
    dlq_args = dlq_calls[0][0]
    dlq_fields = dlq_args[1]
    assert dlq_fields["original_msg_id"] == "2-0"
    assert dlq_fields["event_type"] == "InterviewStarted"
    assert dlq_fields["payload"] == event_1.model_dump_json()
    assert dlq_fields["tenant_id"] == "tenant_abc"
    assert (
        "Claimed from idle owner 'c_old' after exceeding retry limit."
        in dlq_fields["error"]
    )
    assert "failed_at" in dlq_fields

    # Verify 2-0 was acknowledged to clear from stream
    mock_redis.xack.assert_any_call("platform_events", "my_group", "2-0")
