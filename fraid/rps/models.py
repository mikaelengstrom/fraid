import uuid

from django.db import models

from . import (utils,constants)


# Create your models here.
class Sequence(models.Model):
    sequence = models.BigIntegerField()
    upcoming = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)


class Game(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def throw(self, throw):
        last_throws = self.throw_set.order_by('-pk')[:5]
        seq = [(x.human_throw, x.computer_throw) for x in last_throws]
        seq.reverse()

        (victory_status, throw_sequence) = utils.throw(seq, throw)
        (human_throw, ai_throw) = throw_sequence.pop()

        return Throw.objects.create(
            game=self,
            computer_throw=ai_throw,
            human_throw=human_throw,
            game_status=victory_status
        )


class Throw(models.Model):
    game = models.ForeignKey(Game)

    computer_throw = models.IntegerField()
    human_throw = models.IntegerField()
    game_status = models.IntegerField()
