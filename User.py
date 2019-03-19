import simplejson as json
import os


class User(object):
    """User class
    This is the class to state what a user has attached to them.
    This includes Inventory, Messages, and Exchange information	"""

    def __init__(self, name, inventory=None, messages=None, exchange=None, json_data=None):
        """
        Basic Constructor
        :param name: a string for the username of the user
        :param inventory: a dictionary containing the user's inventory
        :param messages: a list of message objects that the user needs to read
        :param exchange: a list of basic item information for lent and borrowed objects
        :param json_data: a json object to be interpreted into a class object
        """
        self.Username = name
        if json_data is None:
            self.Inventory = inventory
            self.Messages = messages
            self.Exchange = exchange
        else:
            self.__read(json_data)
        if self.Inventory is None:
            self.Inventory = {}
        if self.Messages is None:
            self.Messages = []
        if self.Exchange is None:
            self.Exchange = []

    def __read(self, json_data):
        """
        A hidden copy constructor with a serialized json object
        :param json_data: json object to attribute back into a class object
        """
        if "Inventory" not in list(json_data.keys()):
            print("Missing 'Inventory' key")
        elif "Messages" not in list(json_data.keys()):
            print("Missing 'Messages' key")
        elif "Exchange" not in list(json_data.keys()):
            print("Missing 'Exchange' key")
        else:
            self.Inventory = json_data['Inventory']
            self.Messages = json_data['Messages']
            self.Exchange = json_data['Exchange']

    def serialize(self):
        """
        Serialize a class to a dictionary
        :return: a dictionary of the class variables
        """
        return self.__dict__

    def to_file(self):
        """
        Sends the database to a file
        """
        json.dump(self.serialize(), open(os.path.join('db', self.Username + '.json'), 'w'))

    def to_backup(self):
        """
        Sends the database to a file
        """
        json.dump(self.serialize(), open(os.path.join('backup', self.Username + '.json'), 'w'), indent=2)

    def add_to_inventory(self, lib_item):
        """ add_to_library()
        Adds an Item to a users database
        :param lib_item: dictionary item {Key, Value} to add to the inventory
        """
        for key, value in lib_item.items():
            self.Inventory.update({key: value})

    def remove_from_inventory(self, lib_key):
        """

        :param lib_key: an SHA 256 key to remove from the database
        """
        result = True
        try:
            self.Inventory.pop(lib_key)
        except KeyError as e:
            print("Item not in the database.")
            print(e)
            result = False
        finally:
            return result


if __name__ == '__main__':
    person_a = User('person_a', inventory={'key1': 1}, messages=['test'], exchange={})
    print(person_a.serialize())
    person_b = User('person_b', json_data=person_a.serialize())
    print(person_b.serialize())
    person_a.to_file()
