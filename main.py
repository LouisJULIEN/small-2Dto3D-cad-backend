from edge.edge import reconstruct_edges
from preprocess.parse import parse_two_D_projections
from type import Raw2DProjections
from preprocess.validate import validateTwoDProjections
from vertex.vertex import reconstruct_vertices


def two_D_to_three_D(two_D_projections: Raw2DProjections):
    assert validateTwoDProjections(two_D_projections), "invalid twoDProjections"
    parsed_two_D_projections = parse_two_D_projections(two_D_projections)

    three_D_reconstruction = {
        'dandling': {}
    }

    reconstructed_vertices, dandling_vertices = reconstruct_vertices(parsed_two_D_projections)

    three_D_reconstruction['vertices'] = reconstructed_vertices
    three_D_reconstruction['dandling']['vertices'] = dandling_vertices

    reconstructed_edges, dandling_edges = reconstruct_edges(parsed_two_D_projections,
                                                            three_D_reconstruction['vertices'])

    three_D_reconstruction['edges'] = reconstructed_edges
    three_D_reconstruction['dandling']['edges'] = dandling_edges

    # draw_3D_points_list([reconstructed_vertices, dandling_vertices])
    print(f"reconstructed_vertices : {len(reconstructed_vertices)}, dandling_vertices : {len(dandling_vertices)}")
    print(f"reconstructed_edges : {len(reconstructed_edges)}, dandling_edges : {len(dandling_edges)}")

    return three_D_reconstruction
