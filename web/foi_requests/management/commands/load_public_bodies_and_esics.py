import csv
import io
from urllib.request import urlopen

from django.core.management.base import BaseCommand

from web.foi_requests import models


ESICS_URL = "https://raw.githubusercontent.com/vitorbaptista/dataset-sics-brasil/master/data/sics-brasil.csv"  # noqa: E501


class Command(BaseCommand):
    help = "Load new PublicBody and ESic from the CSV"

    def add_arguments(self, parser):
        parser.add_argument(
            "esics_url",
            nargs="?",
            help="URL to CSV containing the public bodies and eSICs",
            default=ESICS_URL,
        )

    def handle(self, *args, **options):
        esics_url = options["esics_url"]

        written_count = 0

        for esic in self._esics(esics_url):
            _create_or_update_public_body_and_esic(esic)
            written_count += 1

        msg = "Loaded {} public bodies and their respective eSICs in the database"
        self.stdout.write(msg.format(written_count))

    def _esics(self, url):
        response = urlopen(url)
        # It's a pity we're reading everything here, but I couldn't make
        # urlopen() read the file in text-mode, so I can't pass it directly to
        # the CSV reader
        response_text = response.read().decode("utf-8")
        return csv.DictReader(io.StringIO(response_text))


def _create_or_update_public_body_and_esic(esic_data):
    # TODO: Some e-SICs have e-mails instead
    esic_url = esic_data["url"]
    esic, _ = models.Esic.objects.update_or_create(url=esic_url)

    public_body, _ = models.PublicBody.objects.update_or_create(
        name=esic_data["orgao"],
        municipality=esic_data["municipio"],
        uf=esic_data["uf"],
        defaults={
            "esic": esic,
        },
    )

    return public_body
