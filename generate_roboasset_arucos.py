import os
import subprocess
from typing import List

def roboasset_aruco_command(dictionary_name: str,
                            marker_id: int,
                            output_dir: str="roboasset_arucos") -> str:
    command = "python3 generate_aruco.py"
    command += " --box_side 90"
    command += " --marker_margin 10"
    command += " --box_thickness 2"
    command += " --marker_groove_depth 0.8"
    command += f" --aruco_dictionary {dictionary_name}"
    command += f" --marker_id {marker_id}"
    command += " --magnet_inset_radius 5.15"
    command += " --layer_height 0.2"
    filename = f"{dictionary_name}_{marker_id}.stl"
    command += f" --output {os.path.join(output_dir, filename)}"

    return command

def generate_arucos_commands(dictionary_names: List[str],
                             marker_ids: List[int],
                             output_dir: str="roboasset_arucos") -> List[str]:
    for dictionary_name in dictionary_names:
        for marker_id in marker_ids:
            yield roboasset_aruco_command(dictionary_name, marker_id, output_dir)

def main():
    output_dir = "roboasset_arucos"
    os.makedirs(output_dir, exist_ok=True)

    dictionary_names = ["DICT_4X4_50", "DICT_APRILTAG_36h11"]
    marker_ids = [1, 3]


    for command in generate_arucos_commands(dictionary_names, marker_ids):
        subprocess.run(command, shell=True)


if __name__ == "__main__":
    main()
