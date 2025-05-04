from rest_framework import serializers

from .models import LineupMember, PraiseLineup


class PraiseLineupSerializers(serializers.ModelSerializer):
    class Meta:
        model = PraiseLineup
        fields = "__all__"


class LineupMemberSerializers(serializers.ModelSerializer):
    lineup = PraiseLineupSerializers()
    member_display = serializers.SerializerMethodField()
    function_display = serializers.SerializerMethodField()

    class Meta:
        model = LineupMember
        fields = "__all__"

    
