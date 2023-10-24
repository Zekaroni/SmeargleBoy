from pyboy import PyBoy

pyboy = PyBoy('game.gb')
while not pyboy.tick():
    pyboy.screen_image()
    input()

pyboy.stop()