# copy_apy.py
"""
Create and configure the Game API exposing the resources.
this can also contain game logic.
for more complex games it would be wise to 
move game logic to another file.
Ideally the API will be simple,
concerned primary with communication to/from API's users.
"""

import logging
import endpoints
from protrpc import remote, messages
from google.appengin.api import memcache
from google.appengin.api import taskqueue

from models import User, Game, Score
from models import StringMessage, NewGameForm, GameForm, MakeMoveForm,\
      ScoreForms

from utils import get_by_urlsafe

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
      urlsafe_game_key-messages.StringField(1),)
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
      MakeMoveForm,
      urlsafe_game_key=messages.StringField(1),)
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                            email=messages.StringField(2))
MEMCACHE_MOVES_REMAINING = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                                        email=messages.StringField(2))
MEMCACHE_MOVES_REMAINING  = 'MOCES_REMAINING'


@endpoints.api(name='guess_a_number', version='v1')
class GuessANumberApi(remote.Service):
    """Game API"""

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user'
                      http_method='POST')
    def create_user(self, request):
        """Create a user. requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                  'A user with that name already excist!')

        user = User(name=request.user_name, email=request.email)
        user = put()
        return StringMessage(message='User {} created!'.format(
                request.user_name))


    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      responce_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                  'A User with that name does not exist!')
        try:
            game = Game.new_game(user.key, request.min,
                                request.max, request.attempts)
        except ValueError:
            raise endpoints.BadRequestException('Maximum must be grater' 
                                                'than minimum!')

        # タスクキューを使って残りの試みの平均をアップデートする。
        # このオペレーションはNEWGAMEの作成が終わるまで待つ必要はない。
        # この一連作業とは別のものである。
        taskqueue.add(url='/task/cache_average_attempts')
        
        return game.to_form('Good luck playing guess a number!')


    @endpoints.method(request_message=GET_GAME_REQUEST,
                      responce_message=GameForm,
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
                      path="game/{urlsafe_game_key}",
                      name='maka_move',
                      http_method="PUT")
    def make_move(self, request):
        """Makes a move. return a game state with message"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game.game_over:
            return game.to_form('Game already over!')

        #のこりの数からマイナス１する
        game.attempts_remaining -= 1
        if request.guess == game.target:
            game.end_game(True)
            return game.to_form('You win!')

        if request.guess < game.target:
            msg = 'Too Low!'

        else:
            msg = 'Too High!'

        if game.attempts_remaining < 1:
            game.end_game(False)
            return game.to_form(msg + ' Game over!')
        else:
            game.put()
            return game.to_form(msg)

    @endpoints.method(response_message=ScoreForms,
                      path='scores',
                      name='get_scores',
                      http_method='GET')
    def get_scores(self, request):
        """Return all scores"""
        return ScoreForms(items=[score.to_form() for score in Score.query()])


    @endpoints.method(request_message=USER_REQUEST,
                      response_message=ScoreForms,
                      path='score/user/{user_name}',
                      name='get_user_scores',
                      http_method='GET')
    def get_user_scores(self, request):
        """Returns all of an indicidual User's scores"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'a User with that name does not exist!')

        score = Score.query(Score.user == user.key)
        return ScoreForms(items=[score.to_form() for score in scores.query()])


    @endpoints.method(response_message=StringMessage,
                      path='games/average_attempts',
                      name='get_average_attempts_remaining',
                      http_method='GET')
    def get_acerage_attempts(self, request):
        """Get the cached acerage moves remaining"""
        return StringMessage(message=memcache.get(MEMCACHE_MOVES_REMAINING) or '')


    @staticmethod
    def _cache_average_attempts():
        """Populates memcache with the average moves remaining of the game"""

      games = Game.query(Game.game_over == False).fetch()
      if games:
          count = len(games)
          total_attempts_remaining = sum([game.total_attempts_remaining
                                          for game in games])
          average = float(total_attempts_remaining)/count
          memcache.set(MEMCACHR_MOVES_REMINING,
                        'The acerage mocves remaining is {:.2f}'.format())


api = endpoints.api_server([GuessANumberApi])