from unittest import TestCase

from src.classes.eventmanager import EventManager, EventTyp


class test_EventManager(TestCase):

    def setUp(self):
        self.event_manager = EventManager()
        self.received_data = ''

    def test_subscribe(self):
        def handler(data):
            pass  # Simulate an actual handler

        self.event_manager.subscribe(EventTyp.NEU_DATEN, handler)

        self.assertIn(EventTyp.NEU_DATEN, self.event_manager.events)
        [self.assertIsInstance(event_type, EventTyp) for event_type in self.event_manager.events.keys()]
        self.assertEqual(len(self.event_manager.events[EventTyp.NEU_DATEN]), 1)
        self.assertIs(self.event_manager.events[EventTyp.NEU_DATEN][0], handler)

    def test_subscribe_existing_event(self):
        def handler1(data):
            pass

        def handler2(data):
            pass

        self.event_manager.subscribe(EventTyp.NEU_DATEN, handler1)
        self.event_manager.subscribe(EventTyp.NEU_DATEN, handler2)

        self.assertIn(EventTyp.NEU_DATEN, self.event_manager.events)
        self.assertEqual(len(self.event_manager.events[EventTyp.NEU_DATEN]), 2)
        self.assertIn(handler1, self.event_manager.events[EventTyp.NEU_DATEN])
        self.assertIn(handler2, self.event_manager.events[EventTyp.NEU_DATEN])

    def test_unsubscribe(self):
        def handler(data):
            pass

        self.event_manager.subscribe(EventTyp.NEU_DATEN, handler)
        self.event_manager.unsubscribe(EventTyp.NEU_DATEN, handler)

        self.assertNotIn(EventTyp.NEU_DATEN, self.event_manager.events)

    def test_unsubscribe_nonexistent_event(self):
        # Test unsubscribing fuer ein nicht-existierenden event type
        def handler(data):
            pass

        self.event_manager.unsubscribe("nonexistent_event", handler)

        # No assertion needed, unsubscribing from a non-existent event should not raise errors

    def test_unsubscribe_not_subscribed_funktion(self):
        # Test unsubscribing von einem event mit einer Funktion die nicht subscribed war
        def handler1(data):
            pass

        def handler2(data):
            pass

        self.event_manager.subscribe(EventTyp.NEU_DATEN, handler1)
        self.event_manager.unsubscribe(EventTyp.NEU_DATEN, handler2)

        self.assertIn(EventTyp.NEU_DATEN, self.event_manager.events)
        self.assertEqual(len(self.event_manager.events[EventTyp.NEU_DATEN]), 1)
        self.assertIs(self.event_manager.events[EventTyp.NEU_DATEN][0], handler1)

    def test_benachrichtigen(self):
        # Test benachrichtigen handlers for an event
        def handler(data):
            self.received_data = data

        class Foo:
            def __init__(self):
                self.data = ''

            def handler(self, data):
                self.data = data

        obj = Foo()

        self.event_manager.subscribe(EventTyp.NEU_DATEN, handler)
        self.event_manager.subscribe(EventTyp.NEU_DATEN, obj.handler)

        test_data = "This is some test data"
        self.event_manager.benachrichtigen(EventTyp.NEU_DATEN, test_data)

        self.assertEqual(self.received_data, test_data)
        self.assertEqual(obj.data, test_data)

    def test_benachrichtigen_nonexistent_event(self):
        # Test notifying for a non-existent event type
        def handler(data):
            pass

        self.event_manager.subscribe(EventTyp.NEU_DATEN, handler)
        test_data = "This is some test data"
        self.event_manager.benachrichtigen("nonexistent_event", test_data)

        # No assertion needed, notifying for a non-existent event shouldn't raise errors

    def test_benachrichtigen_empty_handlers(self):
        # Test notifying with no handlers subscribed to the event
        test_data = "This is some test data"
        self.event_manager.benachrichtigen(EventTyp.NEU_DATEN, test_data)

        # No assertion needed, notifying with no handlers shouldn't raise errors
