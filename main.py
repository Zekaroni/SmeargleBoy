from fb import RenderEngine
from pyboy import PyBoy, WindowEvent, logger
import time

logger.log_level("DISABLE")

def main():
    screen = RenderEngine()
    pyboy = PyBoy('game.gb', window_type="headless")
    pyboy.tick()
    screen.setupParams(pyboy.screen_image())

    frame_count = 0
    start_time = time.time()

    while not pyboy.tick():
        screen.drawFrame(pyboy.screen_image())
        screen.updateFrameBuffer()
        frame_count += 1
        if time.time() - start_time >= 1.0:
            fps = frame_count / (time.time() - start_time)
            print(f"FPS: {fps:.2f}\r", end="")
            frame_count = 0
            start_time = time.time()

    pyboy.stop()

if __name__ == "__main__":
    main()
