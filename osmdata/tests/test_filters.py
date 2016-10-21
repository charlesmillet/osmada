from django.test import TestCase

from ..filters import IgnoreUsers, IgnoreNewTags, IgnoreChangedTags
from ..models import Action


class AbstractFilterTestcase(TestCase):
    def assertFilterCount(self,_filter, expected_count):
        filtered_qs = _filter.filter(Action.objects)
        return self.assertEqual(filtered_qs.count(), expected_count)


class TestIgnoreUsers(AbstractFilterTestcase):
    fixtures = ['test_filters.json']  # Versailles Chantier

    def test_empty_list(self):
        self.assertFilterCount(IgnoreUsers([]), 1)

    def test_ignored_new_user(self):
        self.assertFilterCount(IgnoreUsers(['foo', 'Eunjeung Yu']), 0)

    def test_ignored_old_user(self):
        """ Old user of an item should not be taken into account for that
        filter
        """
        self.assertFilterCount(IgnoreUsers(['foo', 'overflorian']), 1)


class TestIgnoreNewTags(AbstractFilterTestcase):
    fixtures = ['test_filters_2.json']  # Pont Cadinet

    def test_non_present_tag(self):
        self.assertFilterCount(IgnoreNewTags("non=existent"), 3)

    def test_noncreate_tag(self):
        self.assertFilterCount(IgnoreNewTags("access=no"), 3)

    def test_modify_tag(self):
        self.assertFilterCount(IgnoreNewTags("shop=newsagent"), 2)

    def test_modify_wrong_val(self):
        self.assertFilterCount(IgnoreNewTags("shop=coffee"), 3)

    def test_modify_tag_wildcard_value(self):
        self.assertFilterCount(IgnoreNewTags("shop=*"), 2)


class TestIgnoreModifiedTags(AbstractFilterTestcase):
    fixtures = ['test_filters_2.json']  # Pont Cadinet

    def test_non_present_tag(self):
        self.assertFilterCount(IgnoreChangedTags("non=existent"), 3)

    def test_create_tag(self):
        self.assertFilterCount(IgnoreChangedTags("access=no"), 2)

    def test_modify_wrong_val(self):
        self.assertFilterCount(IgnoreChangedTags("access=hello"), 3)

    def test_modify_tag_wildcard_value(self):
        self.assertFilterCount(IgnoreChangedTags("access=*"), 2)