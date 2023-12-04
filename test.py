or A_left_boundary <= centroid[0] <= A_right_boundary and A_min <= centroid[0] <= A_max or B_left_boundary <= centroid[0] <= B_left_boundary and B_min <= centroid[0] <= B_max

or pos[t.id]['current'] > A_right_boundary > pos[t.id]['previous'] and A_max > centroid[1] > A_min or pos[t.id]['current'] < B_right_boundary < pos[t.id]['previous'] and B_max > centroid[1] > B_min

or pos[t.id]['current'] < A_left_boundary < pos[t.id]['previous'] and A_max > centroid[1] > A_min or pos[t.id]['current'] > B_left_boundary > pos[t.id]['previous'] and B_max > centroid[1] > B_min

or pos[t.id]['current'] > A_right_boundary > pos[t.id]['previous'] and A_max > centroid[1] > A_min or pos[t.id]['current'] < B_right_boundary < pos[t.id]['previous'] and B_max > centroid[1] > B_min

or pos[t.id]['current'] < A_left_boundary < pos[t.id]['previous'] and A_max > centroid[1] > A_min or pos[t.id]['current'] > B_left_boundary > pos[t.id]['previous'] and B_max > centroid[1] > B_min

