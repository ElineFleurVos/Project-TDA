from pygame import Vector2
# Vectors are (long, -lat)

class Camera:
    center = Vector2(116.3124, -39.9604)
    zoom = 8000
    screen_size: Vector2


camera: Camera
window: any
