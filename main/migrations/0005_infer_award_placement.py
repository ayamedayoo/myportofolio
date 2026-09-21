"""Isi kolom ``placement`` untuk data Award lama berdasarkan judulnya.

Data award dari CV sudah menuliskan peringkat di judul ("1st Place ...",
"Finalist ..."), jadi tidak perlu diisi ulang satu per satu lewat form.
"""
from django.db import migrations

KEYWORDS = [
    ('first', ('1st', 'juara 1', 'first place')),
    ('second', ('2nd', 'juara 2', 'second place')),
    ('third', ('3rd', 'juara 3', 'third place')),
    ('finalist', ('finalist', 'finalis')),
]


def infer_placement(apps, schema_editor):
    Award = apps.get_model('main', 'Award')
    for award in Award.objects.filter(placement='other'):
        lowered = award.title.lower()
        for placement, words in KEYWORDS:
            if any(word in lowered for word in words):
                award.placement = placement
                award.save(update_fields=['placement'])
                break


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_award_details'),
    ]

    operations = [
        migrations.RunPython(infer_placement, migrations.RunPython.noop),
    ]
