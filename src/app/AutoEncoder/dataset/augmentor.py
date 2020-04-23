import Augmentor
import os

PATH = os.path.dirname(os.path.abspath(__file__))
def main():

	print(PATH)
	for _, dir_, files in os.walk(PATH+"/sorted_cropped_words_resized"):
		for folder in dir_:
			print(folder)
			if(folder =="output"):
				continue

			p = Augmentor.Pipeline(PATH+"{}/{}".format("/sorted_cropped_words_resized",folder))
			p.random_distortion(probability=1, grid_width=2, grid_height=2, magnitude=3)
			p.rotate(probability=1, max_left_rotation=10, max_right_rotation=10)
			p.sample(10)

if __name__ == '__main__':
	main()
