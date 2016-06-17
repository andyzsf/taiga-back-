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

from taiga.projects.votes import services as votes_service

from .serpy_fields import (TimelineDataFieldSerpy, UserRelatedFieldSerpy,
                           ProjectRelatedFieldSerpy, DateTimeFieldSerpy,
                           PgArrayFieldSerpy, NestedArraySerpy)
from .serpy_mixins import (CustomAttributesValuesExportSerializerMixinSerpy,
                           HistoryExportSerializerMixinSerpy,
                           AttachmentExportSerializerMixinSerpy,
                           WatcheableObjectModelSerializerMixinSerpy)
from .cache import (_custom_tasks_attributes_cache,
                    _custom_userstories_attributes_cache,
                    _custom_issues_attributes_cache)


class TimelineExportSerializerSerpy(serpy.Serializer):
    data_content_type = serpy.Field('data_content_type_id')
    data = TimelineDataFieldSerpy()
    created = DateTimeFieldSerpy()
    event_type = serpy.Field()
    content_type = serpy.Field('content_type_id')


class IssueExportSerializerSerpy(CustomAttributesValuesExportSerializerMixinSerpy, HistoryExportSerializerMixinSerpy,
                                 AttachmentExportSerializerMixinSerpy, WatcheableObjectModelSerializerMixinSerpy):
    owner = UserRelatedFieldSerpy()
    status = ProjectRelatedFieldSerpy(slug_field="name")
    assigned_to = UserRelatedFieldSerpy()
    priority = ProjectRelatedFieldSerpy(slug_field="name")
    severity = ProjectRelatedFieldSerpy(slug_field="name")
    type = ProjectRelatedFieldSerpy(slug_field="name")
    milestone = ProjectRelatedFieldSerpy(slug_field="name")
    votes = serpy.MethodField("get_votes")
    created_date = DateTimeFieldSerpy()
    modified_date = DateTimeFieldSerpy()
    finished_date = DateTimeFieldSerpy()
    tags = PgArrayFieldSerpy()
    is_blocked = serpy.Field()
    blocked_note = serpy.Field()
    version = serpy.Field()
    ref = serpy.Field()
    subject = serpy.Field()
    description = serpy.Field()
    # attachments = serpy.Field()
    external_reference = NestedArraySerpy()

    def get_votes(self, obj):
        return [x.email for x in votes_service.get_voters(obj)]

    def custom_attributes_queryset(self, project):
        if project.id not in _custom_issues_attributes_cache:
            _custom_issues_attributes_cache[project.id] = list(project.issuecustomattributes.all().values('id', 'name'))
        return _custom_issues_attributes_cache[project.id]


class TaskExportSerializerSerpy(CustomAttributesValuesExportSerializerMixinSerpy, HistoryExportSerializerMixinSerpy,
                                AttachmentExportSerializerMixinSerpy, WatcheableObjectModelSerializerMixinSerpy):
    owner = UserRelatedFieldSerpy()
    status = ProjectRelatedFieldSerpy(slug_field="name")
    user_story = ProjectRelatedFieldSerpy(slug_field="ref", required=False)
    milestone = ProjectRelatedFieldSerpy(slug_field="name")
    assigned_to = UserRelatedFieldSerpy()
    created_date = DateTimeFieldSerpy()
    modified_date = DateTimeFieldSerpy()
    finished_date = DateTimeFieldSerpy()
    tags = PgArrayFieldSerpy()
    is_blocked = serpy.Field()
    blocked_note = serpy.Field()
    version = serpy.Field()
    ref = serpy.Field()
    subject = serpy.Field()
    description = serpy.Field()
    # attachments = serpy.Field()
    external_reference = NestedArraySerpy()
    us_order = serpy.Field()
    taskboard_order = serpy.Field()
    is_iocaine = serpy.Field()

    def custom_attributes_queryset(self, project):
        if project.id not in _custom_tasks_attributes_cache:
            _custom_tasks_attributes_cache[project.id] = list(project.taskcustomattributes.all().values('id', 'name'))
        return _custom_tasks_attributes_cache[project.id]


class RolePointsFieldSerpy(serpy.Serializer):
    def to_value(self, data):
        return [{"role": x.role.name, "points": x.points.name} for x in data.all()]


class UserStoryExportSerializerSerpy(CustomAttributesValuesExportSerializerMixinSerpy, HistoryExportSerializerMixinSerpy,
                                     AttachmentExportSerializerMixinSerpy, WatcheableObjectModelSerializerMixinSerpy):
    role_points = RolePointsFieldSerpy()
    generated_from_issue = ProjectRelatedFieldSerpy(slug_field="ref")
    owner = UserRelatedFieldSerpy()
    status = ProjectRelatedFieldSerpy(slug_field="name")
    milestone = ProjectRelatedFieldSerpy(slug_field="name")
    assigned_to = UserRelatedFieldSerpy()
    created_date = DateTimeFieldSerpy()
    modified_date = DateTimeFieldSerpy()
    finish_date = DateTimeFieldSerpy()
    tags = PgArrayFieldSerpy()
    is_blocked = serpy.Field()
    blocked_note = serpy.Field()
    version = serpy.Field()
    ref = serpy.Field()
    subject = serpy.Field()
    description = serpy.Field()
    # attachments = serpy.Field()
    external_reference = NestedArraySerpy()
    backlog_order = serpy.Field()
    sprint_order = serpy.Field()
    kanban_order = serpy.Field()
    is_closed = serpy.Field()
    client_requirement = serpy.Field()
    team_requirement = serpy.Field()
    tribe_gig = serpy.Field()


    def custom_attributes_queryset(self, project):
        if project.id not in _custom_userstories_attributes_cache:
            _custom_userstories_attributes_cache[project.id] = list(project.userstorycustomattributes.all().values('id', 'name'))
        return _custom_userstories_attributes_cache[project.id]
