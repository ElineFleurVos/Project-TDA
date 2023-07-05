from datetime import timedelta

from pygame import Vector2

window_start_size = Vector2(1920, 1080)
# analysis_time_slot_start_time = timedelta(hours=11, minutes=0)
analysis_time_slot_end_time = timedelta(hours=1, minutes=30)
analysis_time_slot_interval = timedelta(minutes=5)
analysis_time_slot_interval_padding = timedelta(minutes=3)

# these values are in long/lat degrees.
alpha_complex_filtration_value = .000006

#Vectors are in (lat, -long)
refilter_data: bool = True
filter_end_points: bool = False
max_distance_between_datapoints = .001
filter_left_top = Vector2(116.3042592145297, -39.99760917976811)
filter_right_bottom = Vector2(116.31635444177587, -39.985175353300555)

# campus??
# filter_left_top = Vector2(116.30675027472009, -39.97247810644602)
# filter_right_bottom = Vector2(116.32350518435274, -39.956727502363265)