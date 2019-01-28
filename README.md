# eBorrow - Server

This project is an Inventory Catalog designed as a desktop application using Python 3. This README is designed to assist in running the server and understanding it's processes.

## Prerequisites

To install all requirements for this project, run the following command
```
pip install -r requirements.txt
```

## Getting Started

This repository contains the Server Application to be run headless. It is to be run completely autonomously. Backups and Running the application is up to the installer's discrestion.

## Networking

Coming Soon!

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
* **Caleb Lundquist** - Frontend/Networking
* **Tim Weber** - Backend/Networking/Security
* **Jordan Yates** - Frontend/GUI/Security

## License

This project is licensed under the GNU General Purpose License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Stephen Clyde - Professor 
