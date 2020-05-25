from time import time
from uuid import UUID, uuid4
from typing import (
    Any,
    Dict,
    List,
    Tuple,
    Callable,
    NamedTuple
)

class LogicError(Exception):
    """
    An error in logic has been made
    """

StrDict = Dict[str, Any]

class Entity(NamedTuple):
    uuid: UUID
    data: StrDict

    def __repr__(self):
        return f"Entity({self.uuid})"

class EntityFactory(object):
    _entity: Entity
    def __init__(self) -> None:
        pass

    def create(
        self,
        entity_cls: Any,
        data: StrDict
    ) -> Entity:
        return entity_cls(uuid4(), data)

class Event(NamedTuple):
    kind: str
    data: StrDict
    entity: Entity
    created: float

    def __repr__(self):
        kind = self.kind
        data = self.data
        args = ", ".join([kind, repr(data)])
        return f"Event({args})"

EventHandler = Callable[[Event], None]
EventHandlers = List[EventHandler]

class Store(object):
    _events: List[Event]
    def __init__(self) -> None:
        self._events = list()

    @property
    def events(self):
        return self._events

    def save(self, event: Event) -> None:
        self._events.append(event)

    def apply(
        self,
        event: Event,
        *handlers: EventHandler
    ) -> None:
        for handler in handlers:
            handler(event)

    def replay(
        self,
        *handlers: EventHandler
    ) -> None:
        for event in self._events:
            self.apply(event, *handlers)

class Bus(object):
    _store: Store
    _subscribers: Dict[str, EventHandlers]
    def __init__(self, store: Store) -> None:
        self._store = store
        self._subscribers = dict()

    def subscribe(
        self,
        kind: str,
        *callbacks: EventHandler
    ) -> None:
        subs = self._subscribers.get(kind)
        if subs is None:
            self._subscribers[kind] = list()
            subs = self._subscribers[kind]

        for callback in callbacks:
            subs.append(callback)

    def unsubscribe(
        self,
        kind: str,
        *callbacks: EventHandler
    ) -> None:
        subs = self._subscribers.get(kind)
        if subs is None:
            self._subscribers[kind] = list()
            subs = self._subscribers[kind]

        for callback in callbacks:
            try:
                subs.remove(callback)

            except ValueError as e:
                err = f"is no {callback}"
                raise LogicError(err)

    def dispatch(self, event: Event) -> None:
        self._store.save(event)
        self.react(event)

    def react(self, event: Event) -> None:
        kind = event.kind
        subs = self._subscribers.get(kind)
        if subs is None:
            return

        handlers = tuple(subs)
        self._store.apply(event, *handlers)

class Service(object):
    _bus: Bus
    _entities: Dict[str, Entity]
    def __init__(
        self,
        bus: Bus,
        *entities: Entity
    ) -> None:
        self._bus = bus
        self._entities = dict()

        for entity in entities:
            name = entity.__class__.__name__
            self._entities[name] = entity

    def announce(
        self,
        name: str,
        kind: str,
        data: StrDict
    ) -> None:
        entity = self._entities.get(name)
        if entity is None:
            raise LogicError(f"is no {name}")

        event = Event(
            kind,
            data,
            entity,
            time()
        )
        self._bus.dispatch(event)

class ServiceFactory(object):
    def __init__(self):
        pass

    def create(
        self,
        bus: Bus,
        service_cls: Any
    ) -> Callable[..., Service]:
        def curry(*ents: Entity) -> Service:
            return service_cls(bus, *ents)

        return curry

# # # # #

class TestEntity(Entity):
    pass

e_factory = EntityFactory()
test_entity = e_factory.create(
    TestEntity,
    {"key": "value"}
)

store = Store()
bus = Bus(store)

class TestService(Service):
    entity: TestEntity

s_factory = ServiceFactory()
test_service_factory = s_factory.create(
    bus,
    TestService
)
test_service = test_service_factory(
    test_entity
)

handler = lambda e: print(f"EVENT:\n\t{e}")
bus.subscribe("CREATED", handler)
test_service.announce(
    "TestEntity",
    "CREATED",
    {"a": 1}
)
print(f"STORE:")
for event in store.events:
    print(f"\t{event}\n")

