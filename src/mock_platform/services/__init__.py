"""Service registration helpers."""

from mock_platform.services.admin import register_admin_tools
from mock_platform.services.contacts import register_contacts_tools
from mock_platform.services.memo import register_memo_tools
from mock_platform.services.messaging import register_messaging_tools

__all__ = [
    "register_admin_tools",
    "register_contacts_tools",
    "register_memo_tools",
    "register_messaging_tools",
]
