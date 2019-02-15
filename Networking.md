# Networking Protocols

Below are listed the structure of packets sent and recieved for this server.

## Packet structures

Each packet sent to the database will be either interpretted or piped. Each packet sent will recieve a reply with a code. These code and structured are listed below.

### Base Structure

The Header and the Packet are separated by the space character, " ". Since we are using AES encryption keys, "||" will be used as the delimiter to prevent key mismatch and key separation. 

### Server Received Command Structure

Every header follows a similar structure of having the username and the packet identifier. This allows for expandable transmission protocols to be made. The range of which is specified in the following sections.

#### Interpreted Commands

These are interpreted commands that edits the database in some manner or form. Therefore, they are slower in execution. These commands packet identifier range from an number between 0 and 99.

* Create New User

		Header:
			@username:0:
		Packet:
			{"Private": Private_key, "Public":Public_key}

* Delete Existing User

		Header:
			@username:1:Private_key
		Packet:
			{"Delete": 1, "Public":Public_key}

* Remove an item from the database

		Header:
			@username:2:Private_key
		Packet:
			<SHA_256 Hash of item>

* Add an item to database
	
		Header:
			@username:3:Private_key
		Packet:
			<SHA_256 Hash of item>{json data}

* Send All Data

		Header:
			@username:4:Public_key
		Packet:
			{"Library": 1, "IP": "User's IP address"}

* Send Specific Data

		Header:
			@username:5:Public_key
		Packet:
			{"SHA_256 Hash of item": 1, "IP": "User's IP address"}

* Item Current Ownership Update
	
		Header:
			@username:6:Private_key
		Packet
			<SHA_256 Hash of item>{"New Owner": "friend_username", "Public Key": "Friends_public_key}


#### Piped Commands

These commands are only read by the server, and are stored in a buffer. Whenever the target user connects with the database, the command is then sent. All piped commands have a packet identifier between 100 and 199.

* Acquisition Request
	
		Header:
			@username:100:Private_key||@friend_username:Public_key||
		Packet:
			{json data}

* Add \ Confirm Friend

		Header:
			@personal_username:101:Personal_private_key
		Packet:
			[@friendly_username:Personal_Public_key||]



### Server Transmit Command Structure

These are commands that are sent, per request from a user, to the connected IP address. All commands following this structure have an identifier between 200 and 299. 

* Send Item:		

		Header:
			@username:200:Private_key
		Packet:
			<SHA_256 Hash of item>{json data}


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

0. No error. Successful Execution

1. Invalid Packet Format

	This usually means the you structured your packet wrong on a high level
	
	i.e.: Missing parenthesis, No space between Header and Packet, Incorrect Json format

2. Invalid Packet ID

	The Packet that you sent was not recognized as a valid packet.
	
	i.e.: Wrong Key words and Identifiers

3. Invalid User Key

	The key the user is using, is not found in the database

