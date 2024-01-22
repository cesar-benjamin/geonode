#########################################################################
#
# Copyright (C) 2023 Open Source Geospatial Foundation - all rights reserved
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

import collections
import logging

from django.db.models import Count

from geonode.base.models import TopicCategory
from geonode.facets.models import FACET_TYPE_CATEGORY, FacetProvider, DEFAULT_FACET_PAGE_SIZE, FACET_TYPE_GROUP
from itertools import chain
from geonode.groups.models import GroupProfile
from geonode.security.utils import get_user_visible_groups
logger = logging.getLogger(__name__)


class GroupFacetProvider(FacetProvider):
    """
    Implements faceting for resource's group
    """

    @property
    def name(self) -> str:
        return "group"

    def get_info(self, lang="en", **kwargs) -> dict:
        return {
            "name": self.name,
            "filter": "filter{group.in}",
            "label": "Group",
            "type": FACET_TYPE_CATEGORY,
        }

    def get_facet_items(
        self,
        queryset,
        start: int = 0,
        end: int = DEFAULT_FACET_PAGE_SIZE,
        lang="en",
        topic_contains: str = None,
        keys: set = {},
        **kwargs,
    ) -> (int, list):
        logger.debug("Retrieving facets for %s", self.name)
        #logger.warning("user is ",**kwargs)
        #print('i came i saw i printed')
        #print(kwargs['user'])
        filters = {"resourcebase__in": queryset}

        if topic_contains:
            filters["gn_description__icontains"] = topic_contains

        if keys:
            logger.debug("Filtering by keys %r", keys)
            filters["identifier__in"] = keys

        visible_groups= get_user_visible_groups(user=kwargs['user'])# need to get info from user 
        # if isinstance(visible_groups, list):
        #     q=queryset.values('group__name', 'group__id').annotate(count=Count("pk")).filter(group__id__in=[group.group_id for group in visible_groups])
        # else:
        #     q = queryset.values('group__name', 'group__id').annotate(count=Count("pk")).filter(group__id__in=[group.group_id for group in visible_groups])
        q=queryset.values('group__name', 'group__id').annotate(count=Count("pk")).filter(group__id__in=[group.group_id for group in visible_groups])

        






        logger.debug(" PREFILTERED QUERY  ---> %s\n\n", queryset.query)
        logger.debug(" ADDITIONAL FILTERS ---> %s\n\n", filters)
        logger.debug(" FINAL QUERY        ---> %s\n\n", q.query)
        logger.warning(" FINAL QUERY        ---> %s\n\n", q.query)
        

        cnt = q.count()
        logger.warning(f" q.count()  {q.count()}")
        logger.info("Found %d facets for %s", cnt, self.name)
        logger.debug(" ---> %s\n\n", q.query)
        logger.debug(" ---> %r\n\n", q.all())

        topics = [
            {
                "key": r['group__id'],
                "label":r['group__name'],
                "count": r['count'],
            }
            for r in q[start:end].all()
        ]


        return cnt, topics

    def get_topics(self, keys: list, lang="en", **kwargs) -> list:
        #TODO change this logic aswell

        q = TopicCategory.objects.filter(identifier__in=keys)
        q= get_user_visible_groups()

        logger.debug(" ---> %s\n\n", q.query)
        logger.debug(" ---> %r\n\n", q.all())

        return [
            {
                "key": r["slug"],
                "label": r["name"],
            }
            for r in q.all()
        ]



    @classmethod
    def register(cls, registry, **kwargs) -> None:
        registry.register_facet_provider(GroupFacetProvider(**kwargs))
