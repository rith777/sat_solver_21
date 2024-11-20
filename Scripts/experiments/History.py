from datetime import datetime
from enum import Enum


class EventType(Enum):
    IMPLICATION = "IMPLICATION"
    DECISION = "DECISION"
    CONFLICT = "CONFLICT"


class Event:
    def __init__(self, event_type: EventType, count):
        self.event_type = event_type,
        self.count = count
        self.datetime = datetime.now()

    def to_dict(self):
        return {
            'event_type': self.event_type[0].value,
            'count': self.count,
            'datetime': self.datetime.isoformat()
        }


class HistoryManager:
    def __init__(self):
        self.history = set()

    def add(self, event: Event):
        self.history.add(event)

    def add_conflict(self, count):
        self.history.add(Event(EventType.CONFLICT, count))

    def add_implication(self, count):
        self.history.add(Event(EventType.IMPLICATION, count))

    def add_decision(self, count):
        self.history.add(Event(EventType.DECISION, count))
