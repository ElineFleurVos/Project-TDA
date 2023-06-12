from pygame import Vector2


class Camera:
    center = Vector2(39.9604, 116.3124)
    zoom = 8000
    screen_size: Vector2


camera: Camera
window: any
