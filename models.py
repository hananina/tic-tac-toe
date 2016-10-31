"""models.py - This file contains the class definitions for the Datastore
entities used by the Game."""

import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb


class User(ndb.Model):
    """User profile"""
    name  = ndb.StringProperty(required=True)
    email = ndb.StringProperty()

    def to_form(self):
        return UserForm(name=self.name,
                        email=self.email)


class Game(ndb.Model):
    """Game object"""
    user_o      = ndb.KeyProperty(required=True, kind='User')
    user_x      = ndb.KeyProperty(required=True, kind='User')
    attempts    = ndb.IntegerProperty(required=True, default=9)
    board       = ndb.PickleProperty(required=True, default={})
    next_move   = ndb.KeyProperty(required=True, kind='User')
    game_over   = ndb.BooleanProperty(required=True, default=False)
    tie         = ndb.BooleanProperty(default=False)
    cancelled   = ndb.BooleanProperty(required=True, default=False)
    history     = ndb.PickleProperty(required=True, default={})
    winner      = ndb.StringProperty()

    @classmethod
    def new_game(cls, user_o, user_x):
        """Creates and returns a new game"""

        game = Game(user_o=user_o,
                    user_x=user_x,
                    attempts=9,
                    board=['' for _ in range(9)],
                    next_move=user_o,
                    game_over=False,
                    tie=False,
                    history=[],
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
        form.next_move   = self.next_move.get().name
        form.attempts    = self.attempts
        form.game_over   = self.game_over
        form.tie         = self.tie
        form.cancelled   = self.cancelled
        form.winner      = self.winner
        form.message     = message
        return form


    def end_game(self, won, user):
        """Ends the game - if won is True, the player won. - if won is False,
        the player lost."""

        if won:
            self.winner = user.name
        else:
            self.tie = True

        self.game_over = True
        self.put()
    
        score = Score(
                    winner=self.winner, 
                    user_o=self.user_o, 
                    user_x=self.user_x, 
                    date=date.today()
                )
        score.put()



    def cancel_game(self):
        """cancel the game"""
        self.cancelled = True
        self.put()


class Score(ndb.Model):
    """Score object"""
    winner = ndb.StringProperty(required=True)
    user_o = ndb.KeyProperty(required=True)
    user_x = ndb.KeyProperty(required=True)
    date = ndb.DateProperty(required=True)

    def to_form(self):
        return ScoreForm(
            winner=self.winner,
            user_o=self.user_o.get().name,
            user_x=self.user_x.get().name,
            date=str(self.date)
        )

class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    attempts    = messages.IntegerField(2, required=True)
    user_o_name = messages.StringField(3, required=True)
    user_x_name = messages.StringField(4, required=True)
    next_move   = messages.StringField(5, required=True)
    game_over   = messages.BooleanField(6, required=True)
    tie         = messages.BooleanField(7)
    cancelled   = messages.BooleanField(8)
    winner      = messages.StringField(9)
    message     = messages.StringField(10, required=True)


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
    winner = messages.StringField(1, required=True)
    user_o = messages.StringField(2, required=True)
    user_x = messages.StringField(3, required=True)
    date = messages.StringField(4, required=True)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)


class UserForm(messages.Message):
    """User Form"""
    name = messages.StringField(1, required=True)
    email = messages.StringField(2)

class UserForms(messages.Message):
    """Container for multiple User Forms"""
    items = messages.MessageField(UserForm, 1, repeated=True)

class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)
