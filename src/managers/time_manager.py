import time

class Time:
    
    deltaTime = 0.0
    unscaledDeltaTime = 0.0
    fixedDeltaTime = 1.0 / 60
    unscaledFixedDeltaTime = 1.0 / 60

    time = 0.0
    unscaledTime = 0.0
    frameCount = 0
    timeScale = 1.0

    _last_frame_time = None

    @classmethod
    def start(cls):
        """Initialize timing values."""
        cls._last_frame_time = time.perf_counter()
        cls.time = 0.0
        cls.unscaledTime = 0.0
        cls.deltaTime = 0.0
        cls.unscaledDeltaTime = 0.0
        cls.frameCount = 0

    @classmethod
    def update(cls):
        """Update all timing values (called every frame)."""
        now = time.perf_counter()
        if cls._last_frame_time is None:
            cls._last_frame_time = now

        raw_dt = now - cls._last_frame_time
        cls._last_frame_time = now

        cls.unscaledDeltaTime = raw_dt
        cls.deltaTime = raw_dt * cls.timeScale

        cls.unscaledFixedDeltaTime = cls.fixedDeltaTime
        cls.frameCount += 1

        cls.unscaledTime += cls.unscaledDeltaTime
        cls.time += cls.deltaTime
