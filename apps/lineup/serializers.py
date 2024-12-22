from rest_framework import serializers

from .models import PraiseLineup

class PraiseLineupSerializers(serializers.ModelSerializer):
    class Meta:
        model = PraiseLineup
        fields = '__all__'