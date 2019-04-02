import os

if __name__ == '__main__':
	inp = input("Are you sure you want to reset everything?\n\t(Y)es\n\t(N)o\n").lower()
	if inp == 'y':
		open('keys.db', 'w').write('{}')
		open('config.json', 'w').write('{\n\t"run": 1\n}')
		try:
			os.remove("db/username_1.json")
			os.remove("db/username_2.json")
		except FileNotFoundError as e:
			print("Test Usernames already removed")
		print("\n\nCompleted")
