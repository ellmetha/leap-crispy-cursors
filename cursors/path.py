# -*- coding: utf-8 -*-

# Standard library imports
import math

# Third party imports
from Leap import Vector

# Local application / specific library imports
from . import BaseCursorListener
from . import NaN


class CrispyPathCursor(BaseCursorListener):
	"""
	Handles movements by using hand trajectory in the Leap plane.
	"""
	# Palm velocity faster than this is ignored (in mm/s)
	max_vel = 2000
	# Pause movement when fingers changes (in ms)
	finger_pause = 100
	# After this long, the next frames sets are ignored (in ms)
	max_elapsed = 1000

	def __init__(self, *args, **kwargs):
		super(CrispyPathCursor, self).__init__(*args, **kwargs)
		self.last_change = 0

	def update(self, frame, data):
		# Get the required data
		hand_state = data['leap_state']['current']
		hand_state_prev = data['leap_state']['prev']

		elapsed = NaN # (s)
		d_av_tip_pos = Vector(NaN, NaN, NaN) # (mm)
		velocity = NaN # (mm/s)
		try:
			# Computes some differences between the current and previous frames sets
			d_av_fingers = hand_state.av_fingers - hand_state_prev.av_fingers
			d_av_tip_pos = hand_state.av_tip_pos - hand_state_prev.av_tip_pos
			d_av_palm_pos = hand_state.av_palm_pos - hand_state_prev.av_palm_pos
			# Computes the elapsed time between the current and previous frames sets
			elapsed = max(0.000001, hand_state.ts - hand_state_prev.ts)
			# Computes velocity and acceleration
			velocity = d_av_tip_pos.magnitude / elapsed
		except:
			pass

		if not math.isnan(velocity) and elapsed <= (self.max_elapsed / 1000) and velocity <= self.max_vel:
			if d_av_fingers > 0:
				self.last_change = hand_state.ts
			if hand_state.ts - self.last_change < (self.finger_pause / 1000):
				d_av_tip_pos *= 0 # don't move pointer when #fingers changes

			if hand_state.av_numhands >= 0.5 and hand_state.av_fingers >= 1:
				# The cursor speed will be inversely proportional to the number of fingers detected by the controller
				d_av_tip_pos *= (1. / hand_state.av_fingers) * 2

				# Move it!
				self.move(d_av_tip_pos.x, -d_av_tip_pos.y)
		elif self.active_fist:
				# Move it!
				self.move(d_av_palm_pos.x, -d_av_palm_pos.y)

		if data['actions']['click']:
			self.click()
		if data['actions']['press']:
			self.press()
		if data['actions']['release']:
			self.release()
