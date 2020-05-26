import Augmentor
import os

PATH = os.path.dirname(os.path.abspath(__file__))
def main():

	print(PATH)
	for _, dir_, files in os.walk(PATH+"/normal_dataset"):
		for folder in dir_:
			
			if(folder =="output"):
				continue
	
			print(folder)
			p = Augmentor.Pipeline(PATH+"{}/{}".format("/normal_dataset",folder))
			p.random_distortion(probability=1, grid_width=2, grid_height=2, magnitude=3)
			p.rotate(probability=1, max_left_rotation=10, max_right_rotation=10)
			p.sample(8000)

if __name__ == '__main__':
	main()
