from django.core.management.base import NoArgsCommand

from aws.utils import load_keys


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        load_keys()
