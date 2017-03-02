from random import randint
from django.db.models import Count
from . import (models, constants)


def build_sequence(sequence):
    """Converts a sequence to int

    ex: [(ROCK, ROCK), (SCISSOR, PAPER)] -> 1123
    """
    if not sequence:
        return constants.EMPTY_SEQUENCE

    str_sequence = "" \
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
    _sequence = sequence.copy()
    best_opponent_guess = models.Sequence.objects \
        .filter(sequence=build_sequence(_sequence)) \
        .values('upcoming') \
        .annotate(cnt=Count('upcoming')) \
        .order_by('-cnt') \
        .first()

    if not best_opponent_guess:
        if len(_sequence) <= 1:
            return randint(1, 3)

        _sequence.pop(0)
        return calculate_ai_response(_sequence)

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
