"""
Routes package for Event Reminder System API
"""

from . import auth_routes
from . import contacts
from . import events
from . import subscriptions
from . import notifications
from . import dashboard

__all__ = [
    'auth_routes',
    'contacts',
    'events',
    'subscriptions',
    'notifications',
    'dashboard'
]
