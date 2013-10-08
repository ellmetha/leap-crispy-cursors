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
	CURSOR_CHOICES = {
		'path': CrispyPathCursor,
		'pitch': CrispyPitchCursor,
	}

	def __init__(self, parsed_args, *args, **kwargs):
		self.parsed_args = parsed_args
		
		# Create a Leap controller and a listener
		self.controller = Controller()
		self.listener = self.CURSOR_CHOICES[self.parsed_args.mode]()

		self.listener.click_timeout = self.parsed_args.click
		self.listener.press_timeout = self.parsed_args.press

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
	# Specify the available options
	parser.add_argument('-m', '--mode', type=str,
		choices=LeapCrispyCursor.CURSOR_CHOICES,
		default='path',
		help='cursor mode -- \'path\' forces cursor to follow hand and fingers movements ; \'pitch\' forces cursor to follow hand pitch/roll/yaw'
	)
	parser.add_argument('-c', '--click', type=int,
		default=CrispyPathCursor.click_timeout,
		help='set the amount of time after which a click event is generared (ms)'
	)
	parser.add_argument('-p', '--press', type=int,
		default=CrispyPathCursor.click_timeout,
		help='set the amount of time after which a press event is generared (ms)'
	)

	# Parse args!
	args = parser.parse_args()

	# Run the crispy cursor
	crispy_cursor = LeapCrispyCursor(args)
	crispy_cursor.run()

if __name__ == "__main__":
	main()