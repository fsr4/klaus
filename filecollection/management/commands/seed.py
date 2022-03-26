from django.core.management import BaseCommand

from filecollection.models import Major


class Command(BaseCommand):
    help = 'Load seed data into the database'

    majors = {
        "ai-b": "AI (B) - Angewandte Informatik (Bachelor)",
        "ai-m": "AI (M) - Angewandte Informatik (Master)",
        "fiw-b": "FIW (B) - Informatik und Wirtschaft (Frauenstudiengang_Bachelor)",
        "ikg-b": "IKG (B) - Informatik in Kultur und Gesundheit",
        "imi-b": "IMI (B) - Internationale Medieninformatik (Bachelor)",
        "imi-m": "IMI (M) - Internationale Medieninformatik (Master)",
        "wi-b": "WI (B) - Wirtschaftsinformatik (Bachelor)",
        "wi-m": "WI (M) - Wirtschaftsinformatik (Master)",
        "wiko-b": "WiKo (B) - Wirtschaftskommunikation (Bachelor)",
        "wiko-m": "WiKo (M) - Wirtschaftskommunikation (Master)",
        "wm-b": "WiMa (B) - Wirtschaftsmathematik (Bachelor)",
        "far-m": "WiMa (M) - Finanzmathematik, Aktuarwissenschaften und Risikomanagement (Master)",
        "wiw-b": "WIW (B) - Wirtschaftsingenieurwesen (Bachelor)",
        "wiw-m": "WIW (M) - Wirtschaftsingenieurwesen (Master)",
    }

    def create_majors(self):
        for slug, major in self.majors.items():
            major, created = Major.objects.get_or_create(name=major, slug=slug)
            if created:
                self.stdout.write(self.style.NOTICE('created major "%s"' % major))
            else:
                self.stdout.write(self.style.NOTICE('major "%s" already exists, skipping' % major))

    def handle(self, *args, **options):
        self.create_majors()
        self.stdout.write(self.style.SUCCESS('Successfully seeded the database'))
