import os
import sys

sys.path.insert(1, "/home/abramov/ASB-Project")
from scripts.HELPERS.paths import parallel_parameters_path, ploidy_path

if __name__ == "__main__":
    with open(parallel_parameters_path + 'ASWP_parameters.cfg', 'w') as file:
        for file_name in os.listdir(ploidy_path):
            if not os.path.isfile(ploidy_path + file_name):
                continue
            file.write(file_name + '\n')