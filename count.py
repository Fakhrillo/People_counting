
def counting_people(door, centroid, pos, t, obj_counter, C_left_boundary, C_right_boundary, C_min, C_max, A_left_boundary, A_right_boundary, A_min, A_max, B_left_boundary, B_right_boundary, B_min, B_max):
    if door in ["top", "bottom"]:
        if not (C_left_boundary <= centroid[1] <= C_right_boundary and C_min <= centroid[1] <= C_max or A_left_boundary <= centroid[0] <= A_right_boundary and A_min <= centroid[0] <= A_max or B_left_boundary <= centroid[0] <= B_left_boundary and B_min <= centroid[0] <= B_max):
            pos[t.id] = {
                'previous': pos[t.id]['current'],
                'current': centroid      }
        if door == "bottom":        
            if pos[t.id]['current'][1] > C_right_boundary > pos[t.id]['previous'][1] and C_max > centroid[0] > C_min or pos[t.id]['current'][0] > A_right_boundary > pos[t.id]['previous'][0] and A_max > centroid[1] > A_min or pos[t.id]['current'][0] < B_right_boundary < pos[t.id]['previous'][0] and B_max > centroid[1] > B_min:

                obj_counter[1] += 1 #Right side
                going_out += 1
            if pos[t.id]['current'][1] < C_left_boundary < pos[t.id]['previous'][1] and C_max > centroid[0] > C_min or pos[t.id]['current'][0] < A_left_boundary < pos[t.id]['previous'][0] and A_max > centroid[1] > A_min or pos[t.id]['current'][0] > B_left_boundary > pos[t.id]['previous'][0] and B_max > centroid[1] > B_min:
                
                obj_counter[0] += 1 #Left side
                going_in += 1

        elif door == "top":
            if pos[t.id]['current'][1] > C_right_boundary > pos[t.id]['previous'][1] and C_max > centroid[0] > C_min or pos[t.id]['current'][0] > A_right_boundary > pos[t.id]['previous'][0] and A_max > centroid[1] > A_min or pos[t.id]['current'][0] < B_right_boundary < pos[t.id]['previous'][0] and B_max > centroid[1] > B_min:

                obj_counter[0] += 1 #Right side
                going_in += 1

            if pos[t.id]['current'][1] < C_left_boundary < pos[t.id]['previous'][1] and C_max > centroid[0] > C_min or pos[t.id]['current'][0] < A_left_boundary < pos[t.id]['previous'][0] and A_max > centroid[1] > A_min or pos[t.id]['current'][0] > B_left_boundary > pos[t.id]['previous'][0] and B_max > centroid[1] > B_min:
                
                obj_counter[1] += 1 #Left side
                going_out += 1

    else:
        if not (C_left_boundary <= centroid[0] <= C_right_boundary and C_min <= centroid[0] <= C_max or A_left_boundary <= centroid[1] <= A_right_boundary and A_min <= centroid[1] <= A_max or B_left_boundary <= centroid[1] <= B_left_boundary and B_min <= centroid[1] <= B_max):
            pos[t.id] = {
                'previous': pos[t.id]['current'],
                'current': centroid      }
        if door == "right":        
            if pos[t.id]['current'][0] > C_right_boundary > pos[t.id]['previous'][0] and C_max > centroid[1] > C_min or pos[t.id]['current'][1] > A_right_boundary > pos[t.id]['previous'][1] and A_max > centroid[0] > A_min or pos[t.id]['current'][1] < B_right_boundary < pos[t.id]['previous'][1] and B_max > centroid[0] > B_min:

                obj_counter[1] += 1 #Right side
                going_out += 1
            if pos[t.id]['current'][0] < C_left_boundary < pos[t.id]['previous'][0] and C_max > centroid[1] > C_min or pos[t.id]['current'][1] < A_left_boundary < pos[t.id]['previous'][1] and A_max > centroid[0] > A_min or pos[t.id]['current'][1] > B_left_boundary > pos[t.id]['previous'][1] and B_max > centroid[0] > B_min:
                
                obj_counter[0] += 1 #Left side
                going_in += 1

        elif door == "left":
            if pos[t.id]['current'][0] > C_right_boundary > pos[t.id]['previous'][0] and C_max > centroid[1] > C_min or pos[t.id]['current'][1] < A_right_boundary < pos[t.id]['previous'][1] and A_max > centroid[0] > A_min or pos[t.id]['current'][1] > B_right_boundary > pos[t.id]['previous'][1] and B_max > centroid[0] > B_min:

                obj_counter[0] += 1 #Right side
                going_in += 1

            if pos[t.id]['current'][0] < C_left_boundary < pos[t.id]['previous'][0] and C_max > centroid[1] > C_min or pos[t.id]['current'][1] > A_left_boundary > pos[t.id]['previous'][1] and A_max > centroid[0] > A_min or pos[t.id]['current'][1] < B_left_boundary < pos[t.id]['previous'][1] and B_max > centroid[0] > B_min:
                
                obj_counter[1] += 1 #Left side
                going_out += 1