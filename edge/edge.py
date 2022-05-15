from typing import Dict

from constant import MAX_POINT_TO_POINT_ERROR_DISTANCE
from superclasses import ThreeDLineStringWithId, ProjectedLineStringWithId
from type import Parsed2DProjections, Reconstructed3DVertices, Reconstructed3DEdges


def reconstruct_edges(parsed_projections: Parsed2DProjections, reconstructed_3d_points: Reconstructed3DVertices
                      ) -> (Reconstructed3DEdges, Reconstructed3DEdges):
    all_edges_projections: Dict[str, ProjectedLineStringWithId] = {}
    for a_projection in parsed_projections.values():
        all_edges_projections.update(a_projection['edges'])

    reconstruct_edge_id = '100000'

    reconstructed_edges = {}
    for an_edge_projection_id, an_edge_projection in all_edges_projections.items():
        # we do the cross product of all possible 3D point. The extra vertices are deleted afterwards
        edge_3D_points_couple = []
        for three_d_pt_first in an_edge_projection.two_D_points[0].ancestors:
            for three_d_pt_second in an_edge_projection.two_D_points[1].ancestors:
                edge_3D_points_couple.append((three_d_pt_first, three_d_pt_second))

        # sort 3D_points by id to enhance stability
        edge_3D_points_couple.sort(key=lambda x: (x[0].id, x[1].id))

        for a_3D_pt_couple in edge_3D_points_couple:
            reconstructed_edges[reconstruct_edge_id] = ThreeDLineStringWithId(reconstruct_edge_id,
                                                                              a_3D_pt_couple)
            reconstructed_edges[reconstruct_edge_id].attach_to_ancestor(all_edges_projections[an_edge_projection_id])
            all_edges_projections[an_edge_projection_id].attach_to_ancestor(reconstructed_edges[reconstruct_edge_id])

            reconstruct_edge_id = str(int(reconstruct_edge_id) + 1)

    # remove duplicates i.e. edges with the exact same three_D_points
    def get_vertices_ids(edge):
        return [pt.id for pt in edge.three_D_points]

    reconstructed_edges_list = list(reconstructed_edges.values())  # it copies values
    reconstructed_edges_list.sort(key=get_vertices_ids)

    # remove duplicate edge
    for i in range(len(reconstructed_edges_list) - 1):
        if get_vertices_ids(reconstructed_edges_list[i]) == get_vertices_ids(reconstructed_edges_list[i + 1]):
            reconstructed_edges_list[i].attach_to_multiple_ancestors(reconstructed_edges_list[i + 1].ancestors)


            for a_projected_edge in reconstructed_edges_list[i + 1].ancestors:
                a_projected_edge.remove_ancestor(reconstructed_edges_list[i + 1])
                a_projected_edge.attach_to_ancestor(reconstructed_edges_list[i])

            del reconstructed_edges[reconstructed_edges_list[i + 1].id]

    point_to_points_edge_map = generate_2D_point_to_point_edge_map(parsed_projections)

    for edge_id in list(reconstructed_edges.keys()):
        if not edge_is_consistent(reconstructed_edges[edge_id], point_to_points_edge_map):
            for a_projected_edge in reconstructed_edges[edge_id].ancestors:
                a_projected_edge.remove_ancestor(reconstructed_edges[edge_id])
            del reconstructed_edges[edge_id]

    dangling_edges = {}
    for an_edge_projection_id, an_edge_projection in all_edges_projections.items():
        if len(an_edge_projection.ancestors) == 0:
            dangling_edges[an_edge_projection_id] = an_edge_projection

    return reconstructed_edges, dangling_edges


def generate_2D_point_to_point_edge_map(parsed_projections: Parsed2DProjections):
    two_D_point_to_points = {}
    for an_axe, a_shape in parsed_projections.items():
        axes_points = {}

        for an_edge in a_shape['edges'].values():
            for a_pt in an_edge.two_D_points:
                a_pt_id = a_pt.id
                if a_pt_id not in axes_points.keys():
                    axes_points[a_pt_id] = []
                axes_points[a_pt_id] += [p.id for p in an_edge.two_D_points]

        two_D_point_to_points[an_axe] = axes_points
    return two_D_point_to_points


def edge_is_consistent(reconstructed_edge: ThreeDLineStringWithId, point_to_points_edge_map):
    was_checked_at_least_once = False

    if abs(reconstructed_edge.three_D_points[0].x - reconstructed_edge.three_D_points[
        1].x) < MAX_POINT_TO_POINT_ERROR_DISTANCE:
        was_checked_at_least_once = True
        for an_ancestor in reconstructed_edge.ancestors:
            pt_first, pt_second = an_ancestor.two_D_points[0], an_ancestor.two_D_points[1]
            if pt_first.id in point_to_points_edge_map['yz'].get(pt_second.id, []):
                return True

    if abs(reconstructed_edge.three_D_points[0].y - reconstructed_edge.three_D_points[
        1].y) < MAX_POINT_TO_POINT_ERROR_DISTANCE:
        was_checked_at_least_once = True
        for an_ancestor in reconstructed_edge.ancestors:
            pt_first, pt_second = an_ancestor.two_D_points[0], an_ancestor.two_D_points[1]
            if pt_first.id in point_to_points_edge_map['xz'].get(pt_second.id, []):
                return True

    if abs(reconstructed_edge.three_D_points[0].z - reconstructed_edge.three_D_points[
        1].z) < MAX_POINT_TO_POINT_ERROR_DISTANCE:
        was_checked_at_least_once = True
        for an_ancestor in reconstructed_edge.ancestors:
            pt_first, pt_second = an_ancestor.two_D_points[0], an_ancestor.two_D_points[1]
            if pt_first.id in point_to_points_edge_map['xy'].get(pt_second.id, []):
                return True

    # return false if at least one test was possible but no tests were successful
    # return true if no test were possible
    return not was_checked_at_least_once
