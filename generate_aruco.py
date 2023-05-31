import argparse
from typing import Tuple
import cadquery.cqgi as cqgi
import cadquery as cq

import cv2
import numpy as np

ARUCO_DICT = {
	"DICT_4X4_50": cv2.aruco.DICT_4X4_50,
	"DICT_4X4_100": cv2.aruco.DICT_4X4_100,
	"DICT_4X4_250": cv2.aruco.DICT_4X4_250,
	"DICT_4X4_1000": cv2.aruco.DICT_4X4_1000,
	"DICT_5X5_50": cv2.aruco.DICT_5X5_50,
	"DICT_5X5_100": cv2.aruco.DICT_5X5_100,
	"DICT_5X5_250": cv2.aruco.DICT_5X5_250,
	"DICT_5X5_1000": cv2.aruco.DICT_5X5_1000,
	"DICT_6X6_50": cv2.aruco.DICT_6X6_50,
	"DICT_6X6_100": cv2.aruco.DICT_6X6_100,
	"DICT_6X6_250": cv2.aruco.DICT_6X6_250,
	"DICT_6X6_1000": cv2.aruco.DICT_6X6_1000,
	"DICT_7X7_50": cv2.aruco.DICT_7X7_50,
	"DICT_7X7_100": cv2.aruco.DICT_7X7_100,
	"DICT_7X7_250": cv2.aruco.DICT_7X7_250,
	"DICT_7X7_1000": cv2.aruco.DICT_7X7_1000,
	"DICT_ARUCO_ORIGINAL": cv2.aruco.DICT_ARUCO_ORIGINAL,
	"DICT_APRILTAG_16h5": cv2.aruco.DICT_APRILTAG_16h5,
	"DICT_APRILTAG_25h9": cv2.aruco.DICT_APRILTAG_25h9,
	"DICT_APRILTAG_36h10": cv2.aruco.DICT_APRILTAG_36h10,
	"DICT_APRILTAG_36h11": cv2.aruco.DICT_APRILTAG_36h11
}

def get_user_input(message, input_type, quit_string: str = "q"):
    """ Get user input for a given type

    Args:
        message (str): The message to display to the user
        input_type (type): The type of input to get from the user
        quit_string (str, optional): The string to use to exit the program. Defaults to "q".

    Returns:
        input_type: The user input
    """

    while True:
        raw_input = input(f"{message} (q to exit): ")

        if raw_input == quit_string:
            exit()

        if raw_input == '':
            print(f"Invalid {input_type}")
            continue

        try:
            return input_type(raw_input)
        except ValueError:
            print(f"Invalid {input_type}")


def get_aruco_dict_and_type() -> Tuple[str, int]:
    """ Query the user for the type of aruco marker to generate """

    print("Available Aruco Markers:")
    for i, key in enumerate(ARUCO_DICT.keys()):
        print(f"{i}: {key.replace('DICT_', '')}")

    # Select the marker type
    while True:
        raw_input = input("Enter the type of marker to generate (q to exit) (Default: ARUCO_ORIGINAL): ")

        if raw_input == 'q':
            exit()

        if raw_input == '':
            marker_type = "DICT_ARUCO_ORIGINAL"
            break

        try:
            selected_marker = int(raw_input)
        except ValueError:
            print("Invalid marker type")
            continue

        if selected_marker < 0 or selected_marker > len(ARUCO_DICT.keys()):
            print("Invalid marker type")
        else:
            marker_type = list(ARUCO_DICT.keys())[selected_marker]
            break

    # get the max marker id for the selected marker type
    max_marker_id = cv2.aruco.getPredefinedDictionary(ARUCO_DICT[marker_type]).bytesList.shape[0]

    # Select the marker id
    while True:
        raw_input = input("Enter the marker id (q to exit): ")

        if raw_input == 'q':
            exit()

        try:
            marker_id = int(raw_input)
        except ValueError:
            print(f"Input must be an integer between 0 and {max_marker_id}")
            continue

        if marker_id < 0 or marker_id > max_marker_id:
            print(f"Input must be an integer between 0 and {max_marker_id}")
        else:
            break

    return marker_type, marker_id


def generate_aruco_ocupancy_grid(dict_type: str, marker_id: int):
    """ Generate an ocupancy grid with 0 for black squares and 1 for white squares """

    # Check if the dictionary type is valid
    if dict_type not in ARUCO_DICT.keys():
        raise ValueError(f"Invalid dictionary type: {dict_type}")

    # Get the aruco dictionary dimensions
    dimensions = dict_type.split('_')[1]

    # Special case for the original dictionary
    if dict_type == "DICT_ARUCO_ORIGINAL":
        dimensions = "5X5"

    # Special case for the april tag dictionaries
    if dict_type.startswith("DICT_APRILTAG"):
        if dict_type.endswith("16h5"):
            dimensions = "4X4"
        elif dict_type.endswith("25h9"):
            dimensions = "5X5"
        elif dict_type.endswith("36h10"):
            dimensions = "6X6"
        elif dict_type.endswith("36h11"):
            dimensions = "6X6"


    # Get the number of rows and columns
    rows, _ = dimensions.split('X')

    # Get the aruco dictionary
    aruco_dict = cv2.aruco.getPredefinedDictionary(ARUCO_DICT[dict_type])

    # Generate the marker
    marker = np.array(aruco_dict.generateImageMarker(marker_id, int(rows) + 2))

    # Convert the marker to a binary array
    marker = np.where(marker == 255, 1, 0)

    # rotate the marker -90 degrees
    # marker = np.rot90(marker, -1)

    return marker

def parse_args():
    """ Parse command line arguments """

    parser = argparse.ArgumentParser(description="Generate Aruco Markers")
        # card_side = get_user_input("Enter the total side length (marker+margin) (mm)", float)
        # card_margin = get_user_input("Enter the white margin width (mm)", float)
        # card_height = get_user_input("Enter the marker thikness (mm)", float)
        # groove_depth = get_user_input("Enter the groove depth (mm)", float)
        # marker_type, marker_id = get_aruco_dict_and_type()
    parser.add_argument("-o", "--output", type=str, default="aruco_marker",
                        help="Output file name")
    parser.add_argument("--default_id", type=int,
                        help=("Provide only marker id, usee default parameters,"
                              " 4X4_50, 90mm side, 1mm marker depth, 10mm margin,"
                              "0.4mm marker groove depth"))
    parser.add_argument("--box_side", type=float,
                        help="Provide box side length in mm")
    parser.add_argument("--box_thickness", type=float,
                        help="Provide box thickness in mm")
    parser.add_argument("--marker_margin", type=float,
                        help="Provide marker margin in mm")
    parser.add_argument("--marker_groove_depth", type=float,
                        help="Provide marker groove depth in mm")
    parser.add_argument("--aruco_dictionary", type=str,
                        help=f"Choose from the available aruco dictionaries: {list(ARUCO_DICT.keys())}")
    parser.add_argument("--marker_id", type=int,
                        help="Provide marker id")
    parser.add_argument("--magnet_inset_radius", type=float,
                        help="If given, two circular indentations will be made on the bottom of the box for magnets")
    parser.add_argument("--layer_height", type=float,
                        help="Layer height for the 3D printer, will be used for inset depth and groove depth")

    return parser.parse_args()

def main():
    """ Main function """

    args = parse_args()

    FILENAME = args.output

    if args.default_id:
        marker_type, marker_id = "DICT_4X4_50", args.default_id
        card_side = 90
        card_margin = 10
        card_height = 1
        groove_depth = 0.4
        FILENAME += f"_{marker_id}"
    else:
        if args.aruco_dictionary and args.marker_id is not None:
            marker_type = args.aruco_dictionary
            marker_id = args.marker_id
        else:
            marker_type, marker_id = get_aruco_dict_and_type()

        if args.box_side:
            card_side = args.box_side
        else:
            card_side = get_user_input("Enter the total side length (marker+margin) (mm)", float)

        if args.box_thickness:
            card_height = args.box_thickness
        else:
            card_height = get_user_input("Enter the marker thickness (mm)", float)

        if args.marker_margin:
            card_margin = args.marker_margin
        else:
            card_margin = get_user_input("Enter the white margin width (mm)", float)

        if args.marker_groove_depth:
            groove_depth = args.marker_groove_depth
        else:
            groove_depth = get_user_input("Enter the groove depth (mm)", float)

        if args.magnet_inset_radius:
            magnet_inset_radius = args.magnet_inset_radius / 10
        else:
            magnet_inset_radius = None

        if args.layer_height:
            layer_height = args.layer_height / 10
        else:
            layer_height = get_user_input("Enter the layer height (mm)", float)

    print(f"Aruco Dictionary: {marker_type}")
    aruco_img = generate_aruco_ocupancy_grid(marker_type, marker_id)


    print(f"ArUco Marker {marker_id}: ")
    # print as ASCII art
    print(u"\u2588"*(aruco_img.shape[1]+2)*2)
    for i in range(0, aruco_img.shape[0]):
        print(u"\u2588"*2, end="")
        for j in range(0, aruco_img.shape[1]):
            if aruco_img[i,j] == 0:
                print(" "*2, end="")
            else:
                print(u"\u2588"*2, end="")
        print(u"\u2588"*2)
    print(u"\u2588"*(aruco_img.shape[1]+2)*2)

    # Extrude the aruco marker
    aruco_extrusion = cq.Workplane('XY')
    extrusion_points = []

    aruco_side = card_side - card_margin * 2

    square_side = aruco_side / aruco_img.shape[0]
    square_offset = aruco_side/2 - square_side / 2

    for i in range(0, aruco_img.shape[0]):
        for j in range(0, aruco_img.shape[1]):
            if aruco_img[i,j] == 0:
                extrusion_points.append(
                    (  # Rotate to align X and Y axes
                        (j) * square_side - square_offset,
                        (aruco_img.shape[0]-1-i) * square_side - square_offset,
                    )
                )

    aruco_extrusion = aruco_extrusion.pushPoints(extrusion_points).rect(square_side,square_side).extrude(card_height-groove_depth)

    # Add a base under the aruco marker
    base = cq.Workplane('XY').rect(card_side, card_side).extrude(groove_depth)
    base = base.rect(card_side, card_side).extrude(-card_height+groove_depth)

    # Subtract the aruco marker from the base
    obj = base.cut(aruco_extrusion)

    # Add a magnet inset
    dist_to_indent = card_side/2-card_margin/2
    if magnet_inset_radius is not None:
        print("Adding magnet inset")
        indent_positions = [
            (dist_to_indent, dist_to_indent),
            (-dist_to_indent, -dist_to_indent),
            (dist_to_indent, -dist_to_indent),
            (-dist_to_indent, dist_to_indent),
        ]
        obj = obj.faces("<Z").workplane().pushPoints(indent_positions).circle(magnet_inset_radius).cutBlind(-layer_height)

    # Add the number if the marher in the bottom
    obj = obj.faces("<Z").workplane().center(0.0, -dist_to_indent).text(str(marker_id), card_margin*0.7, -layer_height, combine='cut')

    # Add the dictionary name in the bottom
    obj = obj.faces("<Z").workplane().center(0.0, dist_to_indent*2).transformed(rotate=(0,0,180)).text(marker_type, card_margin*0.5, -layer_height, combine='cut')

    obj.val().exportStl(FILENAME+'.stl', ascii=True)



if __name__ == "__main__":
    main()
