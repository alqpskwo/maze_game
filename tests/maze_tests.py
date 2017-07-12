from nose.tools import assert_raises
from maze_game import maze

def test_init():
	width_min = maze.Maze.WIDTH_MIN
	width_max = maze.Maze.WIDTH_MAX
	height_min = maze.Maze.HEIGHT_MIN
	height_max = maze.Maze.HEIGHT_MAX

	maze.Maze(width_min, height_min)
	maze.Maze(width_min, height_max)
	maze.Maze(width_max, height_min)
	maze.Maze(width_max, height_max)

	width_avg = (width_min + width_max) // 2
	width_odd = width_avg + 1 - (width_avg % 2)
	width_even = width_avg - (width_avg % 2)

	height_avg = (height_min + height_max) // 2
	height_odd = height_avg + 1 - (height_avg % 2)
	height_even = height_avg = (height_avg % 2)

	maze.Maze(width_odd, height_odd)

	assert_raises(ValueError, maze.Maze, width_even, height_odd)
	assert_raises(ValueError, maze.Maze, width_odd, height_even)
	assert_raises(ValueError, maze.Maze, width_even, height_even)

	assert_raises(ValueError, maze.Maze, width_min - 1, height_min)
	assert_raises(ValueError, maze.Maze, width_max + 1, height_min)
	assert_raises(ValueError, maze.Maze, width_min - 10, height_min)
	assert_raises(ValueError, maze.Maze, width_max + 16, height_min)

	assert_raises(ValueError, maze.Maze, width_min, height_min - 1)
	assert_raises(ValueError, maze.Maze, width_min, height_min - 20)
	assert_raises(ValueError, maze.Maze, width_min, height_max + 1)
	assert_raises(ValueError, maze.Maze, width_min, height_max + 8)
