 # -*- coding: utf-8 -*-`
"""api.py - game logic For Tic Tac Toe."""


import logging
import endpoints
from protorpc import remote, messages
from google.appengine.api import memcache
from google.appengine.api import taskqueue

from models import User, Game, Score
from models import (
    StringMessage, NewGameForm, GameForm, GameForms, MakeMoveForm,\
    ScoreForm, ScoreForms, UserForm, UserForms
)

from utils import get_by_urlsafe


# Endpoint requets which is the data you input in endpoint form
NEW_GAME_REQUEST = endpoints.ResourceContainer(
    NewGameForm)

GET_GAME_REQUEST = endpoints.ResourceContainer(
    urlsafe_game_key=messages.StringField(1),)

MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm,
    urlsafe_game_key=messages.StringField(1),)

USER_REQUEST = endpoints.ResourceContainer(
    user_name=messages.StringField(1),
    email=messages.StringField(2),)

USER_GAME_REQUEST = endpoints.ResourceContainer(
    user_name=messages.StringField(1))


@endpoints.api(name='tic_tac_toe', version='v1')
class TicTacToeApi(remote.Service):
    """Game API"""
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                    'A User with that name already exists!')
        user = User(name=request.user_name, email=request.email, wins=0)
        user.put()
        return StringMessage(message='User {} created!'.format(
                request.user_name))

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""
        user_o = User.query(User.name == request.user_o).get()
        user_x = User.query(User.name == request.user_x).get()

        if not (user_o and user_x):
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        try:

            game = Game.new_game(user_o.key, user_x.key)
        except ValueError:
            raise endpoints.BadRequestException('Maximum must be greater '
                                                'than minimum!')

        return game.to_form('Good luck playing Tic Tac Toe!')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            return game.to_form('Time to make a move!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Makes a move. Returns a game state with message"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if not game:
            raise endpoints.NotFoundException('Game not found!')

        if game.game_over:
            return game.to_form('Game already over!')

        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException('No such a user!')

        if user.key != game.next_move:
            raise endpoints.NotFoundException('It\'s not your turn!')

        game.attempts -= 1

        if game.attempts < 1:
            game.end_game(False, False)
            return game.to_form('Game over!')

        else:
            # check this user is o or x?
            o = True if user.key == game.user_o else False

            move = request.move
            
            game.score_board[move] = 'o' if o else "x"
            game.history.append(("o" if o else"x", move))

            game.put()
            msg = 'continue!'
            return game.to_form(msg)

    @endpoints.method(response_message=ScoreForms,
                      path='scores',
                      name='get_scores',
                      http_method='GET')
    def get_scores(self, request):
        """Return all scores"""
        scores = Score.query()
        return ScoreForms(items=[score.to_form() for score in scores])


    @endpoints.method(request_message=USER_REQUEST,
                      response_message=ScoreForms,
                      path='scores/user/{user_name}',
                      name='get_user_scores',
                      http_method='GET')
    def get_user_scores(self, request):
        """Returns all of an individual User's scores"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')

        scores = Score.query(Score.user == user.key)
        return ScoreForms(items=[score.to_form() for score in scores])


    @endpoints.method(request_message=USER_GAME_REQUEST,
                      response_message=GameForms,
                      path='game/user/{user_name}',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """
        Return all of a user's active games
        """
        user = User.query(User.name == request.user_name).get()
        if not user:

            raise endpoints.NotFoundException('A User with that name does not exist!')

        games = Game.query(ndb.OR(Game.user_o == user.key,
                                  Game.user_x == user.key)).\
                filter(Game.game_over == False)

        games = Game.query()

        if not games:
            raise endpoints.NotFoundException('You have no active game!')

        return GameForms(items=[game.to_form("Here are all active game you have!") 
                          for game in games])


    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path="game/{urlsafe_game_key}/cancel_game",
                      name="cancel_game",
                      http_method='GET')
    def cancel_game(self, request):
        """Cancel a game in progres"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game.game_over:
            return game.to_form('Game already over!')
        else:
            game.history.append(("over!", "cancelled!"))
            game.cancel_game()
            return game.to_form('Game logically deleted!')


    @endpoints.method(response_message=UserForms,
                      path='user/ranking',
                      name="get_user_rankings",
                      http_method="GET")
    def get_user_rankings(self, request):
        """Return all users ranked by wins"""
        users = User.query().order(-User.wins).fetch()
        if not users:
            raise endpoints.NotFoundException('You have no game!')
        return UserForms(items=[user.to_form() for user in users])


    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=StringMessage,
                      path="game/{urlsafe_game_key}/history",
                      name="get_game_history",
                      http_method='GET')
    def get_game_history(self, request):
        """Get all moves from the game."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if not game:
            raise endpoints.NotFoundException('game does not exist!')
        
        if game.history:
          return StringMessage(message=str(game.history))
        else:
          return StringMessage(message="game haven't started!")


api = endpoints.api_server([TicTacToeApi])