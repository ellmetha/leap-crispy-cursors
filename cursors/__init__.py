# -*- coding: utf-8 -*-

# Standard library imports
import sys
import time

# Third party imports
from Leap import Listener
from Leap import Vector
from pymouse import PyMouse

# Local application / specific library imports
from utils import Colors
from utils import showmessage
from utils import Status


NaN = float('NaN')


class CursorState:
	"""
	Store some information about the current and previous states of the frames used to
	handle cursor movements.
	"""

	def __init__(self, frames, numframes, *args, **kwargs):
		norm = 1. / numframes

		self.ts = frames[0].timestamp / 1000000.0
		self.av_numhands = sum(len(fr.hands) for fr in frames) * norm
		# Calculates the hand's average pitch, roll and yaw
		self.av_pitch = sum(fr.hands[0].direction.pitch for fr in frames) * norm
		self.av_roll = sum(fr.hands[0].palm_normal.roll for fr in frames) * norm
		self.av_yaw = sum(fr.hands[0].direction.yaw for fr in frames) * norm
		# Calculates the average number of fingers
		self.av_fingers = sum(len(fr.hands[0].fingers) for fr in frames) * norm
		# Calculates the hand's average finger tip position
		try:
			self.av_tip_pos = Vector(0, 0, 0)
			for fr in frames:
				self.av_tip_pos += sum((fg.tip_position for fg in fr.hands[0].fingers), Vector()) / len(fr.hands[0].fingers)
			self.av_tip_pos *= norm
		except:
			raise
			self.av_tip_pos = NaN


class BaseCursorListener(Listener):
	"""
	Defines generic callback functions in order to convert frame events into mouse actions.
	"""
	click_timeout = 1000
	numframes = 10 # Number of frames to average

	def __init__(self, *args, **kwargs):
		super(BaseCursorListener, self).__init__(*args, **kwargs)

		# The following sets are maintained to determine the actions to be performed from
		# the average values fetched from the last 10 frames
		self.frames_set = list()
		self.previousframes_set = list()

		# Fetch a given mouse object or instanciate it if necessary
		if 'mouse' in kwargs and isinstance(kwargs['mouse'], PyMouse):
			self.mouse = kwargs['mouse']
		else:
			self.mouse = PyMouse()

		# Init mouse position tracking
		self.previous_pos = self.mouse.position()
		self.fixed_dtstart = 0

	def is_clicking(self, data):
		"""
		Determines whether the mouse is clicking or not.
		The default behavior is to cause a click when the mouse position remains the same
		during a fixed amount of time. This value is given by the click_timeout attribute.
		"""
		if self.previous_pos == data['pos']:
			current_time = time.time()
			elapsed_time = current_time - self.fixed_dtstart
			if (elapsed_time * 1000) >= self.click_timeout:
				self.fixed_dtstart = time.time()
				return True
		else:
			self.fixed_dtstart = time.time()
		return False

	def is_claw(self, pos):
		pass

	def on_init(self, controller):
		# Force the listener to stop if therse is no controller and no leapd daemon launched
		showmessage("Initializing listener", Status.RUNNING, Colors.BLUE)
		i_try = 0
		while not controller.frame(2*self.numframes).is_valid:
			i_try += 1
			if i_try >= 1e6:
				showmessage("Initializing listener", Status.ERROR, Colors.RED, update=True)
				sys.exit(1)
		showmessage("Initializing listener", Status.SUCCESS, Colors.GREEN, update=True)

		# Fill the frames and previousframes lists with the first available frames
		for i_frame in range(self.numframes):
			self.frames_set.append(controller.frame(i_frame))
			self.previousframes_set.append(controller.frame(self.numframes + i_frame))

	def on_connect(self, controller):
		showmessage("Initializing listener", Status.SUCCESS, Colors.GREEN, update=True, newline=True)

	def on_disconnect(self, controller):
		print("Disconnected")

	def on_exit(self, controller):
		print("Exit")

	def on_frame(self, controller):
		# Get the most recent frame
		latest_frame = controller.frame()
		
		# Update the frames sets
		self.previousframes_set.pop(0)
		self.previousframes_set.append(self.frames_set[0])
		self.frames_set.pop(0)
		self.frames_set.append(latest_frame)

		data = dict()

		# Fetch some usefull information
		pos = self.mouse.position()
		current_state = CursorState(self.frames_set, self.numframes)
		previous_state = CursorState(self.previousframes_set, self.numframes)

		data.update({
			'pos': pos,
			'leap_state': {
				'current': current_state,
				'prev': previous_state,
			}
		})

		# Determine what is going on above the Leap
		click = self.is_clicking(data)

		data.update({
			'actions': {
				'click': click,
			}
		})

		# Update the previous mouse position
		self.previous_pos = pos

		self.update(latest_frame, data)

	def update(self, frame, data):
		"""
		Translates frames dispatched by the Leap Motion to mouse events.
		"""
		raise NotImplementedError

	def move(self, x, y):
		"""
		Moves the mouse by using x and y pixels offsets.
		"""
		# Get the mouse position
		current_x, current_y = self.mouse.position()
		# Move!
		self.mouse.move(current_x + round(x), current_y + round(y))

	def click(self):
		"""
		Do a click at the current mouse position.
		"""
		# Get the mouse position
		current_pos = self.mouse.position()
		# Click!
		self.mouse.click(*current_pos)


# Sub-packages imports
from path import *
from pitch import *