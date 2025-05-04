import random
from datetime import datetime, timedelta

from django.utils.timezone import make_aware
from apps.lineup.models import PraiseLineup, LineupMember
from apps.accounts.models import Member

def populate_lineup_members():
    lineup_ids = PraiseLineup.objects.all()
    member_ids = Member.objects.all()

    created_count = 0

    for lineup in lineup_ids:
        usados = set()
        num_membros = random.randint(4, 7)

        while len(usados) < num_membros:
            member = random.choice(member_ids)
            functions = member.function.all()

            if not functions:
                continue

            function = random.choice(list(functions))
            key = (lineup.id, member.id, function.id)

            if key in usados:
                continue

            usados.add(key)
            obj, created = LineupMember.objects.get_or_create(
                lineup=lineup,
                member=member,
                function=function,
                defaults={
                    "created_at": make_aware(datetime.now() - timedelta(days=random.randint(0, 180))),
                    "updated_at": make_aware(datetime.now())
                }
            )
            if created:
                created_count += 1

    print(f"Criados {created_count} registros em LineupMember.")

populate_lineup_members()
