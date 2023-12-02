
def counting_people(door, centroid, pos, t, obj_counter, C_left_boundary, C_right_boundary, C_min, C_max, A_left_boundary, A_right_boundary, A_min, A_max, B_left_boundary, B_right_boundary, B_min, B_max):
    
        if not (C_left_boundary <= centroid[1] <= C_right_boundary and C_min <= centroid[1] <= C_max):
            pos[t.id] = {
                'previous': pos[t.id]['current'],
                'current': centroid[1]      }
        if door == "bottom":        
            if pos[t.id]['current'] > C_right_boundary > pos[t.id]['previous'] and C_max > centroid[0] > C_min:

                obj_counter[1] += 1 #Right side
                going_out += 1
            if pos[t.id]['current'] < C_left_boundary < pos[t.id]['previous'] and C_max > centroid[0] > C_min:
                
                obj_counter[0] += 1 #Left side
                going_in += 1

        elif door == "top":
            if pos[t.id]['current'] > C_right_boundary > pos[t.id]['previous'] and C_max > centroid[0] > C_min:

                obj_counter[0] += 1 #Right side
                going_in += 1

            if pos[t.id]['current'] < C_left_boundary < pos[t.id]['previous'] and C_max > centroid[0] > C_min:
                
                obj_counter[1] += 1 #Left side
                going_out += 1