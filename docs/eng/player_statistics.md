# I assume you checked example-code in README

***

If you checked source code, you could see the ``get_statistic_by_nickname`` signature. If you did not, dont worry, we will cover this arguments in this article.

There are multiple arguments, that we can pass in the method:
1. nickname - Nickname of user to find
2. mode - Game mode (Number from 0 to 4)
3. data - Unique ID of player(overwrites user nickname if not 0)
4. tank_id - staticID of tank to find for(Number 0 means overall stat for mode)
5. day - Filter stats by some date/battle count(Does not work because of site issues)

| Argument | type            | Description                                                                  |
|----------|-----------------|------------------------------------------------------------------------------|
| nickname | str             | Nickname of user to find                                                     |
| mode     | int or GameMode | Either GameMode enum instance or int in range from 0 to 4                    |
| player_id     | int             | Unique ID of player (overwrites user nickname if not 0)                      |
| tank_id  | int             | staticID of tank to find for(Number 0 means overall stat for mode)           |
| day      | int             | Filter stats by some date/battle count(Does not work because of site issues) |
***

## Performing request
### Game mode statistics

#### Using int as gamemode ID
Lets start with simple. As you could know, we have 4 main game modes: PvP, PvE, GLOPS and Ranked Battles. Each of them have their unique ID.


0 - **PvP**

1 - **PvE**

2 - **Lords of War(legacy mode)**

3 - **GLOPS**

4 - **Ranked Battles**

So, you just pass ID of game mode you want in method like this 
```python
from aw_api import API
import json
cookies = json.loads(open('cookies.json').read())
client = API(cookies) # Initialize client with cookies

# Return SomePlayer statistics in PvP
stats_using_int_as_gamemode_id = client.get_statistic_by_nickname('NicknameOfSomePlayer', mode=0)
```

, where `0` is your ID of PvP.


#### Using GameMode instance
First, you will need to import GameMode class itself
```python
from aw_api import GameMode, API
import json
cookies = json.loads(open('cookies.json').read())
client = API(cookies) # Initialize client with cookies

# Return SomePlayer statistics in PvP
stats_using_gamemode_class = client.get_statistic_by_nickname('NicknameOfSomePlayer', mode=GameMode.PVP)

```

### Player ID
If you know player ID but don't know his nickname, you can use his ID, instead of nick:
```python
from aw_api import GameMode, API
import json
cookies = json.loads(open('cookies.json').read())
client = API(cookies) # Initialize client with cookies

player_id_we_search_for = 234289348923 # ID of player you are looking for

# Return player statistics in PvP by ID
stats_using_gamemode_class = client.get_statistic_by_nickname('AnyStringYouWantToBeAPlaceholder', player_id=player_id_we_search_for)
```

, where player_id_we_search_for is ID of player you search for.

**BE AWARE that if you pass data keyword, API will ignore value at nickname argument and look for playerID instead**.

### Get statistics on specific tank
If you want to receive statistics on specific vehicle, than just pass it's ID. For example:
```python
from aw_api import GameMode, API
import json
cookies = json.loads(open('cookies.json').read())
client = API(cookies) # Initialize client with cookies

player_id_we_search_for = 234289348923 # ID of player you are looking for

# Return player statistics in PvP by ID
stats_using_gamemode_class = client.get_statistic_by_nickname('NicknameOfSomePlayer', tank_id=157)
```
will return your statistics on XM1A3.

_I cant give you list of IDs for all tanks now, but I may write an article how to extract them_


## Response data
``get_statistic_by_nickname`` returns ``PlayerStatistics`` dataclass which has several fields:

| Argument         | type  | Description                                                                                                |
|------------------|-------|------------------------------------------------------------------------------------------------------------|
| nickname         | str   | Proper spelling of player nickname                                                                         |
| winrate          | float | Represents winrate of player                                                                               |
| battles          | int   | How many battles have player played                                                                        |
| damage           | float | Average damage of player                                                                                   |
| clantag          | str   | Clantag of player. **Can be None**                                                                         |
| battalion_full   | str   | Full name of player battalion. **Can be None**                                                             |
| average_spotting | float | Damage given by player assist                                                                              |
| average_kills    | float | Average kills in battle                                                                                    |
| average_level    | float | Represents average level of player battles **Can be None** , **IT'S NOT WORKING PROPERLY DUE SITE-ISSUES** |

You can access this data using dictionary notation AND attribute notation, so ``stats.nickname`` will be equal to ``stats["nickname"]``


 