from rest_framework import (viewsets, mixins, status, response)
from rest_framework.decorators import detail_route

from . import (serializers, models, constants)


class InvalidStringException(Exception):
    pass


def str_to_const(string):
    _s = string.upper()
    if _s == 'ROCK':
        return constants.ROCK
    elif _s == 'PAPER':
        return constants.PAPER
    elif _s == 'SCISSORS':
        return constants.SCISSORS
    else:
        raise InvalidStringException


class GameViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    queryset = models.Game.objects.all()
    serializer_class = serializers.GameSerializer

    @detail_route(methods=['post'], url_path='throw')
    def throw(self, request, pk=None):
        game = self.get_object()
        try:
            user_throw = str_to_const(request.data['throw'])
        except InvalidStringException:
            return response.Response({
                'error': 'Invalid parameter {}'.format(request.data['throw'])
            }, status=status.HTTP_400_BAD_REQUEST)

        throw = game.throw(user_throw)
        serializer = serializers.ThrowSerializer(instance=throw)
        return response.Response(serializer.data, status=status.HTTP_201_CREATED)
