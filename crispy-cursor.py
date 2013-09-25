# -*- coding: utf-8 -*-

# Standard library imports
import sys
import time

# Third party imports
import argparse
from Leap import Controller

# Local application / specific library imports
from cursors import CrispyPathCursor
from cursors import CrispyPitchCursor


class LeapCrispyCursor:
	def __init__(self, *args, **kwargs):
		# Create a Leap controller and a listener
		self.controller = Controller()
		self.listener = CrispyPathCursor()

	def run(self):
		self.controller.add_listener(self.listener)

		try:
			while True:
				time.sleep(1000)
		except KeyboardInterrupt:
			pass
		finally:
			self.controller.remove_listener(self.listener)


def main():
	"""
	Main function: parses args and run cursor.
	"""
	# Create the argument parser
	parser = argparse.ArgumentParser(
		description='Allow the Leap Motion to be used as a mouse device',
		epilog='Propulsed by ellmetha'
	)
	# Specify the logging output file option
	parser.add_argument('-l', '--log', type=str,
		help='log command output to a file instead of stdout'
	)


	# Parse args!
	args = parser.parse_args()

	# Run the crispy cursor
	crispy_cursor = LeapCrispyCursor(args)
	crispy_cursor.run()

if __name__ == "__main__":
	main()