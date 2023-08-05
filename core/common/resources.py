from core.common.names import *
from core.event_holder import EventHolder

event_holder: Optional[EventHolder] = None

screen: Optional[Surface] = None

gallery = None
editor = None

sql_agent = None


def ws() -> Vector2:
    return Vector2(screen.get_size())


def ws_rect() -> FRect:
    return screen.get_frect()
