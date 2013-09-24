# -*- coding: utf-8 -*-

# Standard library imports
# Third party imports

# Local application / specific library imports
from . import BaseCursorListener


class CrispyPitchCursor(BaseCursorListener):
	"""
	Handles movements by using hand pitch, roll and yaw.
	"""
	# Multipliers on roll and pitch
	roll_mult = 4
	pitch_mult = 4

	def __init__(self, *args, **kwargs):
		super(CrispyPitchCursor, self).__init__(*args, **kwargs)
		if 'roll_mult' in kwargs:
			self.roll_mult = kwargs['roll_mult']
		if 'pitch_mult' in kwargs:
			self.pitch_mult = kwargs['pitch_mult']

	def update(self, frame, data):
		# Get the required data
		hand_state = data['leap_state']['current']
		hand_state_prev = data['leap_state']['current']

		if hand_state.av_numhands >= 0.5:
			# Compute X and Y offset from roll, pitch and yaw values
			x_offset = (-hand_state.av_roll - hand_state.av_yaw) * self.roll_mult
			y_offset = hand_state.av_pitch * self.pitch_mult

			# Move it!
			self.move(x_offset, y_offset)

			if data['actions']['click']:
				self.click()
