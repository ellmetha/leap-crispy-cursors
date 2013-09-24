# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports
from Leap import Vector

# Local application / specific library imports
from . import BaseCursorListener


class CrispyPathCursor(BaseCursorListener):
	"""
	Handles movements by using hand trajectory in the Leap plane.
	"""
	# Palm velocity faster than this is ignored (in mm/s)
	max_vel = 2000
	# Acceleration greater than this is ignored (in mm/s^2)
	max_accel = 100000
	# Pause movement when fingers changes (in ms)
	finger_pause = 100


	def __init__(self, *args, **kwargs):
		super(CrispyPathCursor, self).__init__(*args, **kwargs)

	def update(self, frame, data):
		# Get the required data
		hand_state = data['leap_state']['current']
		hand_state_prev = data['leap_state']['prev']

		# Computes some differences between the current and the previous frames
		d_av_fingers = hand_state.av_fingers - hand_state_prev.av_fingers
		d_av_tip_pos = Vector(*hand_state.av_tip_pos) - Vector(*hand_state_prev.av_tip_pos)
		# Compute velocity and acceleration
		self.move(d_av_tip_pos.x, -d_av_tip_pos.y)