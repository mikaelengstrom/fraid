from django.test import TestCase
from datetime import datetime
from .. import (models, constants, utils)


class ThrowTestCase(TestCase):
    def test_build_sequence(self):
        seq = utils.build_sequence([(constants.ROCK, constants.ROCK), (constants.SCISSORS, constants.ROCK), (constants.PAPER, constants.ROCK)])
        self.assertEqual(seq, 113121)

    def test_store_sequence(self):
        utils.store_sequence([(constants.ROCK, constants.ROCK)],
                       upcoming=constants.ROCK)
        self.assertEqual(1, len(models.Sequence.objects.all()))
        seq = models.Sequence.objects.first()
        self.assertEqual(datetime.now().day, seq.date.day)

    def test_store_long_sequence(self):
        utils.store_sequence([
            (constants.ROCK, constants.ROCK),
            (constants.SCISSORS, constants.SCISSORS),
            (constants.PAPER, constants.PAPER),
        ], upcoming=constants.ROCK)

        # Should only create 3 records
        self.assertEqual(3, len(models.Sequence.objects.all()))

        # Test that they are correct
        PP_R = models.Sequence.objects.filter(
            sequence=utils.build_sequence([(constants.PAPER, constants.PAPER)]),
            upcoming=constants.ROCK
        ).all()

        SSPP_R = models.Sequence.objects.filter(
            sequence=utils.build_sequence([(constants.SCISSORS, constants.SCISSORS),
                                     (constants.PAPER, constants.PAPER)]),
            upcoming=constants.ROCK
        ).all()

        RRSSPP_R = models.Sequence.objects.filter(
            sequence=utils.build_sequence([
                (constants.ROCK, constants.ROCK),
                (constants.SCISSORS, constants.SCISSORS),
                (constants.PAPER, constants.PAPER)]),
            upcoming=constants.ROCK
        ).all()

        self.assertEqual(1, len(PP_R),
                         msg="No match for sequence PaperPaper|Rock")
        self.assertEqual(1, len(SSPP_R),
                         msg="No match for sequence ScissorScissorPaperPaper|Rock")
        self.assertEqual(1, len(RRSSPP_R),
                         msg="No match for sequence RockRockScissorScissorPaperPaper|Rock")

    def test_calculate_winner(self):
        self.assertEqual(
            utils.calculate_winner((constants.ROCK, constants.SCISSORS)),
            constants.WIN
        )

        self.assertEqual(
            utils.calculate_winner((constants.ROCK, constants.ROCK)),
            constants.TIE
        )

        self.assertEqual(
            utils.calculate_winner((constants.PAPER, constants.SCISSORS)),
            constants.LOSE
        )

    def test_throw(self):
        (status, last_moves) = utils.throw([], constants.ROCK)
        self.assertEqual(1, len(last_moves))

        (status, last_moves) = utils.throw([], constants.ROCK)
        self.assertEqual(status, constants.LOSE)

        (status, last_moves) = utils.throw([
            (constants.ROCK, constants.SCISSORS),
            (constants.PAPER, constants.PAPER),
            (constants.SCISSORS, constants.SCISSORS),
        ], constants.ROCK)

        self.assertEqual(len(last_moves), 4)

        (status, last_moves) = utils.throw([
            (constants.ROCK, constants.SCISSORS),
            (constants.PAPER, constants.PAPER),
            (constants.SCISSORS, constants.SCISSORS),
        ], constants.ROCK)

        self.assertEqual(status, constants.LOSE)

        (status, last_moves) = utils.throw([
            (constants.ROCK, constants.SCISSORS),
            (constants.PAPER, constants.PAPER),
            (constants.SCISSORS, constants.SCISSORS),
        ], constants.SCISSORS)

        self.assertEqual(status, constants.WIN)
