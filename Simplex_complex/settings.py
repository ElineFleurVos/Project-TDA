from datetime import timedelta

from pygame import Vector2

window_start_size = Vector2(1920, 1080)
# analysis_time_slot_start_time = timedelta(hours=11, minutes=0)
analysis_time_slot_end_time = timedelta(hours=1, minutes=0)
analysis_time_slot_interval = timedelta(minutes=3)
analysis_time_slot_interval_padding = timedelta(minutes=1)

# these values are in long/lat degrees.
alpha_complex_filtration_value = .00002
max_distance_between_datapoints = .01
refilter_data: bool = True

#Vectors are in (lat, -long)
filter_left_top = Vector2(116.30675027472009, -39.97247810644602)
filter_right_bottom = Vector2(116.32350518435274, -39.956727502363265)
