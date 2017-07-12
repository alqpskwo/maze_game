class Maze(object):
	WIDTH_MIN = 3
	WIDTH_MAX = 51
	HEIGHT_MIN = 3
	HEIGHT_MAX = 51

	def __init__(self, width, height):

		if not (Maze.WIDTH_MIN <= width <= Maze.WIDTH_MAX
				and width % 2 == 1):
			message = "width must be odd and in the range [{}, {}].".format(
				Maze.WIDTH_MIN, Maze.WIDTH_MAX)
			raise ValueError(message)

		if not (Maze.HEIGHT_MIN <= height <= Maze.HEIGHT_MAX
				and height % 2 == 1):
			message = "height must be odd and in the range [{}, {}].".format(
				Maze.HEIGHT_MIN, Maze.HEIGHT_MAX)
			raise ValueError(message)

		self.width = width
		self.height = height