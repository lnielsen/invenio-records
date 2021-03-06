# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Test Invenio Records."""

from __future__ import absolute_import, print_function

import uuid

from flask_principal import UserNeed
from invenio_access import InvenioAccess
from invenio_access.models import ActionUsers
from invenio_accounts.models import User
from invenio_db import db

from invenio_records import Record
from invenio_records.permissions import permission_factory, records_read_all


class FakeIdentity(object):
    """Fake class to test DynamicPermission."""

    def __init__(self, *provides):
        """Initialize fake identity."""
        self.provides = provides


def test_permission_factory(app):
    """Test revisions."""
    InvenioAccess(app)
    with app.app_context():
        rec_uuid = uuid.uuid4()

        with db.session.begin_nested():
            user_all = User(email='all@invenio-software.org')
            user_one = User(email='one@invenio-software.org')
            user_none = User(email='none@invenio-software.org')
            db.session.add(user_all)
            db.session.add(user_one)
            db.session.add(user_none)

            db.session.add(ActionUsers(action=records_read_all.value,
                                       user=user_all, argument=None))
            db.session.add(ActionUsers(action=records_read_all.value,
                                       user=user_one, argument=str(rec_uuid)))

            record = Record.create({'title': 'permission test'}, id_=rec_uuid)

        # Create a record and assign permissions.
        permission = permission_factory(record)

        # Assert which permissions has access.
        assert permission.allows(FakeIdentity(UserNeed(user_all.id)))
        assert permission.allows(FakeIdentity(UserNeed(user_one.id)))
        assert not permission.allows(FakeIdentity(UserNeed(user_none.id)))
