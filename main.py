from fb import RenderEngine
from pyboy import PyBoy, WindowEvent, logger

logger.log_level("DISABLE")

LAST_FRAME = bytearray(bytes(0))

def main():
    screen = RenderEngine()
    pyboy = PyBoy('game.gb', window_type="headless")
    pyboy.tick()
    screen.setupParams(pyboy.screen_image())
    
    while not pyboy.tick():
        screen.drawFrame(pyboy.screen_image())
        screen.updateFrameBuffer()
    pyboy.stop()

if __name__ == "__main__":
    main()