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

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType

from taiga.base.api import serializers
from taiga.projects.history import models as history_models
from taiga.projects.attachments import models as attachments_models
from taiga.projects.notifications import services as notifications_services
from taiga.projects.history import services as history_service

from .serpy_fields import (UserRelatedFieldSerpy, HistoryUserFieldSerpy,
                           HistoryDiffFieldSerpy, JsonFieldSerpy,
                           HistoryValuesFieldSerpy, CommentFieldSerpy,
                           FileFieldSerpy, DateTimeFieldSerpy)


class HistoryExportSerializerSerpy(serpy.Serializer):
    user = HistoryUserFieldSerpy()
    diff = HistoryDiffFieldSerpy()
    snapshot = JsonFieldSerpy()
    values = HistoryValuesFieldSerpy()
    comment = CommentFieldSerpy()
    delete_comment_date = DateTimeFieldSerpy()
    delete_comment_user = HistoryUserFieldSerpy()
    created_at = DateTimeFieldSerpy()
    type = serpy.Field()
    comment_versions = JsonFieldSerpy()
    edit_comment_date = DateTimeFieldSerpy()
    is_hidden = serpy.Field()
    is_snapshot = serpy.Field()


class HistoryExportSerializerMixinSerpy(serpy.Serializer):
    history = serpy.MethodField("get_history")

    def get_history(self, obj):
        history_qs = history_service.get_history_queryset_by_model_instance(obj,
            types=(history_models.HistoryType.change, history_models.HistoryType.create,))

        return HistoryExportSerializerSerpy(history_qs, many=True).data


class AttachmentExportSerializerSerpy(serpy.Serializer):
    owner = UserRelatedFieldSerpy()
    attached_file = FileFieldSerpy()
    modified_date = DateTimeFieldSerpy()
    created_date = DateTimeFieldSerpy()
    name = serpy.Field()
    size = serpy.Field()
    sha1 = serpy.Field()
    is_deprecated = serpy.Field()
    description = serpy.Field()
    order = serpy.Field()


class AttachmentExportSerializerMixinSerpy(serpy.Serializer):
    attachments = serpy.MethodField("get_attachments")

    def get_attachments(self, obj):
        content_type = ContentType.objects.get_for_model(obj.__class__)
        attachments_qs = attachments_models.Attachment.objects.filter(object_id=obj.pk,
                                                                      content_type=content_type)
        return AttachmentExportSerializerSerpy(attachments_qs, many=True).data


class CustomAttributesValuesExportSerializerMixinSerpy(serpy.Serializer):
    custom_attributes_values = serpy.MethodField("get_custom_attributes_values")

    def custom_attributes_queryset(self, project):
        raise NotImplementedError()

    def get_custom_attributes_values(self, obj):
        def _use_name_instead_id_as_key_in_custom_attributes_values(custom_attributes, values):
            ret = {}
            for attr in custom_attributes:
                value = values.get(str(attr["id"]), None)
                if value is not  None:
                    ret[attr["name"]] = value

            return ret

        try:
            values =  obj.custom_attributes_values.attributes_values
            custom_attributes = self.custom_attributes_queryset(obj.project)

            return _use_name_instead_id_as_key_in_custom_attributes_values(custom_attributes, values)
        except ObjectDoesNotExist:
            return None


class WatcheableObjectModelSerializerMixinSerpy(serpy.Serializer):
    watchers = serpy.MethodField('get_watchers')

    def get_watchers(self, obj):
        return [user.email for user in obj.get_watchers()]
