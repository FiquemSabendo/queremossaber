from django.db.models import QuerySet


class PublicBodyQueryset(QuerySet):
    def order_by_name(self, is_asc=True):
        ordering = 'lower_name' if is_asc else '-lower_name'
        return self.extra(select={'lower_name': 'lower(name)'}).order_by(ordering)
