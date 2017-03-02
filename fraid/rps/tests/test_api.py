from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .. import (models, utils, constants)


class ApiTestCase(APITestCase):
    def test_new_game(self):
        resp = self.client.post(reverse('api:game-list'))
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(models.Game.objects.all()), 1)
        self.assertEqual(resp.data['id'], str(models.Game.objects.first().id))

    def test_throw_reverse(self):
        game = models.Game.objects.create()
        rev = reverse('api:game-throw', kwargs={'pk': game.id})
        self.assertEqual('/api/v1/games/{}/throw/'.format(game.id), rev)

    def test_throw_rejects_bad_params(self):
        game = models.Game.objects.create()
        rev = reverse('api:game-throw', kwargs={'pk': game.id})

        # Good requests
        resp = self.client.post(rev, {'throw': 'ROCK'})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        resp = self.client.post(rev, {'throw': 'paper'})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        resp = self.client.post(rev, {'throw': 'scissors'})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Bad req
        resp = self.client.post(rev, {'throw': 'ROCKs'})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_throw_and_use_sequences(self):
        game = models.Game.objects.create()
        rev = reverse('api:game-throw', kwargs={'pk': game.id})

        # Good requests
        resp1 = self.client.post(rev, {'throw': 'ROCK'})
        resp2 = self.client.post(rev, {'throw': 'ROCK'})

        self.assertEqual(resp1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp2.status_code, status.HTTP_201_CREATED)

        seq = utils.build_sequence([
            (resp1.data['human_throw'], resp1.data['computer_throw']),
        ])

        self.assertEqual(len(models.Sequence.objects.filter(sequence=seq)), 1)
