from django.conf import settings
from django.db import models

from osmdata.models import Tag, OSMElement


class ActionReport:
    """ Utility class to process some costly analysis on Action instances

    Future evolutions may include storing the output of the analysis (that
    means turning ActionReport into a Django model) in database, to allow
    filtering on it.
    """
    @classmethod
    def find_main_tag(cls, action, tags_importance):
        """
        :type action: Action
        :param tags_importance: ordered list giving tag patterns giving
           precedence for (most important first). Each pattern can be a
           compound form.
           ex: ``["railway=station,operator=SNCF", man_made=tower]``.
        :return: the main tag (tag pattern of the list which won), or None
        :rtype str:
        """
        new_tags = Tag.objects.filter(element=action.new)
        old_tags = Tag.objects.filter(element=action.old)

        # FIXME: could be optimised with a SQL ORDER BY CASE...

        # We try first the new tags and then the old tags
        for taglist in old_tags, new_tags:
            for tag_pattern in tags_importance:
                relevant_tags = taglist.filter(
                    **Tag.parse_tag_pattern(tag_pattern))
                if relevant_tags.exists():
                    return str(relevant_tags.first())

        return None

    @classmethod
    def is_tag_action(cls, action):
        """
        :type action: Action
        """

        if action.type == action.CREATE:
            return False
        else:
            old = action.old
            new = action.new
            return old.tags_dict() != new.tags_dict()

    @classmethod
    def is_geometric_action(cls, action):
        """
        :type action: Action
        """
        element_type = action.new.type()

        if action.type in (action.CREATE, action.DELETE):
            return True

        else:
            if element_type == OSMElement.NODE:
                return (
                    (action.new.node.lat != action.old.node.lat) or
                    (action.new.node.lon != action.old.node.lon))

            elif element_type == OSMElement.WAY:
                return action.old.way.nodes_list() != action.new.way.nodes_list()

            elif element_type == OSMElement.RELATION:
                return False # FIXME: According to the meaning of what is a geometric action

    @classmethod
    def added_tags(cls, action):
        """
        :type action: Action
        """
        new_tags = action.new.tags_dict()

        if action.type == action.CREATE:
            return list(action.new.tags.all())
        else:
            old_tags = action.old.tags_dict()

            return [action.new.tags.get(k=i)
                    for i in new_tags if i not in old_tags]

    @classmethod
    def removed_tags(cls, action):
        new_tags = action.new.tags_dict()
        if action.type == action.CREATE:
            return []
        else:
            old_tags = action.old.tags_dict()

            return [action.old.tags.get(k=i)
                    for i in old_tags if i not in new_tags]

    @classmethod
    def modified_tags(cls, action):
        """
        :type action: Action
        """
        if action.type == action.CREATE:
            return [], list(action.new.tags.all())
        else:
            old_tags = action.old.tags_dict()

            old_versions = []
            new_versions = []

            for new_tag in action.new.tags.all():
                if new_tag.k in old_tags and old_tags[new_tag.k] != new_tag.v:
                    new_versions.append(new_tag)
                    old_versions.append(action.old.tags.get(k=new_tag.k))

            return old_versions, new_versions
