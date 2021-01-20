In addition to player statistics, API has several methods with battalions information.

They are almost useless due the fact that website does not give plenty of information. But we have what we have .

Let's start with two classes that can be returned from battalion methods.

### Classes

``BattalionMemberEntry`` - can be obtained from ``get_battalion_players`` method and contains 4 fields.

| Field        | Type | Description                              |
|--------------|------|------------------------------------------|
| nickname     | str  | Nickname of battalion member.            |
| role         | str  | Role of player in the battalion.         |
| battalion_id | int  | Unique ID of battalion player belongs to |
| id           | int  | Unique ID of player                      |

``BattalionSearchResultEntry`` - being returned from ``search_battalion`` method and contain only two fields.

| Field        | Type | Description                              |
|--------------|------|------------------------------------------|
| full_name     | str  | Full name of battalion.            |
| id         | int  | ID of battalion.         |


### Methods
#### Search for battalion by its name

If you want to retrive battalion players list, you can use ``get_battalion_players`` method of ``API`` class.

Example of usage below

```python
from aw_api import API
import json
cookies = json.loads(open('cookies.json').read())
client = API(cookies) # Initialize client with cookies

# Search for battalion with "mailru" in their name
battalion_with_mailru_in_name = client.search_battalion('mailru')
```
``battalion_with_mailru_in_name`` variable will contain list of all battalions that has Mailru in their battalion name.
The type of items in list is ``BattalionSearchResultEntry``

#### Get battalion players

**Warning: Due of some website issues, method won't return player members who has their account on Mycom**

You can get list of battalion players using ``get_battalion_players`` method:
```python
from aw_api import GameMode, API
import json
cookies = json.loads(open('cookies.json').read())
client = API(cookies) # Initialize client with cookies

# Get of battalion with battalion ID equal to 1
some_battalion_players = client.get_battalion_players(1)
```
``some_battalion_players`` will contain ``BattalionMemberEntry`` instances.