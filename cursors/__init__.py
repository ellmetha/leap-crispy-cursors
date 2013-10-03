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
			self.av_tip_pos = NaN
		# Calculates the hand's average palm position
		try:
			self.av_palm_pos = Vector(0, 0, 0)
			for fr in frames:
				self.av_palm_pos += fr.hands[0].palm_position
			self.av_palm_pos *= norm
		except:
			self.av_palm_pos = NaN
		# Check whether the hand is horizontal
		if self.av_numhands > 0.5:
			self.is_horizontal = 0
			self.is_vertical = 0
			if self.av_pitch > -10 and self.av_pitch < 20:
				self.is_horizontal = 1
			if self.av_pitch > 55 and self.av_pitch < 70:
				self.is_vertical = 1
			if self.av_pitch < -60 and self.av_pitch > -90:
				self.is_vertical = -1
		# Compute the hand's average palm velocity
		self.av_palm_vel = sum(fr.hands[0].palm_velocity[1] for fr in frames) * norm
		# Compute the hand's average fingers speed
		try:
			self.av_fingers_speed = 0
			for fr in frames:
				self.av_fingers_speed += sum(fg.tip_velocity[1] for fg in fr.hands[0].fingers) / len(fr.hands[0].fingers)
			self.av_fingers_speed *= norm
		except:
			self.av_fingers_speed = NaN


class BaseCursorListener(Listener):
	"""
	Defines generic callback functions in order to convert frame events into mouse actions.
	"""
	# After this amount of time, a click event is generared (ms)
	click_timeout = 600
	# After this amount of time, a press event is generared (ms)
	press_timeout = 600
	# Number of frames to average
	numframes = 10

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

		# Init timers
		self.click_dtstart = 0
		self.press_dtstart = 0

		# Init flags
		self.active_fist = False #Indicates if a clenched fist is considered
		self.press_requested = False # Indicates if a mouse press event is requested

	def is_clicking(self, data):
		"""
		Determines whether the mouse is clicking or not.
		The default behavior is to cause a click when the mouse position remains the same
		during a fixed amount of time. This value is given by the click_timeout attribute.
		"""
		# Get the required data
		hand_state = data['leap_state']['current']

		if self.previous_pos == data['pos']:
			current_time = time.time()
			elapsed_time = current_time - self.click_dtstart
			if (elapsed_time * 1000) >= self.click_timeout and hand_state.av_fingers >=4:
				self.click_dtstart = time.time()
				return True
		else:
			self.click_dtstart = time.time()
		return False

	def is_pressing(self, data):
		"""
		Determines whether the mouse is pressing or not.
		The default behavior is to cause a press action when no fingers are available (the hand
		is closed).
		"""
		# Get the required data
		hand_state = data['leap_state']['current']
		hand_state_prev = data['leap_state']['prev']

		current_time = time.time()
		elapsed_time = current_time - self.press_dtstart

		if hand_state.av_fingers <= 1.2:
			if hand_state.av_numhands == 1 and hand_state.is_horizontal and ((hand_state_prev.av_fingers >= 3 and hand_state.av_fingers <= 1.2)
					or (self.active_fist and hand_state.av_fingers < 1)):
				self.press_requested = True
			elif hand_state.av_numhands == 1 and hand_state.av_fingers <= 1.2 and self.press_requested == True and (elapsed_time * 1000) >= self.press_timeout:
				self.active_fist = True
				return True
		else:
			self.press_dtstart = time.time()
			self.press_requested = False
		return False

	def is_releasing(self, data):
		"""
		Determines whether the mouse is releasing or not.
		The default behabior is to cause a release action when the hand is not closed.
		"""
		# Get the required data
		hand_state = data['leap_state']['current']
		hand_state_prev = data['leap_state']['prev']

		if hand_state.av_fingers >= 2.5 and hand_state.av_palm_pos[2] < 0 and self.active_fist:
			self.active_fist = False
			self.want_press = False
			return True
		return False

	def is_scrolling_up(self, data):
		"""
		Determines whether the mouse is scrolling up or not.
		"""
		# Get the required data
		hand_state = data['leap_state']['current']

		if hand_state.av_fingers >= 4 and not self.active_fist:
			if hand_state.av_fingers_speed - hand_state.av_palm_vel < -150:
				repeats = abs(int(hand_state.av_fingers_speed / 50.))
				repeats = max(repeats, 0)
				repeats = min(repeats, 5)
				return repeats
		return False

	def is_scrolling_down(self, data):
		"""
		Determines whether the mouse is scrolling down or not.
		"""
		# Get the required data
		hand_state = data['leap_state']['current']

		if hand_state.av_fingers >= 4 and not self.active_fist:
			if hand_state.av_fingers_speed -hand_state.av_palm_vel > 150:
				repeats = abs(int(hand_state.av_fingers_speed / 50.))
				repeats = max(repeats, 0)
				repeats = min(repeats, 5)
				return repeats
		return False

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
		press = self.is_pressing(data)
		release = self.is_releasing(data)
		scroll_up = self.is_scrolling_up(data)
		scroll_down = self.is_scrolling_down(data)

		data.update({
			'actions': {
				'click': click,
				'press': press,
				'release': release,
				'scroll_up': scroll_up,
				'scroll_down': scroll_down,
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

	def press(self):
		"""
		Do a press at the current mouse position.
		"""
		# Get the mouse position
		current_pos = self.mouse.position()
		# Click!
		self.mouse.press(*current_pos)

	def release(self):
		"""
		Do a release at the current mouse position.
		"""
		# Get the mouse position
		current_pos = self.mouse.position()
		# Click!
		self.mouse.release(*current_pos)

	def scroll_up(self, repeats=0):
		"""
		Do a scroll up action.
		"""
		# Scroll!
		for irep in range(repeats):
			self.mouse.scroll(vertical=4)
			time.sleep(.1)

	def scroll_down(self, repeats=0):
		"""
		Do a scroll down action.
		"""
		# Scroll!
		for irep in range(repeats):
			self.mouse.scroll(vertical=-4)
			time.sleep(.1)


# Sub-packages imports
from path import *
from pitch import *