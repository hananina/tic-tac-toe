"""models.py - This file contains the class definitions for the Datastore
entities used by the Game."""

import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email =ndb.StringProperty()
    wins = ndb.IntegerProperty(default=0)

    def add_win(self):
        """Add a win"""
        self.wins += 1
        self.put()
        print self.wins

    def to_form(self):
        return UserForm(name=self.name,
                        email=self.email,
                        wins=self.wins)


class Game(ndb.Model):
    """Game object"""

    user_o      = ndb.KeyProperty(required=True, kind='User')
    user_x      = ndb.KeyProperty(required=True, kind='User')

    attempts    = ndb.IntegerProperty(required=True, default=9)
    score_board = ndb.PickleProperty(required=True, default={})
    next_move   = ndb.KeyProperty(required=True, kind='User')

    game_over   = ndb.BooleanProperty(required=True, default=False)
    tie         = ndb.BooleanProperty(required=True, default=False)

    cancelled   = ndb.BooleanProperty(required=True, default=False)
    history     = ndb.PickleProperty(required=True, default={})

    @classmethod
    def new_game(cls, user_o, user_x):
        """Creates and returns a new game"""

        game = Game(user_o=user_o,
                    user_x=user_x,
                    attempts=9,
                    score_board=['' for _ in range(attempts)],
                    next_move=user_o,
                    game_over=False,
                    tie=False,
                    history= [],
                    cancelled=False,
                    )
        game.put()
        return game

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_o_name = self.user_o.get().name
        form.user_x_name = self.user_x.get().name
        form.attempts = self.attempts
        form.game_over = self.game_over
        form.cancelled = self.cancelled
        form.message = message
        return form


    def end_game(self, won=False, history=False):
        """Ends the game - if won is True, the player won. - if won is False,
        the player lost."""
        self.game_over = True

        if history:
            self.history.append(("over!", "human player won."))
        else:
            self.history.append(("over!", "AI player won."))

        self.put()
        # Add the game to the score 'board'
        score = Score(user=self.user, date=date.today(), won=won)
        score.put()
        # Add user model a won
        self.user.get().add_win()


    def cancel_game(self):
        """cancel the game"""
        self.cancelled = True
        self.put()


class Score(ndb.Model):
    """Score object"""
    user_o = ndb.KeyProperty(required=True, kind='User')
    user_x = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True)
    won = ndb.BooleanProperty(required=True,default=False)

    def to_form(self):
        return ScoreForm(
            user_o_name=self.user_o.get().name, user_x_name=self.user_x.get().name, won=self.won,
            date=str(self.date)
        )

class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    attempts = messages.IntegerField(2, required=True)
    game_over = messages.BooleanField(3, required=True)
    cancelled = messages.BooleanField(4, required=True)
    message = messages.StringField(5, required=True)
    user_name = messages.StringField(6, required=True)


class GameForms(messages.Message):
    """Return multiple GameForms"""
    items = messages.MessageField(GameForm, 1, repeated=True)


class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_o = messages.StringField(1, required=True)
    user_x = messages.StringField(2, required=True)

class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""

    user_name = messages.StringField(1, required=True)
    move = messages.IntegerField(2, required=True)


class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    user_o_name = messages.StringField(1, required=True)
    user_x_name = messages.StringField(2, required=True)
    date = messages.StringField(3, required=True)
    won = messages.BooleanField(4, required=True)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)


class UserForm(messages.Message):
    """User Form"""
    name = messages.StringField(1, required=True)
    email = messages.StringField(2)
    wins = messages.IntegerField(3, required=True)

class UserForms(messages.Message):
    """Container for multiple User Forms"""
    items = messages.MessageField(UserForm, 1, repeated=True)

class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)
