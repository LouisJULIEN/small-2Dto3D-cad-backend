from graphics import draw_3D_points_list
from preprocess.parse import parse_two_D_projections
from vertex import reconstruct_vertices


class TestersVertex:
    id_number = 0

    @staticmethod
    def __add_ids(input):
        for an_axis_shapes in input.values():

            for a_shape_id, a_shape in an_axis_shapes.items():
                a_formatted_shape = {
                    "edges": {},
                    "vertices": {},
                    "type": a_shape["type"]
                }
                for a_point in a_shape["vertices"]:
                    a_formatted_shape["vertices"][TestersVertex.id_number] = a_point
                    TestersVertex.id_number += 1
                an_axis_shapes[a_shape_id] = a_formatted_shape

        return input

    @staticmethod
    def __parse_input(input):
        input_with_ids = TestersVertex.__add_ids(input)
        return parse_two_D_projections(input_with_ids)

    @staticmethod
    def reconstruct_vertices(input,
                             expected_found_vertices_number: int = 0, expected_dandling_vertices_number: int = 0,
                             draw=False):
        parsed_input = TestersVertex.__parse_input(input)
        found, dandling = reconstruct_vertices(parsed_input)

        print("\nFOUND")
        [print(f) for f in found.values()]
        print("DANDLING")
        [print(f) for f in dandling.values()]

        if draw:
            draw_3D_points_list([list(found.values()), list(dandling.values())])

        assert len(found) == expected_found_vertices_number, \
            f"{len(found)} vs {expected_found_vertices_number}"
        assert len(dandling) == expected_dandling_vertices_number, \
            f"{len(dandling)} vs {expected_dandling_vertices_number}"