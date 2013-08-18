from django.core.management.base import NoArgsCommand

from aws.utils import load_security_groups


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        load_security_groups()
