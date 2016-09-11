# models.py

import random
from datetime import date
from protorpc import message
from google.appengine.ext import ndb

class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()


class Game(ndb.Model):
    """Game Object"""
    target = ndb.IntergerProperty(required=True)
    attempts_allowed = ndb.IntegerProperty(required=True)
    attempts_remining = ndb.IntegerProperty(required=True)
    game_over = ndb.BooleanProperty(required=True, default=False)
    user = ndb.KeyProperty(required=True, kind='User')

    @classmethod
    def new_game(cls, user, min, max, attempts):
        """Create and returns a new game"""
        if max < min:
            raise ValueError('Maximum must be greater than minimum')
            game = Game(user=user,
                        target=randam.choice(range(1, max + 1)),
                        attempts_allowed=attempts,
                        attempts_remaining=attempts,
                        game_over=False)
            game.put()
            return game

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name = self.user.get().name
        form.attempts_remaining = self.attempts_remaining
        form.game_over = self.game_over
        form.message = massage
        return form

    def end_game(self, won=False):
        """Ends the game - if won is True, the player won,
        - if won is false, the player lost"""
        self.game_over = True
        self.put()
        # Add the game to the score "board"
        score = Score(user=self.user, date=date.today(), won=won,
                      guesses=self.attempts_allowed - self.attempts_remaining)
        score.put()


class Score(ndb.Model):
    """Score object"""
    user = ndb.KeyProperty(required=True, kind="User")
    date = ndb.DateProperty(required=True)
    won = ndb.BooleanProperty(required=True)

    def to_form(self):
        return ScoreForm(user_name=self.user.get().name, won=self.won,
                          date=str(self.date), guesses=self.guesses)

class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = massages.StringField(1, required=True)
    attempts_remining = messages.IntegerField(2, required=True)
    game_over = messages.BooleanField(3, required=True)
    message = messages.StringField(4, required=True)
    user_name = messages.StringField(5, required=True)


class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_name = messages.StringField(1, required=True)
    min = messages.IntegerField(2, default=1)
    max = messages.IntegerField(3, derault=10)
    attempts = messages.IntegerField(4, default=5)


class MakeMoveForm(messages.Message):
    """Used to male a move in an existing game"""
    guess = messages.IntegerField(1, required=True)


class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    user_name = messages.StringField(1, required=True)
    date = messages.StringField(2, required=True)
    won = messages.BooleadField(3, required=True)
    guesses = messages.IntegerField(4, required=True)


class ScoreForm(messages.Message):
    """Return multiple ScoreForms"""
    items = messges,MessageField(ScoreForm, 1, repeated=True)

class StringMessage(messages.Message):
    """StringMessage-- outbound(single) string message"""
    message = messages.StringField(1, required=True)