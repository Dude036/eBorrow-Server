# Networking Protocols

Below are listed the structure of packets sent and recieved for this server.

## Packet structures

Each packet sent to the database will be either interpretted or piped. Each packet sent will recieve a reply with a code. These codes and structures are listed below.

### Base Structure

The Header and the Packet are separated by the space character, " ". At the end of every packet, attach the terminator byte string, "0x7FFF7FFF". Not having this at the end of your transmission, will be interpretted as an incomplete transmission, and will be ignored.

### Server Received Command Structure

Every header follows a similar structure of having the username and the packet identifier. This allows for expandable transmission protocols to be made. The range of which is specified in the following sections.

#### Interpreted Commands

These are interpreted commands that edits the database in some manner or form. Therefore, they are slower in execution. These command packet identifiers range from any number between 0 and 99.

* Create New User

		Header:
			@username:0
		Packet:
			{"private": Private_key, "public":Public_key}

* Delete Existing User

		Header:
			@username:1
		Packet:
			{"Delete": 1, "public":Public_key, "private":Private_key}

* Remove an item from the database

		Header:
			@username:2
		Packet:
			{"Key":[SHA_256 Hash of item], "private":Private_key}

**NOTE**: The Key should be a list of items to remove. This can be a list of any size.

* Add an item to database
	
		Header:
			@username:3
		Packet:
			{"SHA_256 Hash of item":{json data}, "private":Private_key}


**NOTE**: This can be used to retrieve many items from the database, simply add more key, value pairs to the json object. There need only be one "private" key.


* Send All Data

		Header:
			@username:4
		Packet:
			{"public":Public_key}

* Send Specific Data

		Header:
			@username:5
		Packet:
			{"SHA_256 Hash of item": 1, "public":Public_key}

* Item Current Ownership Update

		Header:
			@username:6
		Packet:
            {
                "SHA_256 Hash of item": 1, 
                "New Owner": "friend_username",
                "public": "Friends_Public_key",
                "private": "Username_Private_key",
                "Schedule": {
                    "In": [Day, Month, Year],
                    "Out": [Day, Month, Year],
                }
            }

**NOTE**: This is the creation of an exchange item. This will be modified at runtime according to their owners databases. I.e. the Current Owner of the item will be separate from the Permanent owner until the specified out schedule in the Permanent owner's database. 

* Send Messages

		Header:
			@your_username:7
		Packet:
			{"Messages": 1, "private":Private_key}

* Send Exchanges

		Header:
			@your_username:8
		Packet:
			{"Exchanges": 1, "private":Private_key}

#### Piped Commands

These commands are only read by the server, and are stored in a buffer. Whenever the target user connects with the database, the command is then sent. All piped commands have a packet identifier between 100 and 199.

* Aquisition (Exchange) Request
	
		Header:
			@username:100
		Packet:
			{
			    "SHA_256 Hash of item": 1,
			    "Borrower": {
			        "Public": "Public_key",
			        "Username": "your_username",
			    }
			    "Lender": {
			        "Public": "Public_key",
			        "Username": "friends_username",
			    }
			 }

* Friend Request

		Header:
			@your_username:101
		Packet:
			{"Target": "friends_username"}
			
			
* Add Friend

        Header:
            @your_username:102
        Packet:
            {
                "Target": "friends_username"
                "Key": Your_Public_key
            }

* Delete Friend
    
		Header:
			@your_username:103
		Packet:
			{"Target": "friends_username"}


### Server Transmit Command Structure

These are commands that are sent, per request from a user, to the connected IP address. All commands following this structure have an identifier between 200 and 299. 

**NOTE**: These commands will send a multiple of objects, if requested.

* Return Item(s):		

		Header:
			@username:200
		Packet:
			{"SHA_256 Hash of item":{json data}, "SHA_256 Hash of item":{json data}, ... }


* Return Message(s):

		Header:
			@username:201
		Packet:
			["Message", "Message", ... ]


* Return Exchange(s):		

		Header:
			@username:202
		Packet:
			[{Exchange Object}, {Exchange Object}, ... ]

### Database Item Stucture

This is how items are saved in the database, and if you want to write your own json object item, this is how you do it. The SHA-256 key is validated from the Category, Subcategory, the Permanent Owner and the Name of the item. *These items cannot be changed. The hash is determined from this, and will result in a null reference if you do.*

    {
        "SHA-256 Hash of Permanent Fields": {
		"Category": "This can be of any spcificed Category",
		"Subcategory": "A subtype for further sorting",
		"Permantent Owner": "User name of the owner",
		"Name": "The name of the item",
		"Image": "A hyperlink to an image"
		"Current Owner": "Who owns this item presently"
		"Type Info": {
			"Id": "An identifier specified by the subcategory. For instance, an ISBN for a book, or a UPC for a Board game"
			"This dictionary varies between the subcatagory and a category"
		}
	    }
    }


The Type Info varies based on the category and the sub category. So far, we've implimented three different structures, all under the Entertainment Category.

### Entertainment

#### TV and Movies

    {
        "Cast": ['The cast list'],
        "Day": "Day of release",
        "Month": "Month of Release,
        "Year": "Year of Release",
        "Genres": ["Specified list of genres", "These can be altered per the user's request"],
        "Rating": "The Age rating. i.e. G, PG, PG-13, R",
        "Id": "The IMDB code to auto fill the above"
    }

#### Game

    {
        "Day": "Day of release",
        "Month": "Month of Release,
        "Year": "Year of Release",
        "Platform": "Board game, Card game, or Video game",
        "Publisher": "What company or person published this.",
        "Rating": "Game Age rating. i.e. [E, E10+, T, M, AO, EC] for Video Games.",
        "Genres": ["Specified list of genres", "These can be altered per the user's request"],
        "Id": "The UPC code to auto fill the above fields"
    }

#### Book

    {
        "Authors": ["A List of Authors of the Book", "Can have many"],
        "Edition": "The Released edition",
        "Genres": ["Specified list of genres", "These can be altered per the user's request"],
        "Day": "Day of release",
        "Month": "Month of Release,
        "Year": "Year of Release",
        "Id": "The ISBN code to auto fill the above fields"
    }


## Server Return Codes:

*These are still be actively worked on and implimented*

0. No error, Successful Execution

1. Invalid Packet Format

	This usually means the you structured your packet wrong on a high level
	
	i.e.: Missing parenthesis, No space between Header and Packet, Incorrect Json format

2. Invalid Header ID

	Header ID out of range or not used

3. User Key Not Found

	The key the user is using, is not found in the database

4. Invalid User Public Key

	The hash of the public key didn't validate. Cannot proceed

5. Invalid User Private Key

	The hash of the private key didn't validate. Cannot proceed

6. Invalid Header Format

	Header has an invalid format

7. Invalid Packet Format

	Packet has an invalid format

8. Unspecified Deletion Key

	Tried to delete something that doesn't exist.

	This may be due to an error while updating

9. Key not found in User Database

	Unable to find the key in the database

10. Incorrect Key hash

	The checked hash doesn't match the hash given

11. Missing Private Key

	Lacking a Private Key

12. Missing Public Key

	Lacking a Private Key

13. Illegal Character

	You tried to write a character not in the UTF-8 Character set. Cannot write it

14. Unable to Write to Database

	There was an error in writing your database. Please try again.

15. Unable to Read Database

	There was an error in reading your database. Please try again.

16. Username already exists

17. Username not found

18. Unterminated Transmission Buffer Received

	You sent a packet without terminating. Timed out.

99. Unknown Error Occurred. Unable to resolve error

	Something happened. I have no idea what. I can't solve this.

### Error Code Packet Protocol

	Header:
		!Error:Id
	Packet:
		{"Description": "The Description Information (see above)"}
