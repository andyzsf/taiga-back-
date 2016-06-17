# -*- coding: utf-8 -*-
# Copyright (C) 2014-2016 Andrey Antukh <niwi@niwi.nz>
# Copyright (C) 2014-2016 Jesús Espino <jespinog@gmail.com>
# Copyright (C) 2014-2016 David Barragán <bameda@dbarragan.com>
# Copyright (C) 2014-2016 Alejandro Alonso <alejandro.alonso@kaleidos.net>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import serpy
import base64
import os
import copy
from collections import OrderedDict

from django.core.files.base import ContentFile
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.db import models
from django.contrib.postgres.fields import ArrayField

from taiga.base.api import serializers, ISO_8601
from taiga.base.api.settings import api_settings
from taiga.base.fields import JsonField, PgArrayField
from taiga.mdrender.service import render as mdrender
from taiga.users import models as users_models

from .cache import cached_get_user_by_email, cached_get_user_by_pk


class CommentFieldSerpy(serpy.Field):
    pass


class DateTimeFieldSerpy(serpy.Field):
    format = api_settings.DATETIME_FORMAT

    def to_value(self, value):
        if value is None or self.format is None:
            return value

        if self.format.lower() == ISO_8601:
            ret = value.isoformat()
            if ret.endswith("+00:00"):
                ret = ret[:-6] + "Z"
            return ret
        return value.strftime(self.format)


class JsonFieldSerpy(serpy.Field):
    def to_value(self, data):
        return JsonField().to_native(data)


class PgArrayFieldSerpy(serpy.Field):
    def to_value(self, data):
        return PgArrayField().to_native(data)


class NestedArraySerpy(serpy.Field):
    def to_value(self, data):
        print(ArrayField(ArrayField(models.TextField(), size=2)).to_python(data))
        return ArrayField(ArrayField(models.TextField(), size=2)).to_python(data)


class TimelineDataFieldSerpy(serpy.Field):
    def to_value(self, data):
        new_data = copy.deepcopy(data)
        try:
            user = cached_get_user_by_pk(new_data["user"]["id"])
            new_data["user"]["email"] = user.email
            del new_data["user"]["id"]
        except Exception:
            pass
        return new_data


class FileFieldSerpy(serpy.Field):
    def to_value(self, obj):
        if not obj:
            return None

        data = base64.b64encode(obj.read()).decode('utf-8')

        return OrderedDict([
            ("data", data),
            ("name", os.path.basename(obj.name)),
        ])


class UserRelatedFieldSerpy(serpy.Field):
    def to_value(self, obj):
        if obj:
            return obj.email
        return None


class UserPkFieldSerpy(serpy.Field):
    def to_value(self, obj):
        try:
            user = cached_get_user_by_pk(obj)
            return user.email
        except users_models.User.DoesNotExist:
            return None


class ProjectRelatedFieldSerpy(serpy.Field):
    def __init__(self, slug_field, *args, **kwargs):
        self.slug_field = slug_field
        super().__init__(*args, **kwargs)

    def to_value(self, obj):
        if obj:
            return getattr(obj, self.slug_field)
        return None


class HistoryUserFieldSerpy(serpy.Field):
    def to_value(self, obj):
        if obj is None or obj == {}:
            return []
        try:
            user = cached_get_user_by_pk(obj['pk'])
        except users_models.User.DoesNotExist:
            user = None
        return (UserRelatedFieldSerpy().to_value(user), obj['name'])


class HistoryValuesFieldSerpy(serpy.Field):
    def to_value(self, obj):
        if obj is None:
            return []
        if "users" in obj:
            obj['users'] = list(map(UserPkFieldSerpy().to_value, obj['users']))
        return obj


class HistoryDiffFieldSerpy(serpy.Field):
    def to_value(self, obj):
        if obj is None:
            return []

        if "assigned_to" in obj:
            obj['assigned_to'] = list(map(UserPkFieldSerpy().to_value, obj['assigned_to']))

        return obj
