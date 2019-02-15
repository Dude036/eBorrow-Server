# Networking Protocols

##Packet structures

Each packet sent to the database will be saved and will reply with a code, to the user. Below is structured how to setup some protocol, and how to 

###Base Structure

The Header and the Packet are separated by the space character. Since come of our AES encryption keys, we use "||" as a delimiter to prevent key mismatch and separation between keys and other items in the packet

###Server Received Command Structure

Every command follows a similar structure, and allows for expandable transmission protocols. 

##### Interpreted Commands

These are interpreted commands that edits the database in some manner or form. Therefore, they are slower in execution.

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


##### Piped Commands

These commands are left alone by the server, and are simply sent whenever the specified user connects with the database.

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

These are commands that are sent, per request from a user, to the connected IP address. This is the acknowledgment to the handshake from the client.

* Send Item:		

		Header:
			@username:200:Private_key
		Packet:
			<SHA_256 Hash of item>{json data}


### Database Item Stucture
This is how items are saved in the database, and if you want to write your own json object item, this is how you do it. Ignore comments specified by "#"

    {
        "SHA-256 Hash of Permantent Fields": {
		"Category": "This can be of any spcificed Category",
		"Subcategory": "A subtype for further sorting",
		"Permantent Owner": "User name of the owner",
		"Name": "The name of the item",
		#
		# The above items are considered permanent.
		# Changing this will mean it will be rejected by the database, when it hashes those fields.
		#
   		"Image": "A hyperlink to an image"
		"Current Owner": "Who owns this item presently"
		"Type Info": {
			"Id": "An identifier specified by the subcategory. For instance, an ISBN for a book, or a UPC for a Board game"
			"This dictionary varies between the subcatagory and a category"
		}
	    }
    }


##Server Return Codes:
0. No error. Successful Execution

1. Invalid Packet Format

	This usually means the you structured your packet wrong on a high level
	
	i.e.: Missing parenthesis, No space between Header and Packet, Incorrect Json format

2. Invalid Packet ID

	The Packet that you sent was not recognized as a valid packet.
	
	i.e.: Wrong Key words and Identifiers

3. Invalid User Key

	The key the user is using, is not found in the database

