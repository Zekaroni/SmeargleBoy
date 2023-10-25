from PIL import Image

class RenderEngine:
    def __init__(self):
        with open('/sys/class/graphics/fb0/virtual_size') as size_file:
            self.WIDTH, self.HEIGHT = [int(i) for i in size_file.read().split(',')]
        size_file.close()
        del size_file
        with open('/sys/class/graphics/fb0/bits_per_pixel') as bits_file:
            self.BYTES_PER_PIXEL = int(bits_file.read()) // 8
        bits_file.close()
        del bits_file
        self.SYS_VIDEO_BUFFER = open("/dev/fb0","r+b")
        self.LOCAL_BUFFER = self.SYS_VIDEO_BUFFER.read()
        self.LOCAL_QUEUE = {}

        self.CURRENT_FRAME = {}
        self.FRAME_HEIGHT = 0
        self.FRAME_WIDTH = 0
        self.CURRENT_PIXELS = {}
    
    def getPosition(self, x:int, y:int) -> int:
        return (y * self.WIDTH + x) * self.BYTES_PER_PIXEL

    def queueLocalChange(self, x: int, y: int, Bytes: bytes) -> None:
        if 0 <= x < self.WIDTH and 0 <= y < self.HEIGHT:
            position = self.getPosition(x,y)
            self.LOCAL_QUEUE[position] = Bytes

    def updateLocalBuffer(self) -> None:
        buffer_list = bytearray(self.LOCAL_BUFFER)
        for byte in buffer_list:
            if byte > 10: print(byte)
        for position in self.LOCAL_QUEUE:
            buffer_list[position:position+self.BYTES_PER_PIXEL] = self.LOCAL_QUEUE[position]
        self.LOCAL_BUFFER = bytes(buffer_list)
        self.LOCAL_QUEUE = {}

    def syncBuffers(self) -> None:
        self.SYS_VIDEO_BUFFER.seek(0)
        self.SYS_VIDEO_BUFFER.write(self.LOCAL_BUFFER)

    def updateFrameBuffer(self) -> None:
        self.updateLocalBuffer()
        self.syncBuffers()

    def clearFrameBuffer(self, Bytes: bytes = b'\x00\x00\x00\x00') -> None:
        for i in range(self.WIDTH):
            for j in range(self.HEIGHT):
                self.queueLocalChange(i,j,Bytes)
        self.updateFrameBuffer()

    def initTerminal(self) -> None:
        print("\x1b[2J\x1b[H",end="")
        self.clearFrameBuffer()
        print("\n"*(self.HEIGHT//14))

    def setupParams(self, frame: Image):
        width, height = frame.size
        self.FRAME_WIDTH, self.FRAME_HEIGHT = width, height
        for y in range(self.FRAME_HEIGHT):
            for x in range(self.FRAME_WIDTH):
                self.CURRENT_PIXELS[self.getPosition(x,y)] = None
        self.convertFrame(frame)
        self.drawFrame(frame)
        self.CURRENT_PIXELS = dict(self.CURRENT_FRAME)

    def convertRGBtoBGRA(self, r:int, g:int, b:int) -> bytes:
        r = r << (16)
        g = g << (8)
        return (r + g + b).to_bytes(4,'little')

    def convertFrame(self, frame: Image):
        px = frame.load()
        for y in range(self.FRAME_HEIGHT):
            for x in range(self.FRAME_WIDTH):
                self.CURRENT_FRAME[self.getPosition(x,y)] = self.convertRGBtoBGRA(*px[x,y])

    def drawFrame(self, frame) -> None:
        self.convertFrame(frame)
        cursor = 4
        for y in range(self.FRAME_HEIGHT):
            for x in range(self.FRAME_WIDTH):
                if self.CURRENT_PIXELS[self.getPosition(x,y)] != self.CURRENT_FRAME[self.getPosition(x,y)]:
                    self.queueLocalChange(x,y,self.CURRENT_FRAME)
                    cursor+=3