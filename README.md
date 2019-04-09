# eBorrow - Server

This project is an Inventory Catalog designed as a desktop application using Python 3. This README is designed to assist in running the server and understanding it's processes.

## Prerequisites

We are using Python 3.6+ for this project, with pip 9.0.0+. To install all pip requirements for this project, run the following command
```
pip install -r requirements.txt
```

Windows Users: pip may ask for admin priviledges, which you can do as well. If you choose to not do that, you can use the argument "--user" to install all the libraries for just your user. This seems to work.


## Getting Started

This repository contains the Server Application to be run headless. It is to be run completely autonomously. Backups and Running the application is up to the installer's discrestion.

For setup, I assume you will have a basic knowledge of local IP Addresses, port forwarding/triggering, and basic Network savvy. For the server to have access to the outside network, you will have to modify a few things. In networking.py, you may specify a different port if you like, but the IP address that you should use is the Local IP address assosciated with the device running the program. This is most likely a device IP address in the range of 192.168.XXX.XXX. I found it by knowing which port the computer uses to connect to the outside network.

To begin the application, run the following command.
```
python main.py
```

This will intiate the server. You can see the logs in out.log, which should give all the information as to what is happening in the server.

To quit execution of the server, swap the '1' in config.json to a '0'. The server will terminate in no more than 30 seconds. To ensure that the server is terminated, out.log will specify that all tasks have been terminated.

## Networking / Netcode

See [Networking](Networking.md)

### Coding Style

This project follows [PEP 8](https://www.python.org/dev/peps/pep-0008/) standards and uses the [autopep8](https://github.com/hhatto/autopep8) library for style verification. To automatically modify your code to align with PEP 8 standards, run the following command:

This runs a verbose call to autopep8 for all Python files in the folder to fix all the styling errors.

```
autopep8 -v -i *.py
```
Run this command before every push.

## Contributing & Versioning

We use GitHub's versioning system. The *master* branch is to remain untouched until a full release is planned. The *dev* branch is meant for semi-active development. When there is a feature to be added, follow this checklist:

1. Checkout the *dev* branch
2. Make a new branch, naming it according to the issue/feature
3. Complete the task
4. Modify or write applicable unit tests
5. Run all unit tests
6. Start merge **into** the *dev* branch
7. Run all unit tests
8. Fix merge conflicts
9. Repeat steps 7 and 8 until it meets the requirements definition
10. Run styling script
11. Submit Final Pull request for review

## Authors (sorted alphabetically)

* **Joshua Higham** - Backend/Networking/Security/Database
* **Caleb Lundquist** - Frontend/User Interface
* **Tim Weber** - Backend/Networking/Security
* **Jordan Yates** - Frontend/Networking/Security

## License

This project is licensed under the GNU General Purpose License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Stephen Clyde - Professor 
