from datetime import timedelta

from pygame import Vector2

window_start_size = Vector2(1920, 1080)
analysis_time_slot_start_time = timedelta(hours=11, minutes=0)
analysis_time_slot_end_time = timedelta(hours=13, minutes=0)
analysis_time_slot_interval = timedelta(minutes=5)
analysis_time_slot_interval_padding = timedelta(minutes=5)

# these values are in long/lat degrees.
alpha_complex_filtration_value = .000002
max_distance_between_datapoints = .01
refilter_data: bool = True
