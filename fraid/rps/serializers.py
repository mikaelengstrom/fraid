from rest_framework import serializers
from . import (models,)


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Game
        fields = ('id',)


class ThrowSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Throw
        fields = ('computer_throw', 'human_throw', 'game_status')
