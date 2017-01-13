from random import randint

from django.db.models import Count
from django.test import TestCase
from datetime import datetime
from .. import (models, constants)


def build_sequence(sequence):
    """Converts a sequence to int

    ex: [(ROCK, ROCK), (SCISSOR, PAPER)] -> 1123
    """
    if not sequence:
        return constants.EMPTY_SEQUENCE

    str_sequence = ""\
        .join([str(human) + str(computer) for (human, computer) in sequence])

    return int(str_sequence)


def store_sequence(sequence, upcoming):
    """Store sequences to database. One record for each available sequence

    sequence -- [(ROCK, ROCK)]
    upcoming -- ROCK
    """
    if not sequence:
        models.Sequence(sequence=constants.EMPTY_SEQUENCE, upcoming=upcoming).save()

    else:
        previous = []
        sequence.reverse()
        for round in sequence:
            previous.insert(0, round)
            seq_model = models.Sequence(
                sequence=build_sequence(previous), upcoming=upcoming)
            seq_model.save()


def calculate_ai_response(sequence):
    """Calculate the ai response based on a sequence

    sequence -- [(ROCK, ROCK)]

    return opposite of the most common followup
    """
    best_opponent_guess = models.Sequence.objects \
        .filter(sequence=build_sequence(sequence))\
        .values('upcoming')\
        .annotate(cnt=Count('upcoming'))\
        .order_by('-cnt')\
        .first()

    if not best_opponent_guess:
        if len(sequence) <= 1:
            return randint(1, 3)

        sequence.pop(0)
        return calculate_ai_response(sequence)

    best_counter_move = best_opponent_guess['upcoming'] + 1

    return best_counter_move if best_counter_move < 4 else 1


def calculate_winner(round):
    """Decide winner of a round

    round -- (human, computer)
    Ex. (ROCK, ROCK) -> Tie, (ROCK, PAPER) -> LOSE
    """
    human, computer = round
    if human == computer:
        return constants.TIE
    elif computer + 1 == human or (computer == constants.SCISSORS and human == constants.ROCK):
        return constants.WIN
    else:
        return constants.LOSE


def throw(last_moves, next_throw):
    """Does all the necessary calculations and storing for a throw. Return
    a tuple of victory status and the history of the current game

    Ex.
        throw([], ROCK) -> (LOSE, [(ROCK, PAPER)])
    """
    ai_response = calculate_ai_response(last_moves)
    store_sequence(sequence=last_moves, upcoming=next_throw)
    next_round = (next_throw, ai_response)
    status = calculate_winner(next_round)

    return status, last_moves + [next_round]


class ThrowTestCase(TestCase):

    def test_build_sequence(self):
        seq = build_sequence([(constants.ROCK, constants.ROCK), (constants.SCISSORS, constants.ROCK), (constants.PAPER, constants.ROCK)])
        self.assertEqual(seq, 113121)

    def test_store_sequence(self):
        store_sequence([(constants.ROCK, constants.ROCK)],
                       upcoming=constants.ROCK)
        self.assertEqual(1, len(models.Sequence.objects.all()))
        seq = models.Sequence.objects.first()
        self.assertEqual(datetime.now().day, seq.date.day)

    def test_store_long_sequence(self):
        store_sequence([
            (constants.ROCK, constants.ROCK),
            (constants.SCISSORS, constants.SCISSORS),
            (constants.PAPER, constants.PAPER),
        ], upcoming=constants.ROCK)

        # Should only create 3 records
        self.assertEqual(3, len(models.Sequence.objects.all()))

        # Test that they are correct
        PP_R = models.Sequence.objects.filter(
            sequence=build_sequence([(constants.PAPER, constants.PAPER)]),
            upcoming=constants.ROCK
        ).all()

        SSPP_R = models.Sequence.objects.filter(
            sequence=build_sequence([(constants.SCISSORS, constants.SCISSORS),
                                     (constants.PAPER, constants.PAPER)]),
            upcoming=constants.ROCK
        ).all()

        RRSSPP_R = models.Sequence.objects.filter(
            sequence=build_sequence([
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
            calculate_winner((constants.ROCK, constants.SCISSORS)),
            constants.WIN
        )

        self.assertEqual(
            calculate_winner((constants.ROCK, constants.ROCK)),
            constants.TIE
        )

        self.assertEqual(
            calculate_winner((constants.PAPER, constants.SCISSORS)),
            constants.LOSE
        )

    def test_throw(self):
        (status, last_moves) = throw([], constants.ROCK)
        self.assertEqual(1, len(last_moves))

        (status, last_moves) = throw([], constants.ROCK)
        self.assertEqual(status, constants.LOSE)

        (status, last_moves) = throw([
            (constants.ROCK, constants.SCISSORS),
            (constants.PAPER, constants.PAPER),
            (constants.SCISSORS, constants.SCISSORS),
        ], constants.ROCK)


