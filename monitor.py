import cv2, cv2.cv, math, time, json
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera
from multiprocessing import Pool
from time import sleep

PLAYER0 = BLANK   = BLUE  = 0
PLAYER1 = PLAYERA = RED   = 1
PLAYER2 = PLAYERB = WHITE = 2
  
class Capture:
  __cap = None
  __cam = None
  __cam_array = None
  __debug = False
  __corner_offsets_xs = (-20,20,0,0)
  __corner_offsets_ys = (25,25,0,0)
  __rotation_enabled = False
  __calibration = {}
  
  def __init__(self, device = 0, brightness = 0.5, contrast = 0.5, exposure = 0.4, debug = False):
    self.__cam = PiCamera()
    self.__cam.resolution = (640, 480)
    self.__cam.framerate = 30
    self.__cam.exposure_mode = "auto"
    sleep(2)
    self.__cam.exposure_mode = "off"
    self.__cam.brightness = 35
    self.__cam.contrast = 95
    self.__cam.saturation = -25
    self.__cam_array = PiRGBArray(self.__cam, size=(640, 480))
    self__debug = debug
    self.__best_exposure = (0,0)
    self.__classification = pickle.load(open("MLPClassifier.pkl", "rb"))
    self.__classification2 = pickle.load(open("MLPClassifier2.pkl", "rb"))
    self.__classification3 = pickle.load(open("SGDClassifier.pkl", "rb"))
    sleep(0.05)
    
  def __enter__(self):
    return self
    
  def __exit__(self, exc_type, exc_value, traceback):
    self.close()
    
  def close(self):
    self.__cap.release()
  
  def getFrame(self):
    self.__cam_array.truncate(0)
    
    self.__cam.capture(self.__cam_array, format="bgr", use_video_port=False)
    frame = self.__cam_array.array
    
    return frame
    
  def cropFrame(self, frame, scale_constant = 4.7, crop_size = 180): 
    colour_image = frame
    
    grey_image = cv2.cvtColor(colour_image, cv2.COLOR_BGR2GRAY)
    grey_image = cv2.medianBlur(grey_image,5)

    circles = cv2.HoughCircles(grey_image, cv2.cv.CV_HOUGH_GRADIENT, 1, 25, param1=35, param2=30, minRadius=10, maxRadius=40)
    try:
      circles = np.uint16(np.around(circles))
    except AttributeError:
      return None

    frame_centre = (frame.shape[1]/2, frame.shape[0]/2)

    distance_from_centre = {}

    for circle in circles[0,:]: 
      x = circle[0]
      y = circle[1]
      k = math.sqrt((x-frame_centre[0])**2 + (y-frame_centre[1])**2)
      distance_from_centre[k] = circle

    board_centre = [0, 0]

    centre_circles = []

    for item in sorted(distance_from_centre)[:4]:
      board_centre[0] += distance_from_centre[item][0]
      board_centre[1] += distance_from_centre[item][1]
      centre_circles.append(distance_from_centre[item])
      if self.__debug: cv2.circle(grey_image, (distance_from_centre[item][0], distance_from_centre[item][1]), 5, (255,255,255), 2)

    board_centre = (board_centre[0]/4, board_centre[1]/4)

    average_centre_distance = 0

    for item in centre_circles:
      x = item[0]
      y = item[1]
      average_centre_distance += math.sqrt((x-board_centre[0])**2 + (y-board_centre[1])**2)
      
    average_centre_distance = average_centre_distance/4

    board_radius = scale_constant * average_centre_distance

    #Rotation

    circles_above_centre = []
    circles_below_centre = []

    for item in centre_circles:
      if item[1] < board_centre[1]:
        circles_above_centre.append(item)
      else:
        circles_below_centre.append(item)
    
    try:
      differance_in_xs_above = abs(float(circles_above_centre[0][0]) - float(circles_above_centre[1][0]))
      differance_in_ys_above = float(float(circles_above_centre[1][1]) - float(circles_above_centre[0][1]))
    except IndexError:
      differance_in_xs_above = 1
      differance_in_ys_above = 0
      
    try:
      differance_in_xs_below = abs(float(circles_below_centre[0][0]) - float(circles_below_centre[1][0]))
      differance_in_ys_below = float(float(circles_below_centre[1][1]) - float(circles_below_centre[0][1]))
    except IndexError:
      differance_in_xs_below = 1
      differance_in_ys_below = 0
    
    try:
      angle_above = math.atan(differance_in_ys_above / differance_in_xs_above)
    except ZeroDivisionError:
      angle_above = 0
    
    try:
      angle_below = math.atan(differance_in_ys_below / differance_in_xs_below)
    except ZeroDivisionError:
      angle_below = 0
      
    
    if abs(angle_above) > abs(angle_below):
      angle_extra = 0.5 * angle_below
    else:
      angle_extra = 0.5 * angle_above
    angle_deg = (-180/math.pi) * ((angle_above + angle_below + angle_extra) / 2.5)
    
    if not self.__rotation_enabled:
      angle_deg = 1

    if angle_deg != 0.0:
      matrix = cv2.getRotationMatrix2D((board_centre[0], board_centre[1]), angle_deg, 1)
      colour_image = cv2.warpAffine(colour_image, matrix, (colour_image.shape[1], colour_image.shape[0]))

    #Markers

    top_right    = (board_centre[0] + int(board_radius) + self.__corner_offsets_xs[0], board_centre[1] - int(board_radius) + self.__corner_offsets_ys[0])
    top_left     = (board_centre[0] - int(board_radius) + self.__corner_offsets_xs[1], board_centre[1] - int(board_radius) + self.__corner_offsets_ys[1])
    bottom_right = (board_centre[0] + int(board_radius) + self.__corner_offsets_xs[2], board_centre[1] + int(board_radius) + self.__corner_offsets_ys[2])
    bottom_left  = (board_centre[0] - int(board_radius) + self.__corner_offsets_xs[3], board_centre[1] + int(board_radius) + self.__corner_offsets_ys[3])

    if self.__debug:
      cv2.circle(colour_image, top_right, 5, (255,255,255), 2)
      cv2.circle(colour_image, top_left, 5, (255,255,255), 2)
      cv2.circle(colour_image, bottom_right, 5, (255,255,255), 2)
      cv2.circle(colour_image, bottom_left, 5, (255,255,255), 2)
      cv2.circle(colour_image, (board_centre[0], board_centre[1]), 5, (255,255,255), 2)

    #Crop and Scale

    matrix_from_points = np.float32([list(top_left),list(top_right), list(bottom_left), list(bottom_right)])
    matrix_to_points = np.float32([[0,0], [crop_size,0], [0,crop_size], [crop_size,crop_size]])

    matrix = cv2.getPerspectiveTransform(matrix_from_points, matrix_to_points)
    cropped_image = cv2.warpPerspective(colour_image, matrix, (crop_size, crop_size))
    
    return cropped_image
  
  def showImage(self, image, name = "Image", show_for = 10000):
    cv2.imshow(name, image)
    cv2.waitKey(show_for)
    cv2.destroyAllWindows()
  
  def getSquares(self, cropped_image, squares = 6, blur_amount = 3, calibrate = False):
    size = cropped_image.shape[0]
    step = size/squares
    calib = self.__calibration
    
    if calibrate:
      calib_row = []

    hsv_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2HSV)

    if self.__debug: print overall_mean, overall_means, overall_colour_distance
    
    offset = 0.2
    board = []
    for x in range(0,squares):
      col = []
      if calibrate:
        calib_col = []
      for y in range(0,squares):
        hsv_image_range = hsv_image[int(y*step)+4:int((y+1)*step)-1-4, int(x*step)+4:int((x+1)*step)-1-4]
        
        colour = BLUE

        square_image = hsv_image[int(y*step):int((y+1)*step), int(x*step):int((x+1)*step)]
        if calibrate:
          calib_col.append(square_image)

        yp1 = int(y*step) - 5
        yp2 = int((y+1)*step) + 5
        xp1 = int(x*step) - 5
        xp2 = int((x+1)*step) + 5
        if yp1 < 0: yp1 = 0
        if yp2 > size: yp2 = size
        if xp1 < 0: xp1 = 0
        if xp2 > size: xp2 = size
        grey_image = cv2.cvtColor(cropped_image[yp1:yp2, xp1:xp2], cv2.COLOR_BGR2GRAY)
        grey_image = cv2.medianBlur(grey_image, 1)

        circles = cv2.HoughCircles(grey_image, cv2.cv.CV_HOUGH_GRADIENT, 1, 10, param1=65, param2=20, minRadius=10, maxRadius=40)    
        colours = [[],[],[]]

        if circles != None:
          lower_range = np.array([0, 170, 170], dtype=np.uint8)
          upper_range = np.array([50, 255, 255], dtype=np.uint8)
          mask = cv2.inRange(hsv_image_range, lower_range, upper_range)
          red_masked_average = np.mean(mask)

          lower_range = np.array([0, 0, 160], dtype=np.uint8)
          upper_range = np.array([255, 255, 255], dtype=np.uint8)
          mask = cv2.inRange(hsv_image_range, lower_range, upper_range)
          white_masked_average = np.mean(mask)

          if red_masked_average > 127:
            colour = RED
          elif white_masked_average >  127:
            colour = WHITE
          else:
            colour = BLUE
        
        col.append(colour)
        if self.__debug:
          print x, y, colour
      board.append(col)
      if calibrate:
        calib_row.append(calib_col)
    if calibrate: return calib_row
    return board
    
  def __getBoardUnsafe(self, squares = 6, blur_amount = 3, scale_constant = 4, crop_size = 180):
    cropped_image = None
    while cropped_image == None:
      frame = self.getFrame()
      cropped_image = self.cropFrame(frame)
      if cropped_image == None:
        print self.getFrame()
        raise Exception("I done broke")
    return self.getSquares(cropped_image, squares, blur_amount)
      
  def getBoardThreaded(self, squares = 6, blur_amount = 3, scale_constant = 4, crop_size = 180, samples = 7, pool_size = 4):
    pool = Pool(pool_size)
    counter = 0
    timer = time.time()
    result = False
    while not result:
      if counter > 10 or time.time() - timer > 20: return None
      boards = []
      inputs = []
      for item in range(0, samples): inputs.append((squares, blur_amount, scale_constant, crop_size))
      boards = p.map(self.__getBoardUnsafe, inputs)
      for item in boards:
        if boards.count(item)/float(samples) > 0.7:
          return item
      boards = []
      counter += 1
    return None
  
  def getBoard(self, squares = 6, blur_amount = 3, scale_constant = 4, crop_size = 180, samples = 7):
    counter = 0
    timer = time.time()
    result = False
    boards = []
    while len(boards) < samples:
      sleep(0.035)
      boards.append(self.__getBoardUnsafe(squares, blur_amount, scale_constant, crop_size))
    commonalities = []
    for x in range(6):
      col = []
      for y in range(6):
        col.append([0,0,0])
      commonalities.append(col)
    for board in boards:
      for x in range(6):
        for y in range(6):
          commonalities[x][y][board[x][y]] += 1

    result = []
    for x in range(6):
      col = []
      for y in range(6):
        colour = BLUE
        if commonalities[x][y][BLUE] < commonalities[x][y][RED] and commonalities[x][y][WHITE] < commonalities[x][y][RED]:
          if commonalities[x][y][RED] > samples * 0.5:
             colour = RED
        if commonalities[x][y][BLUE] < commonalities[x][y][WHITE] and commonalities[x][y][RED] < commonalities[x][y][WHITE]:
          if commonalities[x][y][WHITE] > samples * 0.5:
             colour = WHITE
        col.append(colour)
      result.append(col)
    return result

    return None
