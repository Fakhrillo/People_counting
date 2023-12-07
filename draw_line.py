import numpy as np
import cv2

def drawline(img,pt1,pt2,color,thickness=1.5,style='dotted',gap=20):
    dist =((pt1[0]-pt2[0])**2+(pt1[1]-pt2[1])**2)**.5
    pts= []
    for i in  np.arange(0,dist,gap):
        r=i/dist
        x=int((pt1[0]*(1-r)+pt2[0]*r)+.5)
        y=int((pt1[1]*(1-r)+pt2[1]*r)+.5)
        p = (x,y)
        pts.append(p)

    if style=='dotted':
        for p in pts:
            cv2.circle(img,p,thickness,color,-1)
    else:
        s=pts[0]
        e=pts[0]
        i=0
        for p in pts:
            s=e
            e=p
            if i%2==1:
                cv2.line(img,s,e,color,thickness)
            i+=1



# drawline(frame, (A_right_boundary, A_start[0]), (A_right_boundary, A_end[0]), text_color, 2, 'line')
# drawline(frame, (A_left_boundary, A_start[0]), (A_left_boundary, A_end[0]), text_color, 2, 'line')

# drawline(frame, (B_right_boundary, B_start[0]), (B_right_boundary, B_end[0]), text_color, 2, 'line')
# drawline(frame, (B_left_boundary, B_start[0]), (B_left_boundary, B_end[0]), text_color, 2, 'line')

# drawline(frame, (C_start[1], C_right_boundary), (C_end[1], C_right_boundary), text_color, 2, 'line')
# drawline(frame, (C_start[1], C_left_boundary), (C_end[1], C_left_boundary), text_color, 2, 'line')