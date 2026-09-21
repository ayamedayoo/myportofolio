"""Context processor supaya data identitas pemilik portofolio tersedia di semua template.

Sebelumnya setiap view menulis ulang ``"name": "Samuel Kaevin Phasca"`` di context-nya.
Dengan context processor ini, ``{{ name }}`` di ``base.html`` otomatis terisi.
"""

OWNER_NAME = "Samuel Kaevin Phasca"


def portfolio_owner(request):
    return {"name": OWNER_NAME}
