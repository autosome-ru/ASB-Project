import os
import sys

sys.path.insert(1, "/home/abramov/ASB-Project")
from scripts.HELPERS.paths_for_components import parallel_parameters_path, correlation_path

if __name__ == "__main__":
    with open(parallel_parameters_path + 'CS_parameters.cfg', 'w') as file:
        for file_name in os.listdir(correlation_path):
            if os.path.isdir(correlation_path + file_name):
                for file_name2 in os.listdir(correlation_path + file_name):
                    file.write(file_name2 + '\n')
                break
