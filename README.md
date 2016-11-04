#Tic Tac Toe score keeper

## Set-Up Instructions:
1.  Update the value of application in app.yaml to the app ID you have registered
 in the App Engine admin console and would like to use to host your instance of this sample.

1.  Run the app with the devserver using dev_appserver.py DIR, and ensure it's
 running by visiting the API Explorer - by default ```localhost:8080/_ah/api/explorer```.

##Game Description:
Tic tac toe is a simple 2 players game. 
The board has 9 squares. 3*3 matrix form.

given time. Each game can be retrieved or played by using the path parameter
`urlsafe_game_key`.

##Rules:
Each player populate "o" or "x" into the square of 3x3 board alternatively. and the user had 3 squares of "o" or "x" in a row win the game. 
new game always starts with user_o's move.
and "next_turn" property specify the user who is going to play next move.
When the board get full without a winner, then the game ended in a tie.


##How to start playing?
1. Create a new user, using the ```create_user``` endpoint.
1. Use ```create_game``` to create a game. There are two forms ```user_o``` and ```user_x``` to fill you and the other player's name. Remember to copy the```urlsafe_key``` property for later use.
1. use ```make_move``` to implement population of your move. you need ```urlsafe_key``` to let the program know which game are you playing, and fill ```move``` form with a number of square you want to populate. It returns a result as json data.


##Score keeping:
Score is created when a game end.
You can get information of the result such as winner, the players who played the game, and date.
if there are no winner. it means the game ended in a tie.


##Files Included:
 - api.py: Contains endpoints and game playing logic.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue handler.
 - models.py: Entity and message definitions including helper methods.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.
 - Design.txt: Design decisions and records.

##Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email (optional)
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will 
    raise a ConflictException if a User with that user_name already exists.
    
 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: user_name, attempts
    - Returns: GameForm with initial game state.
    - Description: Creates a new Game. user_name provided must correspond to an
    existing user - will raise a NotFoundException if not.
     
 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Returns the current state of a game.
    
 - **make_move**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key
    - Returns: GameForm with new game state.
    - Description: Accepts a won flag and returns the updated state of the game.
    If this causes a game to end, a corresponding Score entity will be created.
    
 - **get_scores**
    - Path: 'scores'
    - Method: GET
    - Parameters: None
    - Returns: ScoreForms.
    - Description: Returns all Scores in the database (unordered).
    
 - **get_user_scores**
    - Path: 'scores/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: ScoreForms. 
    - Description: Returns all Scores recorded by the provided player (unordered).
    Will raise a NotFoundException if the User does not exist.
    
 - **get_active_game_count**
    - Path: 'games/active'
    - Method: GET
    - Parameters: None
    - Returns: StringMessage
    - Description: Gets the average number of attempts remaining for all games
    from a previously cached memcache key.

 - **get_user_games**
    - Path: 'game/user/{user_name}'
    - Method: GET
    - Parameters: None
    - Returns: GameForms
    - Description: Return all of a user's active games.

 - **cancel_game**
    - Path: 'game/{urlsafe_game_key}/cancel_game'
    - Method: PUT
    - Parameters: None
    - Returns: GameForm
    - Description: Cancel a game in progres.

 - **get_user_rankings**
    - Path: 'user/ranking'
    - Method: GET
    - Parameters: None
    - Returns: UserForms
    - Description: Return all users ranked by wins.

 - **get_game_history**
    - Path: 'game/{urlsafe_game_key}/history'
    - Method: GET
    - Parameters: None
    - Returns: StringMessage
    - Description: Get all moves from the game.

##Models Included:
 - **User**
    - Stores unique user_name and (optional) email address.
    
 - **Game**
    - Stores unique game states. Associated with User model via KeyProperty.
    
 - **Score**
    - Records completed games. Associated with Users model via KeyProperty.
    
##Forms Included:
 - **GameForm**
    - Representation of a Game's state (urlsafe_key, attempts_remaining,
    game_over flag, message, user_name).

 - **GameForms**
    - Multiple GameForm container

 - **NewGameForm**
    - Used to create a new game (user_name, min, max, attempts)

 - **MakeMoveForm**
    - Inbound make move form.

 - **ScoreForm**
    - Representation of a completed game's Score (user_name, date, won flag).

 - **ScoreForms**
    - Multiple ScoreForm container.

 - **StringMessage**
    - General purpose String container.

 - **UserForm**
     - inbound user's information.

 - **UserForms**
     - Multiple UserForm container
