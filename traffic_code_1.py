# this code creates a simulate which consists of a complex road network and employs set timer signal control system.

# A video of the simualtion created by this code can be found at: https://www.youtube.com/watch?v=CfFbRqDhEjk&t


import time
import threading
from threading import *
from tkinter import *
import math
import statistics
import random
from statistics import mode

tk = Tk()#initialises tk setup
canvas = Canvas(tk, width=1100, height=800)
tk.title("Drawing")
canvas.pack() #create window show it on the screen
tk.update()
running_check = 1

#####
class Control_display:
    def __init__(self,x2, y2,lanes_test,id_num,lw_half):
        self.colour = "blank"
        lane_angle_from_vert = lanes_test[id_num].points_with_angles[-2][2] # angle leaving second last point, ie. the angle approaching the last point
        lane_end_x = lanes_test[id_num].points[-1][0]
        lane_end_y = lanes_test[id_num].points[-1][1]
        offset_dist = int(lw_half/2)
        x_offset = offset_dist*math.sin(lane_angle_from_vert)
        y_offset = offset_dist*math.cos(lane_angle_from_vert)
        light_centre_x = lane_end_x + x_offset
        light_centre_y = lane_end_y - y_offset

        light_angle_from_vert = lane_angle_from_vert - (math.pi/2)

        # light_length = int(lw_half/1)
        light_length = int(lw_half/1.5)
        # light_width = int(lw_half/2)
        light_width = int(lw_half/3)

        front_side_point_x = light_centre_x + light_length*math.sin(light_angle_from_vert)
        front_side_point_y = light_centre_y - light_length*math.cos(light_angle_from_vert)
        rear_side_point_x = light_centre_x - light_length*math.sin(light_angle_from_vert)
        rear_side_point_y = light_centre_y + light_length*math.cos(light_angle_from_vert)

        x1_corner = front_side_point_x + light_width*math.sin(light_angle_from_vert - (math.pi/2))
        y1_corner = front_side_point_y - light_width*math.cos(light_angle_from_vert - (math.pi/2))

        x2_corner = front_side_point_x - light_width*math.sin(light_angle_from_vert - (math.pi/2))
        y2_corner = front_side_point_y + light_width*math.cos(light_angle_from_vert - (math.pi/2))

        x3_corner = rear_side_point_x - light_width*math.sin(light_angle_from_vert - (math.pi/2))
        y3_corner = rear_side_point_y + light_width*math.cos(light_angle_from_vert - (math.pi/2))

        x4_corner = rear_side_point_x + light_width*math.sin(light_angle_from_vert - (math.pi/2))
        y4_corner = rear_side_point_y - light_width*math.cos(light_angle_from_vert - (math.pi/2))

        # canvas.coords(self.body, x1_corner,y1_corner, x2_corner,y2_corner, x3_corner,y3_corner, x4_corner,y4_corner)

        # self.light = canvas.create_oval(light_centre_x-2,light_centre_y-2,light_centre_x+2,light_centre_y+2)
        self.light = canvas.create_polygon(x1_corner,y1_corner, x2_corner,y2_corner, x3_corner,y3_corner, x4_corner,y4_corner)
        self.lane  = id_num
        # if lanes[id_num].orien == 3:#'l_to_r':
        #     self.light = canvas.create_rectangle(x2+int(lw/10),y2+int(lw/5),x2+(2*(int(lw/10))),y2+(lw)-int(lw/5),outline="")
        #     self.lane = id_num
        # if lanes[id_num].orien == 1:#'r_to_l':
        #     self.light = canvas.create_rectangle(x2-int(lw/10),y2+int(lw/5),x2-(2*(int(lw/10))),y2+(lw)-int(lw/5), outline="")
        #     self.lane = id_num
        # if lanes[id_num].orien == 0:#'t_to_b':
        #     self.light = canvas.create_rectangle(x2-int(lw/5),y2+int(lw/10),x2-(lw)+int(lw/5),y2+(2*(int(lw/10))),outline="")
        #     self.lane = id_num
        # if lanes[id_num].orien == 2:#'b_to_t':
        #     # print("running")
        #     self.light = canvas.create_rectangle(x2+int(lw/5),y2-int(lw/10),x2+(lw)-int(lw/5),y2-(2*(int(lw/10))),outline="")
        #     # canvas.create_rectangle(x2+7,y2+7,x2-7,y2-7,fill = "green")
        #     self.lane = id_num
    def turn_light_green(self):
        self.colour = "green"
        canvas.itemconfig(self.light, fill="green")
        canvas.itemconfig(self.light, outline="green")
    def turn_off_light(self):
        self.colour = "blank"
        canvas.itemconfig(self.light, fill="")
        canvas.itemconfig(self.light, outline="")
    def turn_light_red(self):
        self.colour = "red"
        canvas.itemconfig(self.light, fill="red")
        canvas.itemconfig(self.light, outline="red")
#####
class Car:
    def __init__(self, pos_x, pos_y,i):
        self.id = i
        self.time = 0
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.angle = 0
        self.pos_x_temp = pos_x
        self.pos_y_temp = pos_y
        self.coords = [pos_x, pos_y]
        self.coord_x_hist = []
        self.coord_y_hist = []
        self.current_lane = 9999
        self.previous_lane = 9999
        self.next_lane = 9999
        self.current_zone = 9999
        self.next_zone = 9999
        self.start_zone = 9999
        self.end_zone = 9999
        self.colour = random.choice(colour_choice)
        self.time_in_sys = 0
        self.wait_score = 0
        self.compass = random.uniform(0,math.pi)
        # self.perimeter = canvas.create_rectangle((pos_x-10),(pos_y-10),(pos_x+10),(pos_y+10),dash=(4, 2))
        # self.body = canvas.create_rectangle((pos_x - 1),(pos_y - 2),(pos_x + 1),(pos_y + 2),fill = self.colour)
        # self.body = canvas.create_rectangle((pos_x - 10),(pos_y - 20),(pos_x + 10),(pos_y + 20),fill = self.colour)
        # self.body = canvas.create_polygon((pos_x - 10),(pos_y - 20), (pos_x - 10),(pos_y + 20), (pos_x + 10),(pos_y + 20), (pos_x + 10),(pos_y - 20), fill = self.colour)
        self.body = canvas.create_polygon(100,200, 100,400, 200,400, 200,200, fill = self.colour)
        self.path_opt = 0# this is the path option the car will follow from the set paths
        self.g_zone = 99
        self.g_avg_x = 0
        self.g_avg_y = 0
        self.path_step = 0
        self.potential_lanes = []
        self.potential_lanes_common = []
        self.potential_points = []
        self.potential_lanes_1 = []
        self.potential_points_1 = []
        self.potential_lanes_2 = []
        self.potential_points_2 = []
        self.potential_points_common = []
        self.loca_lane = 99
        self.pot_next_points_with_lane_id = []
        self.move_check_store = []
        self.localised = 0 # if 0 = not localised, if 1 = localised, if 2 = trieed to localised but unable to so only need to run
        self.g_lane = 99
        self.fut_pos = [] # 1st value is x coord, 2nd value is y coord, 3rd value is orientation (1 = vertical, 0 = horizontal)
        self.fut_pos_psuedo = []
        self.lane_history = [] #stores the path through the lanes the car has taken
        self.space_to_change_lane = 0 #if there is space for car in next lane this = 1, if no space = 0, if exiting = 2
        self.step = 0
        self.step_in_current_lane = 0
        self.step_tracker = []
        self.move_status = 0
        self.current_end_pos = []
        self.wait_time = 0
        self.move_time = 0
        self.time_in_system = 0
        self.car_in_system = 0 # 0 represents FALSE, 1 represents TRUE
        self.wait_time_to_enter_system = 0
        self.car_waiting_to_enter_system = 0 # 0 represents FALSE, 1 represents TRUE
        self.wait_time_in_queue = 0
        self.car_waiting_in_queue = 0 # 0 represents FALSE, 1 represents TRUE
        self.move_time = 0
        self.car_moving = 0 # 0 represents FALSE, 1 represents TRUE
        self.lane_step = 0
        self.path = []
        self.localised = 0
        self.localised_stage = 0
        self.orig_coords = []
        self.recent_coords = []
        self.g_track_path = []
        self.g_lane_line_tracker = []
        self.g_lane_temp = 99
        self.g_wait_time = 0
        self.sampling_check = 0
        self.side_points_1 = []
        self.side_points_2 = []
        self.front_queue_check = 0
        self.current_end_step = 0
        self.current_end_step_tracker = []
        self.current_lane_end_step = 0
        self.updated_current_end_step = 0
        self.end_step_for_current_lane = 0
        self.move_status_tracker = []
        self.potential_lanes_lines_1 = []
        self.dist_lane_forward_points_1 = []
        self.potential_lanes_lines_2 = []
        self.localisation_lanes_common = []
        self.dist_lane_forward_points_lanes_common = []
        self.sampling_checker = 0


    def car_on_angle(self,pos_x,pos_y,car_width,car_length,car_angle_from_vert):
        #canvas.coords(self.body,(pos_x - 20),(pos_y - 10),(pos_x + 20),(pos_y + 10))
        # offset_store =
        side_1_point_x = pos_x - car_width*math.cos(car_angle_from_vert - (math.pi/2))
        side_1_point_y = pos_y - car_width*math.sin(car_angle_from_vert - (math.pi/2))
        side_2_point_x = pos_x + car_width*math.cos(car_angle_from_vert - (math.pi/2))
        side_2_point_y = pos_y + car_width*math.sin(car_angle_from_vert - (math.pi/2))

        x1 = side_1_point_x + car_length*math.sin(car_angle_from_vert)
        y1 = side_1_point_y + car_length*math.cos(car_angle_from_vert)
        x2 = side_1_point_x - car_length*math.sin(car_angle_from_vert)
        y2 = side_1_point_y - car_length*math.cos(car_angle_from_vert)
        x3 = side_2_point_x - car_length*math.sin(car_angle_from_vert)
        y3 = side_2_point_y - car_length*math.cos(car_angle_from_vert)
        x4 = side_2_point_x + car_length*math.sin(car_angle_from_vert)
        y4 = side_2_point_y + car_length*math.cos(car_angle_from_vert)

        x1t = pos_x + car_length*math.sin(car_angle_from_vert)
        y1t = pos_y - car_length*math.cos(car_angle_from_vert)


        front_side_point_x = pos_x + car_length*math.sin(car_angle_from_vert)
        front_side_point_y = pos_y - car_length*math.cos(car_angle_from_vert)
        rear_side_point_x = pos_x - car_length*math.sin(car_angle_from_vert)
        rear_side_point_y = pos_y + car_length*math.cos(car_angle_from_vert)

        x1_corner = front_side_point_x + car_width*math.sin(car_angle_from_vert - (math.pi/2))
        y1_corner = front_side_point_y - car_width*math.cos(car_angle_from_vert - (math.pi/2))

        x2_corner = front_side_point_x - car_width*math.sin(car_angle_from_vert - (math.pi/2))
        y2_corner = front_side_point_y + car_width*math.cos(car_angle_from_vert - (math.pi/2))

        x3_corner = rear_side_point_x - car_width*math.sin(car_angle_from_vert - (math.pi/2))
        y3_corner = rear_side_point_y + car_width*math.cos(car_angle_from_vert - (math.pi/2))

        x4_corner = rear_side_point_x + car_width*math.sin(car_angle_from_vert - (math.pi/2))
        y4_corner = rear_side_point_y - car_width*math.cos(car_angle_from_vert - (math.pi/2))

        points_test = [pos_x,pos_y,rear_side_point_x,rear_side_point_y]           # ,front_side_point_x,front_side_point_y] # ,rear_side_point_x,rear_side_point_y]
        points_test_1 = [pos_x,pos_y,front_side_point_x,front_side_point_y]
        points_test_corner_1 = [pos_x,pos_y,x1_corner,y1_corner]
        points_test_corner_2 = [pos_x,pos_y,x2_corner,y2_corner]
        points_test_corner_3 = [pos_x,pos_y,x3_corner,y3_corner]
        points_test_corner_4 = [pos_x,pos_y,x4_corner,y4_corner]
        points_new = [x1_corner,y1_corner,x2_corner,y2_corner,x3_corner,y3_corner,x4_corner,y4_corner]

        car_points = [x1_corner,y1_corner,x2_corner,y2_corner,x3_corner,y3_corner,x4_corner,y4_corner]
        # canvas.create_polygon(car_points, outline='#f11', fill='#1f1', width=2)
        # 315.0, 431.0, 315.0, 471.0, 315.0, 479.0, 315.0, 439.0]

        x_offset = car_length*math.sin(car_angle_from_vert)
        y_offset = car_length*math.cos(car_angle_from_vert)

        # print("coords: " + str(car_points))
        # canvas.coords(self.body, 315.0, 431.0, 315.0, 471.0, 315.0, 479.0, 315.0, 439.0)
        canvas.coords(self.body, x1_corner,y1_corner, x2_corner,y2_corner, x3_corner,y3_corner, x4_corner,y4_corner)

    def car_horz(self,pos_x,pos_y,car_width,car_length):
        #canvas.coords(self.body,(pos_x - 20),(pos_y - 10),(pos_x + 20),(pos_y + 10))
        canvas.coords(self.body,(pos_x - car_length),(pos_y - car_width),(pos_x + car_length),(pos_y + car_width))
    def car_vert(self,pos_x,pos_y,car_width,car_length):
        #canvas.coords(self.body,(pos_x - 10),(pos_y - 20),(pos_x + 10),(pos_y + 20))
        canvas.coords(self.body,(pos_x - car_width),(pos_y - car_length),(pos_x + car_width),(pos_y + car_length))
#####
class Lane_test:
    def __init__(self,junc_pos,points): # ,diff_x,diff_y,abs_diff_x,abs_diff_y,theta,line_grad,line_len,angle_from_vert,line_quadrant):
        #self.boundary = canvas.create_rectangle(x1, y1, x2, y2)
        self.lane_id = 0
        self.map_lane_id = 0 # map_lane_id is the reference on the visual map, this will not always equal lane_id as certain numbers may be missed when creating the map and numbering the lanes
        self.points = points # [x,y] point coordinates
        self.junc_pos = junc_pos # 2 if enters junc from side, 1 if from top or bottom, 0 doesn'y entry as is an interior point
        self.points_with_info = [] # [x,y,status,junc_pos] if first point in lane status = 1, if interior point in lane status = 2, if last point in lane status = 3; junc_pos is the position in which lane enters the junction, if junc_pos = 1 lane top or bottom (horizontal lane end) entry/exit, if junc_pos = 2 lane side (vertical lane end) entry/exit, if internal ppoint junc_pos = 0
        self.lines_info = [] # [diff_x,diff_y,abs_diff_x,abs_diff_y,theta,line_grad,line_len,angle_from_vert,line_quadrant]
        self.lines = [] # [[p1x,p1y,p2x,p2y,angle_from_vert, quadrant, line_length],[p2x,p2y,p3x,p3y,angle_from_vert, quadrant, line_length]]
        self.draw = [] #[[p1x,p1y,angle_at_1,p2x,py2,angle_at_2,angle_from_vert,quadrant],[p2x,p2y,angle_at_2,p3x,py3,angle_at_3,angle_from_vert,quadrant]]
        self.points_min = [] # [[x1,y1,status,junc_pos,angle_from_vert_at_point], [x2,y2,...],...]
        # self.points_with_angles = [] # [[x1,y1,angle_from_vert_at_point,line_quadrant going from point, angle of line of side points], [x2,y2,...],...]
        self.points_with_angles = [] # [[x1,y1,angle_of line_leaving_point_from_vertical,line_quadrant going from point, angle of line of side points], [x2,y2,...],...]
        self.points_outer_line = []
        self.points_inner_line = []
        self.angle_side_points_on = []
        self.side_points = []
        self.upper_line_points = []
        self.lower_line_points = []
        self.points_info_min = [] # [[x1,y1,angle_of_line_leaving_point], [x2,y2,angle_of_line_leaving_point]]
        self.move_points = [] # stores all the points the cars will use to navigate along lins in lane
        self.cars_in_lane_id = []
        self.next_lanes = [] # lanes folllowing on from this lane
        self.next_map_lanes_id = []
        self.assoc_lanes = [] # lanes that run in conjuction with this lane, ie. lanes in the same direction next to each other
        self.free_turn_next_lanes = [] # these are next_lanes that the car can move into freely, ie. no controlled by a traffic light, just a simple turn and move into lane if there is space
        self.free_turn_next_lanes_map_id = []
        self.end_point_for_free_turn_next_lanes = [] #[[next_lane,x value for end_point_in_current_lane_for_moving_to_next_lane,y value for end_point_in_current_lane_for_moving_to_next_lane],[...]]
        self.free_turn_next_lane_points = [] # [[next_lane,point1x,point1y],[next_lane,point2x,point2y]]
        self.free_turn_next_lane_points_with_angles = [] # [[next_lane,[point1x,point1y,angle_line_leaving]],[..[...,...]]]
        self.free_turn_next_lane_move_points = [] # [[next_lane2,[move_point1x,move_point1y,angle_from_vert],[move_point2x,move_point2y,angle_from_vert],[...]],[next_lane2,[...,...]]]
        self.current_end_step = 0
        self.next_lanes_intersection = [] # [[next_lane_option,intersection_point_x,intersection_point_y],[next_lane_option,...]]
        self.next_lanes_transition_points = [] # [[next_lane_option,transition_point1_x, transition_point_1_y,angle_line_leaving_move_point],[next_lane_option,transition_point_2_x,transition_point_2_y,angle_leaving_move_point_2],...]         # used to find the transition_points between lane, include last point of current lane, intersction points, and first point of next lane
        self.move_points_next_lanes = [] # [[next_lane],[move_points....]]
        self.free_turn_next_lanes_intersection = []
        self.control_num = 0
        self.green_light = 0
        self.time_green = 0
        self.light_time_pause = 0
        self.g_lane_wait_time_total = 0
        self.g_cars_in_lane_id = []

class Junc_test:
    def __init__(self,junc_num,lanes_at_junc_map_id):
        self.junc_id = junc_num
        self.centre_x = 0
        self.centre_y = 0
        self.lanes_at_junc_map_id = lanes_at_junc_map_id
        self.lanes_at_junc = []
        self.light_lanes_at_junc = []
        self.g_junc_total_points = 0
        self.g_cars_in_junc_id = []
        self.g_num_cars_in_junc = 0
        self.best_score = 0
        self.best_zone = 0
        self.num_cars_to_pass = 0
        self.time_green = 0
        self.lane_orien_temp = 0
        self.g_junc_wait_time_total = 0
        self.ready_for_green = 0
        self.green_lanes_at_junc = 0
        self.same_light_lanes_link_map_id = 0
        self.same_light_lanes_link = []

def create_coord(cars,car_id,rad_gps):
    theta = random.uniform(0,2*math.pi)
    r = round(random.uniform(0,rad_gps),3) # 8m is the assumed radius of gps uncertainty
    x_dev = r * math.cos(theta)
    y_dev = r * math.sin(theta)
    # cars[car_id].coords[0] = cars[car_id].pos_x_temp + x_dev
    cars[car_id].coords[0] = cars[car_id].pos_x + x_dev
    cars[car_id].coords[0] = int(cars[car_id].coords[0]) # set to integer to remove the decimal places
    # cars[car_id].coords[1] = cars[car_id].pos_y_temp + y_dev
    cars[car_id].coords[1] = cars[car_id].pos_y + y_dev
    cars[car_id].coords[1] = int(cars[car_id].coords[1]) # set to integrate to remove the decimal places
    cars[car_id].coord_x_hist.append(cars[car_id].coords[0])
    cars[car_id].coord_y_hist.append(cars[car_id].coords[1])

# set dimensions
scale_factor = 1
block_len = int(80/scale_factor)
rad_gps = int(10/scale_factor)
car_length = int(4/scale_factor)
half_car_length = int(car_length/2)
car_width = int(2/scale_factor)
lw = int(3/scale_factor)
lw_half = round(lw/2)
move_val = half_car_length # the size of each step
move_val = 2 # need to change this
car_spacing = int(car_length/4)
num_steps_per_block = int(block_len/move_val)
 # want speed to be 20.1 mph, which is equal to 9 ms-1
time_to_travel_block = int(block_len/(9/scale_factor))
time_interval = 0.1796
sampling_time = time_interval * 50 # if in realtime will equal 5
sampling_time = 5

controls = [] #stores control object data
lanes_test = []
juncs_test = []

colour_choice = [["black"],["black"]]

tdx = block_len
tdy = block_len
stx = 0 #the min point in x direction
sty= 0 #the min point in y direction
# lanes_test = [[[200,200],[300,200],[300,400]] ] #,[[400,400],[500,500]]]

x1 = (200+lw+lw_half)
y1 = (200+(2*lw))
x2 = (200+lw+lw_half)
y2 = (300+lw+lw_half)
x3 = 50
y3 = (300+lw_half+lw)

### Create the road network by inputting the coordinates of each lane.
def lanes_test_info(lanes_test):

    lanes_test.append(Lane_test([0,0],[[198, 132],[100, 132]])) # 0
    lanes_test.append(Lane_test([0,0],[[367, 132],[206, 132]])) # 1
    lanes_test.append(Lane_test([0,0],[[200, 130],[200, 7]])) # 2
    lanes_test.append(Lane_test([0,0],[[558, 132],[376, 132]])) # 3
    lanes_test.append(Lane_test([0,0],[[204, 7],[204, 130]])) # 4
    lanes_test.append(Lane_test([0,0],[[566, 132],[681, 127]])) # 5
    lanes_test.append(Lane_test([0,0],[[370, 130],[370, 7]])) # 6
    lanes_test.append(Lane_test([0,0],[[681, 131],[566, 136]])) # 7
    lanes_test.append(Lane_test([0,0],[[374, 7],[374, 130]])) # 8
    lanes_test.append(Lane_test([0,0],[[25, 302],[198, 302]])) # 9
    lanes_test.append(Lane_test([0,0],[[560, 130],[560, 15]])) # 10
    lanes_test.append(Lane_test([0,0],[[206, 302], [367, 302]])) # 11
    lanes_test.append(Lane_test([0,0],[[564, 15], [564, 130]])) # 12
    lanes_test.append(Lane_test([0,0],[[376, 302],[465, 302]])) # 13
    lanes_test.append(Lane_test([0,0],[[684, 70],[684, 125]])) # 14
    lanes_test.append(Lane_test([0,0],[[470, 302],[558, 302]])) # 15
    lanes_test.append(Lane_test([0,0],[[200, 300],[200, 134]])) # 16
    lanes_test.append(Lane_test([0,0],[[376, 212],[465, 212]])) # 17
    lanes_test.append(Lane_test([0,0],[[204, 134],[204, 300]])) # 18
    lanes_test.append(Lane_test([0,0],[[470, 212],[558,214]])) # 19
    lanes_test.append(Lane_test([0,0],[[370, 300],[370, 135]])) # 20
    lanes_test.append(Lane_test([0,0],[[567, 302],[682, 302]])) # 21
    lanes_test.append(Lane_test([0,0],[[374, 135],[374, 300]])) # 22
    lanes_test.append(Lane_test([0,0],[[686, 302],[742, 302]])) # 23
    # lanes_test.append(Lane_test([2,2],[[ # 24
    lanes_test.append(Lane_test([0,0],[[464, 369],[376, 369]])) # 25
    lanes_test.append(Lane_test([0,0],[[467, 134],[467, 210]])) # 26
    lanes_test.append(Lane_test([0,0],[[558, 369],[469, 369]])) # 27
    lanes_test.append(Lane_test([0,0],[[467, 214],[467, 300]])) # 28
    lanes_test.append(Lane_test([0,0],[[377, 492],[465, 492]])) # 29
    lanes_test.append(Lane_test([0,0],[[560, 212],[560, 139]])) # 30
    lanes_test.append(Lane_test([0,0],[[376, 587],[526, 587]])) # 31
    lanes_test.append(Lane_test([0,0],[[560, 300],[560, 216]])) # 32
    lanes_test.append(Lane_test([0,0],[[558, 591],[376, 591]])) # 33
    lanes_test.append(Lane_test([0,0],[[564, 212],[564, 139]])) # 34
    lanes_test.append(Lane_test([0,0],[[531, 587],[558, 587]])) # 35
    lanes_test.append(Lane_test([0,0],[[684, 133],[684, 300]])) # 36
    lanes_test.append(Lane_test([0,0],[[567, 587],[664, 587]])) # 37
    lanes_test.append(Lane_test([2,1],[[367, 591],[287, 586],[286, 478],[207, 478],[200, 304]])) # 38
    lanes_test.append(Lane_test([0,0],[[672, 587],[811, 587]])) # 39
    lanes_test.append(Lane_test([1,2],[[204, 304],[211, 474],[290, 474],[291, 582],[369, 587]])) # 40
    lanes_test.append(Lane_test([0,0],[[811, 591],[672, 591]])) # 41
    lanes_test.append(Lane_test([1,2],[[261, 305],[368, 494]])) # 42
    lanes_test.append(Lane_test([0,0],[[664, 591],[567, 591]])) # 43
    lanes_test.append(Lane_test([0,0],[[370, 490],[370, 304]])) # 44
    lanes_test.append(Lane_test([0,0],[[374, 304],[374, 367]])) # 46
    lanes_test.append(Lane_test([0,0],[[374, 372],[374, 490]])) # 48
    lanes_test.append(Lane_test([0,0],[[370, 585],[370, 495]])) # 50
    lanes_test.append(Lane_test([0,0],[[374, 495],[374, 585]])) # 52
    lanes_test.append(Lane_test([0,0],[[467, 304],[467, 367]])) # 54
    lanes_test.append(Lane_test([0,0],[[467, 371],[467, 490]])) # 56
    lanes_test.append(Lane_test([2,1],[[470, 492],[529, 585]])) # 58
    lanes_test.append(Lane_test([0,0],[[467, 585],[467, 494]])) # 60
    lanes_test.append(Lane_test([0,0],[[560, 585],[560, 371]])) # 62
    lanes_test.append(Lane_test([0,0],[[564, 585],[564, 371]])) # 64
    lanes_test.append(Lane_test([0,2],[[666, 585],[666, 426],[566, 369]])) # 66
    lanes_test.append(Lane_test([0,0],[[670, 585],[670, 426],[746, 356],[744, 304]])) # 68
    lanes_test.append(Lane_test([0,0],[[746, 302],[810, 304],[797, 345]])) # 70
    lanes_test.append(Lane_test([0,0],[[916, 407],[797, 347]])) # 71
    lanes_test.append(Lane_test([0,0],[[370, 708],[370, 593]])) # 72
    lanes_test.append(Lane_test([0,0],[[374, 593],[374, 708]])) # 74
    lanes_test.append(Lane_test([0,0],[[560, 708],[560, 593]])) # 76
    lanes_test.append(Lane_test([0,0],[[564, 593],[564, 708]])) # 78
    lanes_test.append(Lane_test([0,0],[[813, 593],[813, 708]])) # 80
    lanes_test.append(Lane_test([0,0],[[560, 367],[560, 304]])) # 82
    lanes_test.append(Lane_test([0,0],[[564, 367],[564, 304]])) # 84
    lanes_test.append(Lane_test([0,0],[[794, 349],[766, 431],[814, 434],[813, 585]])) # 86
    lanes_test.append(Lane_test([0,0],[[564, 300],[564, 214]])) # 88
lanes_test_info(lanes_test)
### Assign lanes to the junctions.
def juncs_test_info(juncs_test):
    juncs_test.append(Junc_test(0,[4,1,16])) # 0
    juncs_test.append(Junc_test(1,[8,3,20])) # 1
    juncs_test.append(Junc_test(2,[12,7,34,30])) # 2
    juncs_test.append(Junc_test(3,[14,5])) # 3
    juncs_test.append(Junc_test(4,[26,17])) # 4
    juncs_test.append(Junc_test(5,[32,19])) # 5
    juncs_test.append(Junc_test(6,[9,18,38])) # 6
    juncs_test.append(Junc_test(7,[11,22,44])) # 7
    juncs_test.append(Junc_test(8,[28,13])) # 8
    juncs_test.append(Junc_test(9,[15,82,84])) # 9
    juncs_test.append(Junc_test(10,[21,36])) # 10
    juncs_test.append(Junc_test(11,[46,25])) # 11
    juncs_test.append(Junc_test(12,[54,27])) # 12
    juncs_test.append(Junc_test(13,[66,64,62])) # 13
    juncs_test.append(Junc_test(14,[23,68])) # 14
    juncs_test.append(Junc_test(15,[71,70])) # 15
    juncs_test.append(Junc_test(16,[42,48,50])) # 16
    juncs_test.append(Junc_test(17,[29,56,60])) # 17
    juncs_test.append(Junc_test(18,[72,40,52,33])) # 18
    juncs_test.append(Junc_test(19,[31,58])) # 19
    juncs_test.append(Junc_test(20,[35,43,76])) # 20
    juncs_test.append(Junc_test(21,[37,41])) # 21
    juncs_test.append(Junc_test(22,[86,39])) # 22

    same_light_lanes_link_map_id =[[4,1,16],[8,3,20],[12,7,[34,30]],[14,5],[26,17],[32,19],[9,18,38],[11,22,44],[28,13],[15,[82,84]],[21,36],[46,25],[54,27],[66,[64,62]],[23,68],[71,70],[42,48,50],[29,56,60],[72,40,52,33],[31,58],[35,43,76],[37,41],[86,39]]

    for i in range(len(juncs_test)):
        juncs_test[i].same_light_lanes_link_map_id = same_light_lanes_link_map_id[i]
juncs_test_info(juncs_test)
def find_line_info(point_1,point_2):
    # find angle of line from vertical in clockwise rotation
    # print("point1: " + str(point_1) + " point_2: " + str(point_2))
    diff_x = point_2[0] - point_1[0] # point 2 is further down lane than point 1
    diff_y = point_2[1] - point_1[1]
    abs_diff_x = abs(diff_x)
    abs_diff_y = abs(diff_y)
    # initially set line_quadrant to 0
    line_quadrant = 0
    if (abs_diff_x  == 0) or (abs_diff_y == 0):
        theta = 0
    else:
        theta = math.atan(abs_diff_x/abs_diff_y)
    if diff_y == 0:
        line_grad = 0
    elif diff_x == 0 and diff_y > 0:
        line_grad = 1
    elif diff_x == 0 and diff_y < 0:
        line_grad = -1
    else:
        line_grad = diff_y / diff_x
    line_len = math.sqrt((diff_x**2) + (diff_y**2))
    if diff_x >= 0  and diff_y < 0 : # quadrant-1
        if (abs_diff_x  == 0) or (abs_diff_y == 0):
            theta = 0
        else:
            theta = math.atan(abs_diff_x/abs_diff_y)
        angle_from_vert = theta #
        line_quadrant = 1
        # print("quad1: "+ str(math.degrees(angle_from_vert)))
    if diff_x > 0 and diff_y >= 0: # quadrant-2
        if (abs_diff_x  == 0) or (abs_diff_y == 0):
            theta = 0
        else:
            theta = math.atan(abs_diff_y/abs_diff_x)
        angle_from_vert = (math.pi/2) +  theta    ############################## doesn't work for theta = 0, theta should be 90 degrees
        line_quadrant = 2
        # print("quad2: "+ str(math.degrees(angle_from_vert)))
    if diff_x <= 0 and diff_y > 0: # quadrant-3
        if (abs_diff_x  == 0) or (abs_diff_y == 0):
            theta = 0
        else:
            theta = math.atan(abs_diff_x/abs_diff_y)
        angle_from_vert = (math.pi + theta)
        line_quadrant = 3
        # print("quad3: "+ str(math.degrees(angle_from_vert)))
    if diff_x < 0 and diff_y <= 0: # quadrant-4
        if (abs_diff_x  == 0) or (abs_diff_y == 0):
            theta = 0
        else:
            theta = math.atan(abs_diff_y/abs_diff_x)
        angle_from_vert = (3*math.pi/2) + theta
        line_quadrant = 4
    # if diff_x == 0 and diff_y == 0:
    #     theta = 0
    #     angle_from_vert = theta

        # print("quad4: "+ str(math.degrees(angle_from_vert)))
    # return(diff_x,diff_y,abs_diff_x,abs_diff_y,theta,line_grad,line_len,angle_from_vert,line_quadrant)
    # return(point_1[0],point_1[1],point_2[0],point_2[1],angle_from_vert,line_quadrant,line_len)
    return(line_quadrant,angle_from_vert)
    # return(angle_from_vert)
######

lanes_next_lanes_map_id = [[9999],[2,18,0],[9999],[22,1,6,26],[18,0],[36],[9999],[3,10],[22,1],[16,11,40],[9999],[20,13,46,42],[5,3],[15,54],[36,7],[32,21,88],[0,2],[19,28],[11,40],[30],[1,6],[23],[13,46,17],[70],[],[48],[19,28],[56,25],[15,54],[58],[3],[60,35],[30],[74,38,50],[5],[62,37,78],[23],[66,68,39],[16,11],[80],[50,31,74],[43,66,68],[44,29,52],[78,33,62,64],[20,13],[],[48],[],[29,52],[],[44,29],[],[31,74,38],[],[56,25],[],[58],[],[35],[],[58],[],[27,82],[],[84],[],[27,82,84],[],[70],[],[86],[86],[38,50,31],[],[9999],[],[33,62,64,37],[],[9999],[],[9999],[],[32],[],[88,21],[],[80,41],[],[34]]

# generate associated lanes, ie. lanes next to each other moving in the same direction
map_lanes_assoc_lanes = [[62,64],[82,84],[32,88],[30,34]]
# generate free turn next lanes, ie. lanes cars can move into freely as not controlled by traffic light
map_free_turn_next_lanes = [[31,60],[22,17],[3,26],[11,42],[88,34]]    # this means cars in lane 31 can freely move into lane 60 BUT NOT VICE VERSA
# identify map_entry_lanes
map_entry_lanes = [4,8,12,14,72,76,71,9]
entry_lanes = []
# identify map_exit_lanes
map_exit_lanes = [0,2,6,10,80,78,74]
exit_lanes = []

def assign_lanes_map_lane_id(lanes_test,lanes_next_lanes_map_id):
    lane_counter = 0
    for i in range(len(lanes_next_lanes_map_id)):
        if len(lanes_next_lanes_map_id[i]) > 0:
            lanes_test[lane_counter].map_lane_id = i
            lane_counter += 1
assign_lanes_map_lane_id(lanes_test,lanes_next_lanes_map_id)

def assign_next_map_lanes_id_and_free_turn_next_lanes_map_id(lanes_test,lanes_next_lanes_map_id,map_lanes_assoc_lanes):
    # for i in range(len(lanes_test)):
    #     lanes_test[i].next_lanes = lanes_next_lanes[i]
    for k in range(len(lanes_test)):
        lanes_test[k].next_map_lanes_id = lanes_next_lanes_map_id[lanes_test[k].map_lane_id]
        for t in range(len(map_free_turn_next_lanes)):
            if lanes_test[k].map_lane_id == map_free_turn_next_lanes[t][0]:
                map_free_turn_next_lanes_temp = map_free_turn_next_lanes[t][1:]
                lanes_test[k].free_turn_next_lanes_map_id.append( map_free_turn_next_lanes_temp) # append all the following free_turn_amp_lane_ids
                lanes_test[k].free_turn_next_lanes_map_id = lanes_test[k].free_turn_next_lanes_map_id[0]
assign_next_map_lanes_id_and_free_turn_next_lanes_map_id(lanes_test,lanes_next_lanes_map_id,map_lanes_assoc_lanes)

def assign_next_lanes_and_free_turn_next_lanes(lanes_test):
    for i in range(len(lanes_test)):
        lanes_test[i].lane_id = i
        for k in lanes_test[i].next_map_lanes_id:
            if k == 9999:
                lanes_test[i].next_lanes.append(k)
            else:
                next_map_lane_id = k
                for r in range(len(lanes_test)):
                    lane_id_r = r
                    if lanes_test[lane_id_r].map_lane_id == next_map_lane_id:
                        # this is the lane id for a next map lane
                        lanes_test[i].next_lanes.append(lane_id_r)
        for t in lanes_test[i].free_turn_next_lanes_map_id:
            if t == 9999:
                lanes_test[i].free_turn_next_lanes.append(t)
            else:
                free_turn_next_lane_id = t
                for q in range(len(lanes_test)):
                    lane_id_q = q
                    if lanes_test[lane_id_q].map_lane_id ==  free_turn_next_lane_id:
                        # this is the lane id for a free turn map lane
                        lanes_test[i].free_turn_next_lanes.append(lane_id_q)
assign_next_lanes_and_free_turn_next_lanes(lanes_test)

def assign_lane_id_at_junc(juncs_test):
    for i in range(len(juncs_test)):
        for j in juncs_test[i].lanes_at_junc_map_id:
            for k in range(len(lanes_test)):
                if lanes_test[k].map_lane_id == j:
                    true_lane_id = k
                    juncs_test[i].lanes_at_junc.append(true_lane_id)
         # assign lanes to same_light_lanes_link from same_light_lanes_link_map_id
        for r in juncs_test[i].same_light_lanes_link_map_id: # loop through the lanes
            # print("juncs_test[i].same_light_lanes_link_map_id[r]: " + str(juncs_test[i].same_light_lanes_link_map_id[r]))
            temp = []
            if type(r) == int:
                for k in range(len(lanes_test)):
                    if lanes_test[k].map_lane_id == r:
                        true_lane_id = k
                        juncs_test[i].same_light_lanes_link.append(true_lane_id)
            else:
                for y in r:
                    for k in range(len(lanes_test)):
                        if lanes_test[k].map_lane_id == y:
                            true_lane_id = k
                            temp.append(true_lane_id)
                juncs_test[i].same_light_lanes_link.append(temp)

    # assign first green_lanes_at_junc
    for i in range(len(juncs_test)):
        juncs_test[i].green_lanes_at_junc = juncs_test[i].lanes_at_junc[0] #.append(juncs_test[i].lanes_at_junc[0]) #  = juncs_test[i].lanes_at_junc[0]
assign_lane_id_at_junc(juncs_test)

def assign_associate_lanes(lanes_test,map_lanes_assoc_lanes):
    for i in range(len(map_lanes_assoc_lanes)):
        map_lane_1 = map_lanes_assoc_lanes[i][0]
        map_lane_2 = map_lanes_assoc_lanes[i][1]
        for j in range(len(lanes_test)):
            if lanes_test[j].map_lane_id == map_lane_1:
                lane_1 = j
            if lanes_test[j].map_lane_id == map_lane_2:
                lane_2 = j
        lanes_test[lane_1].assoc_lanes.append(lane_2)
        lanes_test[lane_2].assoc_lanes.append(lane_1)
assign_associate_lanes(lanes_test,map_lanes_assoc_lanes)

def create_light_lanes_at_junc(lanes_test,juncs_test):
    # this looks to see if there are any associated lanes in .lanes_at_junc and will keep only one of the assocaited lanes
    # ie. 30 and 34 are associated and at the same junction, (both in lanes_at_junc) but only one (say 30) will appear in light_lanes_at_junc as both will turn green if 30 is green
    for i in range(len(juncs_test)):
        # juncs_test[i].light_lanes_at_junc = juncs_test[i].lanes_at_junc
        for j in juncs_test[i].lanes_at_junc:
            if len(lanes_test[j].assoc_lanes) == 0:
                # lane has no associated lanes so can be added to light_lanes_at_junc
                juncs_test[i].light_lanes_at_junc.append(j)
            else:
                # put lane in but then remove it and remove it's assoc_lanes
                juncs_test[i].light_lanes_at_junc.append(j)
                for k in lanes_test[j].assoc_lanes:
                    if k in juncs_test[i].light_lanes_at_junc:
                        juncs_test[i].light_lanes_at_junc.remove(k)
create_light_lanes_at_junc(lanes_test,juncs_test)

def create_entry_and_exit_with_lanes_id(lanes_test,entry_lanes,exit_lanes,map_entry_lanes,map_exit_lanes):
    for i in range(len(lanes_test)):
        if lanes_test[i].map_lane_id in map_entry_lanes:
            entry_lanes.append(i)
        if lanes_test[i].map_lane_id in map_exit_lanes:
            exit_lanes.append(i)
create_entry_and_exit_with_lanes_id(lanes_test,entry_lanes,exit_lanes,map_entry_lanes,map_exit_lanes)

def populate_points_arrays_and_find_side_points(lanes_test):
    # create lanes_test[i].points_with_info
    for i in range(len(lanes_test)): # loop through all lanes
        for j in range(len(lanes_test[i].points)):
            if j == 0: # first point in lane, give status = 1
                status = 1
                junc_pos = lanes_test[i].junc_pos[0]
                # junc_pos = 2
                lanes_test[i].points[j].append(status)
                lanes_test[i].points[j].append(junc_pos)
                lanes_test[i].points_with_info.append(lanes_test[i].points[j])
                lanes_test[i].points[j] = lanes_test[i].points[j][:-2] # remove status and junc_pos from self.points
            elif j == (len(lanes_test[i].points) - 1): # last point in lane, give status = 3
                status = 3
                # junc_pos = 2
                junc_pos = lanes_test[i].junc_pos[1]
                lanes_test[i].points[j].append(status)
                lanes_test[i].points[j].append(junc_pos)
                lanes_test[i].points_with_info.append(lanes_test[i].points[j])
                # record = record[:-1]
                lanes_test[i].points[j] = lanes_test[i].points[j][:-2] # remove status and junc_pos from self.points
            else:  # interior point in lane, give status = 2
                status = 2
                junc_pos = 0
                # junc_pos = 2
                lanes_test[i].points[j].append(status)
                lanes_test[i].points[j].append(junc_pos)
                lanes_test[i].points_with_info.append(lanes_test[i].points[j])
                lanes_test[i].points[j] = lanes_test[i].points[j][:-2] # remove status and junc_pos from self.points
        # print("points: " + str(lanes_test[i].points))
        # print("points_with_info: " + str(lanes_test[i].points_with_info))

    for i in range(len(lanes_test)): # loop through all lane, to find the angle from vert of the line leaving each point
        for j in range(len(lanes_test[i].points)):
            if j == (len(lanes_test[i].points) - 1): # the last point is different as it doesn't have a line leaving it
                line_quadrant = 0
                angle_of_line_leaving_point = 0
                lanes_test[i].points_with_angles.append([lanes_test[i].points[j][0], lanes_test[i].points[j][1], angle_of_line_leaving_point,line_quadrant])
            else:
                point_1 = lanes_test[i].points[j]
                point_2 = lanes_test[i].points[j + 1]
                line_quadrant, angle_of_line_leaving_point = find_line_info(point_1,point_2)
                lanes_test[i].points_with_angles.append([lanes_test[i].points[j][0], lanes_test[i].points[j][1], angle_of_line_leaving_point,line_quadrant])

    # first find the points either side of the centre_line points
    # need the angle of line approaching point and angle of line leaving the point
    # self.points_with_angles = [] # [[x1,y1,angle_from_vert_at_point,line_quadrant going from point], [x2,y2,...],...]

    # find the angle of the end of the lane where it joins the junction
    for i in range(len(lanes_test)): # loop through all lanes
        for j in range(len(lanes_test[i].points)):
            if j == 0: # for first point
                if lanes_test[i].points_with_info[j][3] == 1: # check junc_pos, enters/exits at top or bottom of junction, hence line vetical
                    angle_from_vert_at_point = 0
                    angle_line_points_on = angle_from_vert_at_point + (math.pi/2)
                elif lanes_test[i].points_with_info[j][3] == 2: # check junc_pos, enters/exits at side of junction, hence line horizontal
                    angle_from_vert_at_point = (math.pi) / 2
                    angle_line_points_on = angle_from_vert_at_point - (math.pi/2)
                elif lanes_test[i].points_with_info[j][3] == 0: # if want to end or start lane perpendicular to lane
                    angle_line_leaving = lanes_test[i].points_with_angles[j][2]
                    angle_line_points_on = angle_line_leaving - (math.pi/2)
                    # print("angle_line_leaving: " + str(angle_line_leaving))
                    # print("angle_line_points_on: " + str(angle_line_points_on))
            elif j == (len(lanes_test[i].points) - 1): # for last
                if lanes_test[i].points_with_info[j][3] == 1: # check junc_pos, enters/exits at top or bottom of junction, hence line vetical
                    angle_from_vert_at_point = 0
                    angle_line_points_on = angle_from_vert_at_point + (math.pi/2)
                elif lanes_test[i].points_with_info[j][3] == 2: # check junc_pos, enters/exits at side of junction, hence line horizontal
                    angle_from_vert_at_point = (math.pi) / 2
                    angle_line_points_on = angle_from_vert_at_point - (math.pi/2)
                elif lanes_test[i].points_with_info[j][3] == 0: # if want to end or start lane perpendicular to lane
                    angle_line_approaching = lanes_test[i].points_with_angles[j - 1][2]
                    angle_line_points_on = angle_line_approaching - (math.pi/2)





            #
            #
            # if j == 0 or j == (len(lanes_test[i].points) - 1): # the first point or last point
            #     if lanes_test[i].points_with_info[j][3] == 1: # check junc_pos, enters/exits at top or bottom of junction, hence line vetical
            #         angle_from_vert_at_point = 0
            #         angle_line_points_on = angle_from_vert_at_point + (math.pi/2)
            #     elif lanes_test[i].points_with_info[j][3] == 2: # check junc_pos, enters/exits at side of junction, hence line horizontal
            #         angle_from_vert_at_point = (math.pi) / 2
            #         angle_line_points_on = angle_from_vert_at_point - (math.pi/2)
            #     elif lanes_test[i].points_with_info[j][3] == 0: # if want to end or start lane perpendicular to lane
            #         angle_line_leaving = lanes_test[i].points_with_angles[j][2]
            #         angle_line_points_on = angle_line_leaving - (math.pi/2)
            elif lanes_test[i].points_with_info[j][3] == 0: # interior point so angle_from_vert_at_point equals the angle_from_vert between it and the next point
                angle_line_approaching = lanes_test[i].points_with_angles[j - 1][2]
                angle_line_leaving = lanes_test[i].points_with_angles[j][2]
                avg_angle = (angle_line_approaching + angle_line_leaving)/ 2
                if angle_line_approaching > angle_line_leaving:
                    angle_line_points_on = avg_angle - (math.pi/2)
                else: # ie. angle_line_approaching <= angle_line_leaving
                    angle_line_points_on = avg_angle + (math.pi/2)
            # print("q j: " + str(j))
            # print("lanes_test[i].points_with_info[j][3]: " + str(lanes_test[i].points_with_info[j][3]))
            lanes_test[i].angle_side_points_on.append(angle_line_points_on)
            # print(" before: " + str(lanes_test[i].points_with_angles))
            lanes_test[i].points_with_angles[j].append(angle_line_points_on)
            # print(" after: " + str(lanes_test[i].points_with_angles))
        #     print("i: " + str(i) + " j: " + str(j) + " angle_line_points_on: " + str(lanes_test[i].angle_side_points_on))
        # print("points_with_angles: " + str(lanes_test[i].points_with_angles))

        for k in range(len(lanes_test[i].points)):
            line_quadrant  = lanes_test[i].points_with_angles[k][3]
            # print("lanes_test[i].points_with_angles[k]: " + str(lanes_test[i].points_with_angles[k]))
            x_offset = lw_half*math.sin(lanes_test[i].points_with_angles[k][4])
            y_offset = lw_half*math.cos(lanes_test[i].points_with_angles[k][4])
            # print("before x_offset: " + str(x_offset) + " y_offset: " + str(y_offset))
            larger_offset = max(abs(x_offset),abs(y_offset))
            factor = lw_half / larger_offset
            x_offset = x_offset * factor
            y_offset = y_offset * factor
            # print("after x_offset: " + str(x_offset) + " y_offset: " + str(y_offset))
            # print("larger_offset: " + str(larger_offset))
            modulus = math.sqrt((x_offset**2) + (y_offset**2))
            # print("modulus: " + str(modulus))
            x1 = lanes_test[i].points_with_angles[k][0] + x_offset
            y1 = lanes_test[i].points_with_angles[k][1] - y_offset
            x2 = lanes_test[i].points_with_angles[k][0] - x_offset
            y2 = lanes_test[i].points_with_angles[k][1] + y_offset
            lanes_test[i].side_points.append([x1,y1,x2,y2])
populate_points_arrays_and_find_side_points(lanes_test)
def find_next_upper_side_point(point_1,latest_upper_line_point,point_2,side_point_2_1,side_point_2_2,lanes_test,lane_of_interest):
    latest_upper_line_point = [latest_upper_line_point]
    side_point_options = [side_point_2_1,side_point_2_2]
    centre_line = [point_1,point_2]
    pair = []
    for i in range(len(latest_upper_line_point)):
        for j in range(len(side_point_options)):
            # print("new upper side point")
            # first check intersection between
            side_line_opt = [latest_upper_line_point[i],side_point_options[j]]
            # print("side_line_opt: " + str(side_line_opt))
            # print("centre_line: " + str(centre_line))
            # input("Press Enter to continue...")
            xdiff = (centre_line[0][0] - centre_line[1][0], side_line_opt[0][0] - side_line_opt[1][0])
            ydiff = (centre_line[0][1] - centre_line[1][1], side_line_opt[0][1] - side_line_opt[1][1])

            def det(a, b):
                return a[0] * b[1] - a[1] * b[0]

            div = det(xdiff, ydiff)
            if div == 0:
                x = 0
                y = 0
                intersection_cross = 0 # so do not cross
                # print(" parallel" + " latest_upper_line_point[i]: " + str(latest_upper_line_point[i]) + " side_point_options[j]: " + str(side_point_options[j]))
                pair.append([latest_upper_line_point[i], side_point_options[j]])
                lanes_test[lane_of_interest].upper_line_points.append(side_point_options[j])
                # input("Press Enter to continue...")

                # print("0: " + " upper_line_points: " + str(lanes_test[lane_of_interest].upper_line_points))
               # raise Exception('lines do not intersect')
            else:
               d = (det(*centre_line), det(*side_line_opt))
               x = det(d, xdiff) / div
               y = det(d, ydiff) / div
               x_round = round(x)
               y_round = round(y)
               centre_line_min_x = min(centre_line[0][0],centre_line[1][0])
               centre_line_max_x = max(centre_line[0][0],centre_line[1][0])
               centre_line_min_y = min(centre_line[0][1],centre_line[1][1])
               centre_line_max_y = max(centre_line[0][1],centre_line[1][1])
               # print("x: " + str(x) + " y: " + str(y))
               # print("x_round: " + str(x_round) + " y_round: " + str(y_round))
               # print("centre_line_min_x: " + str(centre_line_min_x) + " centre_line_max_x: " + str(str(centre_line_max_x))+ " centre_line_min_y: " + str(centre_line_min_y) + " centre_line_max_y: " + str(centre_line_max_y))
               # input("Press Enter to continue...")
               if x_round >= centre_line_min_x and x_round <= centre_line_max_x and y_round >= centre_line_min_y and y_round <= centre_line_max_y:
               # if x >= centre_line_min_x and x <= centre_line_max_x and y >= centre_line_min_y and y <= centre_line_max_y:
                   # print("x: " + str(x) + " y: " + str(y) + " intersects line_1")
                   # print("4")
                   intersection_cross = 1
               else:
                   # print("x: " + str(x) + " y: " + str(y) + " doesn't intersect line_1")
                   # print(" doesn't intersect line_1" + " latest_upper_line_point[i]: " + str(latest_upper_line_point[i]) + " side_point_options[j]: " + str(side_point_options[j]))
                   pair.append([latest_upper_line_point[i], side_point_options[j]])
                   lanes_test[lane_of_interest].upper_line_points.append(side_point_options[j])
                   print
def find_next_lower_side_point(point_1,latest_lower_line_point,point_2,side_point_2_1,side_point_2_2,lanes_test,lane_of_interest):
    latest_lower_line_point = [latest_lower_line_point]
    side_point_options = [side_point_2_1,side_point_2_2]
    centre_line = [point_1,point_2]
    pair = []
    for i in range(len(latest_lower_line_point)):
        for j in range(len(side_point_options)):
            # first check intersection between
            # print("new lower side point")
            side_line_opt = [latest_lower_line_point[i],side_point_options[j]]
            # print("side_line_opt: " + str(side_line_opt))
            xdiff = (centre_line[0][0] - centre_line[1][0], side_line_opt[0][0] - side_line_opt[1][0])
            ydiff = (centre_line[0][1] - centre_line[1][1], side_line_opt[0][1] - side_line_opt[1][1])

            def det(a, b):
                return a[0] * b[1] - a[1] * b[0]

            div = det(xdiff, ydiff)
            if div == 0:
                x = 0
                y = 0
                intersection_cross = 0 # so do not cross
                # print(" parallel" + " latest_lower_line_point[i]: " + str(latest_lower_line_point[i]) + " side_point_options[j]: " + str(side_point_options[j]))
                pair.append([latest_lower_line_point[i], side_point_options[j]])
                lanes_test[lane_of_interest].lower_line_points.append(side_point_options[j])

               # raise Exception('lines do not intersect')
            else:
               d = (det(*centre_line), det(*side_line_opt))
               x = det(d, xdiff) / div
               y = det(d, ydiff) / div
               x_round = round(x)
               y_round = round(y)
               centre_line_min_x = min(centre_line[0][0],centre_line[1][0])
               centre_line_max_x = max(centre_line[0][0],centre_line[1][0])
               centre_line_min_y = min(centre_line[0][1],centre_line[1][1])
               centre_line_max_y = max(centre_line[0][1],centre_line[1][1])
               if x_round >= centre_line_min_x and x_round <= centre_line_max_x and y_round >= centre_line_min_y and y_round <= centre_line_max_y:
               # if x >= centre_line_min_x and x <= centre_line_max_x and y >= centre_line_min_y and y <= centre_line_max_y:
                   # print("x: " + str(x) + " y: " + str(y) + " intersects line_1")
                   # print("5")
                   intersection_cross = 1
               else:
                   # print("x: " + str(x) + " y: " + str(y) + " doesn't intersect line_1")
                   # print(" doesn't intersect line_1" + " latest_lower_line_point[i]: " + str(latest_lower_line_point[i]) + " side_point_options[j]: " + str(side_point_options[j]))
                   pair.append([latest_lower_line_point[i], side_point_options[j]])
                   lanes_test[lane_of_interest].lower_line_points.append(side_point_options[j])
def define_and_draw_upper_line(lanes_test):
    #draw upper line
    for i in range(len(lanes_test)): # loop through all lanes
        for j in range(len(lanes_test[i].points)):
            if j == 0: # the first point defines the upper and lower point on that lane
                point = lanes_test[i].points[j]
                side_point_1 = lanes_test[i].side_points[j][0:2]
                side_point_2 = lanes_test[i].side_points[j][2:]
                # print("side_point_1 first: " + str(side_point_1))
                # print("side_point_2 first: " + str(side_point_2))
                if side_point_1[0] >= point[0] and side_point_1[1] <= point[1]:
                    lanes_test[i].upper_line_points.append(side_point_1)
                    lanes_test[i].lower_line_points.append(side_point_2)
                    # print("1")
                elif side_point_1[0] <= point[0] and side_point_1[1] < point[1]:
                    lanes_test[i].upper_line_points.append(side_point_1)
                    lanes_test[i].lower_line_points.append(side_point_2)
                    # print("2")
                elif side_point_1[0] >= point[0] and side_point_1[1] > point[1]:
                    lanes_test[i].upper_line_points.append(side_point_2)
                    lanes_test[i].lower_line_points.append(side_point_1)
                    # print("3")
                elif side_point_1[0] <= point[0] and side_point_1[1] >= point[1]:
                    lanes_test[i].upper_line_points.append(side_point_2)
                    lanes_test[i].lower_line_points.append(side_point_1)
                    # print("4")
            else:
                # print("here: " + str(lanes_test[i].upper_line_points))
                # print("here j: " + str(j))
                # print("lanes_test[i].points[j-1]: " + str(lanes_test[i].points[j-1]))
                # print("lanes_test[i].side_points: " + str(lanes_test[i].side_points))
                # print("lanes_test[i].upper_line_points: " + str(lanes_test[i].upper_line_points))
                # print("lanes_test[i].upper_line_points[j-1]: " + str(lanes_test[i].upper_line_points[j-1]))
                find_next_upper_side_point(lanes_test[i].points[j-1], lanes_test[i].upper_line_points[j-1],lanes_test[i].points[j],lanes_test[i].side_points[j][0:2],lanes_test[i].side_points[j][2:4],lanes_test,i)
                find_next_lower_side_point(lanes_test[i].points[j-1], lanes_test[i].lower_line_points[j-1],lanes_test[i].points[j],lanes_test[i].side_points[j][0:2],lanes_test[i].side_points[j][2:4],lanes_test,i)
define_and_draw_upper_line(lanes_test)
def define_and_draw_lower_line(lanes_test):
    # draw lower line
    for i in range(len(lanes_test)): # loop through all lanes
        # print("points: " + str(lanes_test[i].points))
        # print("side points: " + str(lanes_test[i].side_points))
        # print("upper_line_points: " + str(lanes_test[i].upper_line_points))
        # print("lower_line_points: " + str(lanes_test[i].lower_line_points))
        for j in range((len(lanes_test[i].points)) - 1 ):
            # print("j: " + str(j))
            x1 = lanes_test[i].points[j][0]
            y1 = lanes_test[i].points[j][1]
            x2 = lanes_test[i].points[j + 1][0]
            y2 = lanes_test[i].points[j + 1][1]
            canvas.create_line(x1,y1,x2,y2,dash=(4,1))
            x1_upper = lanes_test[i].upper_line_points[j][0]
            y1_upper = lanes_test[i].upper_line_points[j][1]
            x2_upper = lanes_test[i].upper_line_points[j + 1][0]
            y2_upper = lanes_test[i].upper_line_points[j + 1][1]
            # canvas.create_line(x1_upper,y1_upper,x2_upper,y2_upper,width=2)
            canvas.create_line(x1_upper,y1_upper,x2_upper,y2_upper)
            x1_lower = lanes_test[i].lower_line_points[j][0]
            y1_lower = lanes_test[i].lower_line_points[j][1]
            x2_lower = lanes_test[i].lower_line_points[j + 1][0]
            y2_lower = lanes_test[i].lower_line_points[j + 1][1]
            canvas.create_line(x1_lower,y1_lower,x2_lower,y2_lower)
            if j == (len(lanes_test[i].points)) - 2:
                canvas.create_line(lanes_test[i].lower_line_points[j + 1][0],lanes_test[i].lower_line_points[j + 1][1],lanes_test[i].upper_line_points[j + 1][0],lanes_test[i].upper_line_points[j + 1][1],dash=(4,1))
define_and_draw_lower_line(lanes_test)

# find point of intersection between lane and next lanes, RESOLVED
def find_point_of_intersection_between_lane_and_next_lanes(lanes_test):
    for i in range(len(lanes_test)):
        lane_last_point = lanes_test[i].points[-1][0:2]
        lane_second_last_point = lanes_test[i].points[-2][0:2]
        lane_points = [lane_second_last_point,lane_last_point]
        # print("lane_last_point: " + str(lane_last_point) + " sec_last: " + str(lane_second_last_point))
        for j in lanes_test[i].next_lanes:
            #find lanes_test
            if j != 9999:
                next_lane_dealt_wth = 0
                # check to see if next_lane is in map_free_turn_next_lanes
                if j in lanes_test[i].free_turn_next_lanes:
                    # found true point_of_intersection between the lane, ie. find the lane line the point_of_intersection lies on
                    # find the point of intersection between the next_lane and every line in the current lane
                    # loop through lanes_test.points_with_angles
                    point_store_temp = []
                    point_store_temp.append(j)
                    num_lines_in_lane = len(lanes_test[i].points_with_angles) - 1
                    for k in range(num_lines_in_lane):
                        line_point_1_x = lanes_test[i].points_with_angles[k][0]
                        line_point_1_y = lanes_test[i].points_with_angles[k][1]
                        line_point_2_x = lanes_test[i].points_with_angles[k + 1][0]
                        line_point_2_y = lanes_test[i].points_with_angles[k + 1][1]
                        line_angle = lanes_test[i].points_with_angles[k][2]

                        # find point_of_intersection, if lies on the line then it is the true point_of_intersection, if it doesn't intersection any lane line treat it as a normal next_lane
                        lane_line_points = [[line_point_1_x,line_point_1_y],[line_point_2_x,line_point_2_y]]
                        next_lane_first_point = lanes_test[j].points[0][0:2]
                        next_lane_second_point = lanes_test[j].points[1][0:2]
                        next_lane_points = [next_lane_first_point,next_lane_second_point]
                        xdiff = (lane_line_points[0][0] - lane_line_points[1][0], next_lane_points[0][0] - next_lane_points[1][0])
                        ydiff = (lane_line_points[0][1] - lane_line_points[1][1], next_lane_points[0][1] - next_lane_points[1][1])
                        point_store_temp.append([line_point_1_x,line_point_1_y])

                        def det(a, b):
                            return a[0] * b[1] - a[1] * b[0]
                        div = det(xdiff, ydiff)
                        if div == 0:
                            intersection_cross = 0 # so do not cross, could be straight ahead or parallel
                            x = next_lane_first_point[0]
                            y = next_lane_first_point[1]
                        else:
                            d = (det(*lane_points), det(*next_lane_points))
                            x = det(d, xdiff) / div
                            y = det(d, ydiff) / div
                            x_round = round(x)
                            y_round = round(y)
                        # check if lies on lane line if dist between the ends of the line are equal to distance between the ends of line and point of intersection
                        dist_lane_line = math.sqrt(((line_point_2_y - line_point_1_y)**2) + ((line_point_2_x - line_point_1_x)**2))
                        dist_between_point_of_inters_and_start_of_lane_line = math.sqrt(((y - line_point_1_y)**2) + ((x - line_point_1_x)**2))
                        dist_between_point_of_inters_and_end_of_lane_line = math.sqrt(((line_point_2_y - y)**2) + ((line_point_2_x - x)**2))
                        if (dist_between_point_of_inters_and_start_of_lane_line + dist_between_point_of_inters_and_end_of_lane_line) == dist_lane_line:
                            # free_turn_next_lane turns off from curent lane at this lane line, thus this is the TRUE point_of_intersection
                            lanes_test[i].next_lanes_intersection.append([j,x,y])
                            lanes_test[i].free_turn_next_lanes_intersection.append([j,x,y])
                            lanes_test[i].end_point_for_free_turn_next_lanes.append([j,x,y])
                            point_store_temp.append([x,y])
                            next_lane_dealt_with = 1
                    if len(lanes_test[i].free_turn_next_lanes_intersection) == 0:
                        # this free_turn_next_lane does not turn off in the middle of the current lane, thus must turn off at the end. ie. a junction but not controlled by lights
                        # thus follow the same process if the free_turn_next_lane was a normal next_lane
                        next_lane_dealt_with = 0
                        # use the last points in the curent lane to find intersection at junction with free_turn_next_lane
                        xdiff = (lane_points[0][0] - lane_points[1][0], next_lane_points[0][0] - next_lane_points[1][0])
                        ydiff = (lane_points[0][1] - lane_points[1][1], next_lane_points[0][1] - next_lane_points[1][1])
                        def det(a, b):
                            return a[0] * b[1] - a[1] * b[0]
                        div = det(xdiff, ydiff)
                        if div == 0:
                            intersection_cross = 0 # so do not cross, could be straight ahead or parallel
                            x = next_lane_first_point[0]
                            y = next_lane_first_point[1]
                        else:
                            d = (det(*lane_points), det(*next_lane_points))
                            x = det(d, xdiff) / div
                            y = det(d, ydiff) / div
                            x_round = round(x)
                            y_round = round(y)
                            if x == lane_last_point[0] and y == lane_last_point[1]:
                                # if lanes aren't parallel but there is onlt a small angle difference, sometimes the point_of_intersection = lane_last_point which will cause an error when finding the move points between these two.
                                # therefore, change point_of_intersection to the first_point of the next_lane
                                x = next_lane_first_point[0]
                                y = next_lane_first_point[1]
                            intersection_cross = 1 # so do cross
                            # canvas.create_oval((x + 2),(y + 2),(x - 2),(y -2))
                            # lanes_test[i].next_lanes_intersection.append([j,next_lane_points[0][0],next_lane_points[0][1]])
                        dist_between_last_point_and_point_of_intersection = math.sqrt(((y - lane_last_point[1])**2) + ((x - lane_last_point[0])**2))
                        # check if point of intersection is accurate, could be miles away
                        if dist_between_last_point_and_point_of_intersection > (3*lw):
                            x = next_lane_first_point[0]
                            y = next_lane_first_point[1]
                        lanes_test[i].next_lanes_intersection.append([j,x,y])
                        lanes_test[i].free_turn_next_lanes_intersection.append([j,x,y])
                        x_end = lane_last_point[0]
                        y_end = lane_last_point[1]
                        lanes_test[i].end_point_for_free_turn_next_lanes.append([j,x_end,y_end])
                        point_store_temp.append([x_end,y_end])
                        next_lane_dealt_with = 1
                    lanes_test[i].free_turn_next_lane_points.append(point_store_temp)


                else: # the normal process for a next_lane
                    next_lane_first_point = lanes_test[j].points[0][0:2]
                    next_lane_second_point = lanes_test[j].points[1][0:2]
                    next_lane_points = [next_lane_first_point,next_lane_second_point]
                    # print("j: " + str(j) + " next_lane_points: " + str(next_lane_points))

                    xdiff = (lane_points[0][0] - lane_points[1][0], next_lane_points[0][0] - next_lane_points[1][0])
                    ydiff = (lane_points[0][1] - lane_points[1][1], next_lane_points[0][1] - next_lane_points[1][1])

                    def det(a, b):
                        return a[0] * b[1] - a[1] * b[0]

                    div = det(xdiff, ydiff)
                    if div == 0:
                        intersection_cross = 0 # so do not cross, could be straight ahead or parallel
                        x = next_lane_first_point[0]
                        y = next_lane_first_point[1]
                        # canvas.create_oval((x + 2),(y + 2),(x - 2),(y -2))
                        # lanes_test[i].next_lanes_intersection.append([j,x,y])
                       # raise Exception('lines do not intersect')
                    else:
                        d = (det(*lane_points), det(*next_lane_points))
                        x = det(d, xdiff) / div
                        y = det(d, ydiff) / div
                        x_round = round(x)
                        y_round = round(y)
                        if x == lane_last_point[0] and y == lane_last_point[1]:
                            # if lanes aren't parallel but there is onlt a small angle difference, sometimes the point_of_intersection = lane_last_point which will cause an error when finding the move points between these two.
                            # therefore, change point_of_intersection to the first_point of the next_lane
                            x = next_lane_first_point[0]
                            y = next_lane_first_point[1]
                        intersection_cross = 1 # so do cross
                        # canvas.create_oval((x + 2),(y + 2),(x - 2),(y -2))
                        # lanes_test[i].next_lanes_intersection.append([j,next_lane_points[0][0],next_lane_points[0][1]])
                    dist_between_last_point_and_point_of_intersection = math.sqrt(((y - lane_last_point[1])**2) + ((x - lane_last_point[0])**2))
                    # check if point of intersection is accurate, could be miles away
                    if dist_between_last_point_and_point_of_intersection > (3*lw):
                        x = next_lane_first_point[0]
                        y = next_lane_first_point[1]
                    lanes_test[i].next_lanes_intersection.append([j,x,y])
find_point_of_intersection_between_lane_and_next_lanes(lanes_test)

def create_and_populate_free_turn_next_lane_points_with_angles(lanes_test):
    for i in range(len(lanes_test)):
        if len (lanes_test[i].free_turn_next_lanes ) > 0:
            # find angle between points between lane line's and final point in free_turn_next_lane_points
            for j in range(len(lanes_test[i].free_turn_next_lane_points)): # this lops through all the free_turn_lanes options
                # lanes_test[i].free_turn_next_lane_points_with_angles.append(lanes_test[i].free_turn_next_lane_points[j][0])
                points_with_angles_temp = []
                points_with_angles_temp.append(lanes_test[i].free_turn_next_lane_points[j][0])
                for k in range(1,(len(lanes_test[i].free_turn_next_lane_points[j])) - 1): # this looops through all the points
                    next_lane = lanes_test[i].free_turn_next_lane_points[j][0]
                    point_1 = lanes_test[i].free_turn_next_lane_points[j][k]
                    point_1_x = lanes_test[i].free_turn_next_lane_points[j][k][0]
                    point_1_y = lanes_test[i].free_turn_next_lane_points[j][k][1]
                    point_2 = lanes_test[i].free_turn_next_lane_points[j][k + 1]
                    point_2_x = lanes_test[i].free_turn_next_lane_points[j][k + 1][0]
                    point_2_y = lanes_test[i].free_turn_next_lane_points[j][k + 1][1]
                    # canvas.create_oval(point_2_x-3,point_2_y-3,point_2_x+3,point_2_y+3,fill = 'green')
                    # tk.update()
                    # input("herhee")
                    line_quadrant, angle_from_vert = find_line_info(point_1,point_2)
                    # lanes_test[i].free_turn_next_lane_points_with_angles.append([point_1_x,point_1_y,angle_from_vert])
                    points_with_angles_temp.append([point_1_x,point_1_y,angle_from_vert])
                # lanes_test[i].free_turn_next_lane_points_with_angles.append([point_2_x,point_2_y,0])
                points_with_angles_temp.append([point_2_x,point_2_y,0])
                lanes_test[i].free_turn_next_lane_points_with_angles.append(points_with_angles_temp)
create_and_populate_free_turn_next_lane_points_with_angles(lanes_test)

def find_move_points_between_lanes_info(lanes_test):
    for i in range(len(lanes_test)):
        for j in range(len(lanes_test[i].next_lanes_intersection)):
            # print("i: " + str(i) + " j: " + str(j))
            # populate with transition points angles from vertical leaving each transition point
            current_lane = i
            next_lane = lanes_test[i].next_lanes_intersection[j][0]
            current_lane_last_point_x = lanes_test[i].points[-1][0]
            current_lane_last_point_y = lanes_test[i].points[-1][1]
            next_lane_first_point_x =  lanes_test[lanes_test[i].next_lanes_intersection[j][0]].points[0][0]
            next_lane_first_point_y =  lanes_test[lanes_test[i].next_lanes_intersection[j][0]].points[0][1]
            next_lane = lanes_test[i].next_lanes_intersection[j][0]
            intersection_point_x = lanes_test[i].next_lanes_intersection[j][1]
            intersection_point_y = lanes_test[i].next_lanes_intersection[j][2]
            # check if next_lane is actually in current_lane's free_turn_next_lanes
            if next_lane in lanes_test[i].free_turn_next_lanes:
                # set current_lane_lat_point to equal the point the free_turn_next_lane leaves the current_lane
                # find the next_lane in end_point_for_free_turn_next_lanes
                for p in range(len(lanes_test[i].end_point_for_free_turn_next_lanes)):
                    if next_lane == lanes_test[i].end_point_for_free_turn_next_lanes[p][0]:
                        current_lane_last_point_x = lanes_test[i].end_point_for_free_turn_next_lanes[p][1]
                        current_lane_last_point_y = lanes_test[i].end_point_for_free_turn_next_lanes[p][2]
                        next_lane_first_point_x =  lanes_test[lanes_test[i].next_lanes_intersection[j][0]].points[0][0]
                        next_lane_first_point_y =  lanes_test[lanes_test[i].next_lanes_intersection[j][0]].points[0][1]
                        next_lane = lanes_test[i].next_lanes_intersection[j][0]
                        intersection_point_x = next_lane_first_point_x
                        intersection_point_y = next_lane_first_point_y


            # next_lane_first_point_x =  lanes_test[lanes_test[i].next_lanes_intersection[j][0]].points[0][0]
            # next_lane_first_point_y =  lanes_test[lanes_test[i].next_lanes_intersection[j][0]].points[0][1]
            # next_lane = lanes_test[i].next_lanes_intersection[j][0]
            # intersection_point_x = lanes_test[i].next_lanes_intersection[j][1]
            # intersection_point_y = lanes_test[i].next_lanes_intersection[j][2]
            # print("i " + str(i))
            # print("current_lane_last_point_x: " + str(current_lane_last_point_x))
            # print("current_lane_last_point_y: " + str(current_lane_last_point_y))
            # print("intersection_point_x: " + str(intersection_point_x))
            # print("intersection_point_y: " + str(intersection_point_y))

            if (intersection_point_x == next_lane_first_point_x) and (intersection_point_y == next_lane_first_point_y):
                # print("here 1")
                # straight line transition so don't need to append to  next_lanes_transition_points again also used for free_turn_next_lanes
                line_quadrant, angle_last_to_intersect_point = find_line_info([current_lane_last_point_x,current_lane_last_point_y],[intersection_point_x,intersection_point_y])
                lanes_test[i].next_lanes_transition_points.append([current_lane,next_lane, current_lane_last_point_x,current_lane_last_point_y,angle_last_to_intersect_point])
            else:
                # print("here 2")
                line_quadrant, angle_last_to_intersect_point = find_line_info([current_lane_last_point_x,current_lane_last_point_y],[intersection_point_x,intersection_point_y])
                line_quadrant, angle_intersect_to_first_point = find_line_info([intersection_point_x,intersection_point_y],[next_lane_first_point_x,next_lane_first_point_y])
                lanes_test[i].next_lanes_transition_points.append([current_lane,next_lane,current_lane_last_point_x,current_lane_last_point_y,angle_last_to_intersect_point, intersection_point_x,intersection_point_y,angle_intersect_to_first_point])
            # if i == 30:
            #     print("next_lanes_transition_points: " + str(lanes_test[i].next_lanes_transition_points))
            #     input("pause 4")
        # print("next_lanes_transition_points: " + str(lanes_test[i].next_lanes_transition_points))
    ##### move pointe -transition here
    for i in range(len(lanes_test)):
        for j in range(len(lanes_test[i].next_lanes_transition_points)):
            # if i == 4:
            #     print("j: " + str(j))
            temp_move_points = []
            if len(lanes_test[i].next_lanes_transition_points[j]) == 5: # simple striaght line transition to next lane
                current_lane = lanes_test[i].next_lanes_transition_points[j][0]
                next_lane = lanes_test[i].next_lanes_transition_points[j][1]
                move_point_x = lanes_test[i].next_lanes_transition_points[j][2] # start at last point of current lane
                move_point_y = lanes_test[i].next_lanes_transition_points[j][3]
                # move_point_x  = lanes_test[i].points_info_min[j][0] # start at start point of first line in lane
                # move_point_y = lanes_test[i].points_info_min[j][1]
                temp_angle = lanes_test[i].next_lanes_transition_points[j][4] # angle of line leaving point
                # temp_angle = lanes_test[i].points_info_min[j][2]
                temp_line_end_point_x = lanes_test[next_lane].points[0][0]
                temp_line_end_point_y = lanes_test[next_lane].points[0][1]
                # temp_line_end_point_x = lanes_test[i].points_info_min[j + 1][0]
                # temp_line_end_point_y = lanes_test[i].points_info_min[j + 1][1]
                dist_to_end_point = math.sqrt(((abs(temp_line_end_point_y - move_point_y))**2) + ((abs(temp_line_end_point_x - move_point_x))**2))
                # if j == 0:
                #     lanes_test[i].move_points_next_lanes.append([move_point_x,move_point_y,temp_angle]) # inoput first point in line
                # if dist_to_end_point == 0: # just in case the first point is the same as the end point
                #     lanes_test[i].move_points.append([move_point_x,move_point_y,temp_angle])
                while dist_to_end_point > 0:
                    # print("1"   " i: " + str(i) + " j: " + str(j))
                    if dist_to_end_point < move_val: # set the move_point tpo the end_point
                        move_point_x = temp_line_end_point_x
                        move_point_y = temp_line_end_point_y

                    else:
                        move_point_x += move_val*math.sin(temp_angle)
                        move_point_y -= move_val*math.cos(temp_angle)
                        move_point_x_rounded = round(move_point_x)
                        move_point_y_rounded = round(move_point_y)
                        temp_move_points.append([move_point_x,move_point_y,temp_angle])
                    dist_to_end_point = math.sqrt(((abs(temp_line_end_point_y - move_point_y))**2) + ((abs(temp_line_end_point_x - move_point_x))**2))
                    # lanes_test[i].move_points_next_lanes.append([move_point_x,move_point_y,temp_angle])
                    # temp_move_points.append([move_point_x,move_point_y,temp_angle])
            else: # if there is an intersection point
                current_lane = lanes_test[i].next_lanes_transition_points[j][0]
                next_lane = lanes_test[i].next_lanes_transition_points[j][1]
                move_point_x = lanes_test[i].next_lanes_transition_points[j][2] # start at last point of current lane
                move_point_y = lanes_test[i].next_lanes_transition_points[j][3]
                angle_last_to_intersection = lanes_test[i].next_lanes_transition_points[j][4] # angle of line leaving point
                intersection_point_x = lanes_test[i].next_lanes_transition_points[j][5]
                intersection_point_y = lanes_test[i].next_lanes_transition_points[j][6]
                angle_intersection_to_first = lanes_test[i].next_lanes_transition_points[j][7] # angle of line leaving point

                next_lane_point_x = lanes_test[next_lane].points[0][0]
                next_lane_point_y = lanes_test[next_lane].points[0][1]
                # first run for last point to intersection
                temp_line_end_point_x = intersection_point_x
                temp_line_end_point_y = intersection_point_y
                temp_angle = angle_last_to_intersection # angle of line leaving point
                dist_to_end_point = math.sqrt(((abs(temp_line_end_point_y - move_point_y))**2) + ((abs(temp_line_end_point_x - move_point_x))**2))
                # if j == 0:
                #     lanes_test[i].move_points_next_lanes.append([move_point_x,move_point_y,temp_angle]) # inoput first point in line
                # if dist_to_end_point == 0: # just in case the first point is the same as the end point
                #     lanes_test[i].move_points.append([move_point_x,move_point_y,temp_angle])
                while dist_to_end_point > 0:
                    # print("2"  " i: " + str(i) + " j: " + str(j))
                    if dist_to_end_point < move_val: # set the move_point tpo the end_point
                        move_point_x = temp_line_end_point_x
                        move_point_y = temp_line_end_point_y
                    else:
                        move_point_x += move_val*math.sin(temp_angle)
                        move_point_y -= move_val*math.cos(temp_angle)
                        move_point_x_rounded = round(move_point_x)
                        move_point_y_rounded = round(move_point_y)
                        temp_move_points.append([move_point_x,move_point_y,temp_angle])
                    dist_to_end_point = math.sqrt(((abs(temp_line_end_point_y - move_point_y))**2) + ((abs(temp_line_end_point_x - move_point_x))**2))
                    # lanes_test[i].move_points_next_lanes.append([move_point_x,move_point_y,temp_angle])
                    # temp_move_points.append([move_point_x,move_point_y,temp_angle])

                ##  now run from interseciton point (current move_point) to the next_lane_first point
                temp_line_end_point_x = next_lane_point_x
                temp_line_end_point_y = next_lane_point_y
                temp_angle = angle_intersection_to_first # angle of line leaving point
                dist_to_end_point = math.sqrt(((abs(temp_line_end_point_y - move_point_y))**2) + ((abs(temp_line_end_point_x - move_point_x))**2))
                # if j == 0:
                #     lanes_test[i].move_points_next_lanes.append([move_point_x,move_point_y,temp_angle]) # input first point in line

                while dist_to_end_point > 0:
                # int = 0
                # while int < 40:
                    # print("3"  " i: " + str(i) + " j: " + str(j))
                    # print("move_point_x: " + str(move_point_x) + " move_point_y: " + str(move_point_y))
                    # print("temp_line_end_point_x: " + str(temp_line_end_point_x) + " temp_line_end_point_y: " + str(temp_line_end_point_y))
                    if dist_to_end_point < move_val: # set the move_point tpo the end_point
                        move_point_x = temp_line_end_point_x
                        move_point_y = temp_line_end_point_y
                    else:
                        move_point_x += move_val*math.sin(temp_angle)
                        move_point_y -= move_val*math.cos(temp_angle)
                        move_point_x_rounded = round(move_point_x)
                        move_point_y_rounded = round(move_point_y)
                        temp_move_points.append([move_point_x,move_point_y,temp_angle])
                    dist_to_end_point = math.sqrt(((abs(temp_line_end_point_y - move_point_y))**2) + ((abs(temp_line_end_point_x - move_point_x))**2))
                    # lanes_test[i].move_points_next_lanes.append([move_point_x,move_point_y,temp_angle])
                    # temp_move_points.append([move_point_x,move_point_y,temp_angle])
                    # int += 1
            lanes_test[i].move_points_next_lanes.append(temp_move_points)
find_move_points_between_lanes_info(lanes_test)

def find_move_points_in_each_lane(lanes_test):
    ###### create move_points which cars transition to for each lane by move_val
    # first create a store of point and angle of line leaving point
    for i in range(len(lanes_test)):
        for j in range(len(lanes_test[i].points)):
            lanes_test[i].points_info_min.append(lanes_test[i].points_with_angles[j][0:3])

    for i in range(len(lanes_test)):
        for j in range(len(lanes_test[i].points_info_min) - 1):
            move_point_x  = lanes_test[i].points_info_min[j][0] # start at start point of first line in lane
            move_point_y = lanes_test[i].points_info_min[j][1]
            temp_angle = lanes_test[i].points_info_min[j][2]
            temp_line_end_point_x = lanes_test[i].points_info_min[j + 1][0]
            temp_line_end_point_y = lanes_test[i].points_info_min[j + 1][1]
            dist_to_end_point = math.sqrt(((abs(temp_line_end_point_y - move_point_y))**2) + ((abs(temp_line_end_point_x - move_point_x))**2))
            if j == 0:
                lanes_test[i].move_points.append([move_point_x,move_point_y,temp_angle]) # inoput first point in line
            # if dist_to_end_point == 0: # just in case the first point is the same as the end point
            #     lanes_test[i].move_points.append([move_point_x,move_point_y,temp_angle])
            while dist_to_end_point > 0:
                if dist_to_end_point < move_val: # set the move_point tpo the end_point
                    move_point_x = temp_line_end_point_x
                    move_point_y = temp_line_end_point_y
                else:
                    move_point_x += move_val*math.sin(temp_angle)
                    move_point_y -= move_val*math.cos(temp_angle)
                    move_point_x_rounded = round(move_point_x)
                    move_point_y_rounded = round(move_point_y)
                dist_to_end_point = math.sqrt(((abs(temp_line_end_point_y - move_point_y))**2) + ((abs(temp_line_end_point_x - move_point_x))**2))
                lanes_test[i].move_points.append([move_point_x,move_point_y,temp_angle])
        if lanes_test[i].next_lanes[0] == 9999:
            lanes_test[i].move_points.append([50,50,temp_angle])
    for i in range(len(lanes_test)):
        for j in range(len(lanes_test[i].move_points)):
            # canvas.create_oval((lanes_test[i].move_points[j][0] + 2),(lanes_test[i].move_points[j][1] + 2),(lanes_test[i].move_points[j][0] - 2),(lanes_test[i].move_points[j][1] -2))
            if j < len(lanes_test[i].move_points) - 1:
                if (lanes_test[i].move_points[j][0] == lanes_test[i].move_points[j + 1][0]) and (lanes_test[i].move_points[j][1] == lanes_test[i].move_points[j + 1][1]):
                    print("duplicate    i: " + str(i) + " j: " + str(j))
find_move_points_in_each_lane(lanes_test)

def find_free_turn_next_lane_move_points_in_lane(lanes_test):
    for i in range(len(lanes_test)):
        if len(lanes_test[i].free_turn_next_lanes) > 0:
            for j in range(len(lanes_test[i].free_turn_next_lane_points_with_angles)): # loop through the next_lane options
                next_lane = lanes_test[i].free_turn_next_lane_points_with_angles[j][0]
                move_points_temp = []
                move_points_temp.append(next_lane)
                for k in range(1,(len(lanes_test[i].free_turn_next_lane_points_with_angles[j])) - 1):
                    next_lane = lanes_test[i].free_turn_next_lane_points_with_angles[j][0]
                    move_point_x = lanes_test[i].free_turn_next_lane_points_with_angles[j][k][0] # start at start point of first line in lane
                    move_point_y = lanes_test[i].free_turn_next_lane_points_with_angles[j][k][1]
                    temp_angle = lanes_test[i].free_turn_next_lane_points_with_angles[j][k][2]
                    temp_line_end_point_x = lanes_test[i].free_turn_next_lane_points_with_angles[j][k + 1][0]
                    temp_line_end_point_y = lanes_test[i].free_turn_next_lane_points_with_angles[j][k + 1][1]
                    # canvas.create_oval(move_point_x-3,move_point_y-3,move_point_x+3,move_point_y+3,fill = 'green')
                    # canvas.create_oval(temp_line_end_point_x-3,temp_line_end_point_y-3,temp_line_end_point_x+3,temp_line_end_point_y+3,fill = 'red')
                    # tk.update()
                    # input("herer")
                    dist_to_end_point = math.sqrt(((abs(temp_line_end_point_y - move_point_y))**2) + ((abs(temp_line_end_point_x - move_point_x))**2))
                    if k == 1:
                        move_points_temp.append([move_point_x,move_point_y,temp_angle])
                    while dist_to_end_point > 0:
                        if dist_to_end_point < move_val: # set the move_point tpo the end_point
                            move_point_x = temp_line_end_point_x
                            move_point_y = temp_line_end_point_y
                        else:
                            move_point_x += move_val*math.sin(temp_angle)
                            move_point_y -= move_val*math.cos(temp_angle)
                            move_point_x_rounded = round(move_point_x)
                            move_point_y_rounded = round(move_point_y)
                        dist_to_end_point = math.sqrt(((abs(temp_line_end_point_y - move_point_y))**2) + ((abs(temp_line_end_point_x - move_point_x))**2))
                        move_points_temp.append([move_point_x,move_point_y,temp_angle])
                    lanes_test[i].free_turn_next_lane_move_points.append(move_points_temp)
find_free_turn_next_lane_move_points_in_lane(lanes_test)

######## create lights control
def turn_light_red(light_num):
    Control_display.turn_light_red(controls[light_num])
def turn_light_green(light_num):
    Control_display.turn_light_green(controls[light_num])
def turn_off_light(light_num):
    Control_display.turn_off_light(controls[light_num])
def create_controls(lanes_test,controls,Control_display):
    control_num = 0
    for i in range(len(lanes_test)):
        lane_end_point = lanes_test[i].points[-1]
        controls.append(Control_display(lane_end_point[0],lane_end_point[1],lanes_test,i,lw_half))
        lanes_test[i].control_num = i
        turn_light_red(lanes_test[i].control_num)
        # print("i_next_lanes: " + str(lanes_test[i].next_lanes))
        if lanes_test[i].next_lanes[0] == 9999: # an exit lane
            # print("i: " + str(i))
            turn_off_light(lanes_test[i].control_num)
create_controls(lanes_test,controls,Control_display)

### Store all car routes through the road network
def internal_lane_car_path_options_full():
    internal_lane_car_path_options_store = [[5, 35, 23, 56, 65, 40, 54, 64, 66, 33, 5, 35, 23, 56, 65, 62], [33, 5, 35, 23, 56, 65, 62], [52, 63, 31, 29, 3, 6], [26, 24, 45, 47, 37, 16, 2], [5, 35, 23, 56, 65, 40, 54, 64, 21, 23, 56, 65, 40, 54, 26, 49, 50, 34, 52, 63, 31, 29, 3, 6], [43, 13, 48, 49, 50, 34, 36, 55, 56, 65, 40, 54, 63, 31, 29, 3, 25, 27, 15, 31, 29, 3, 22, 44, 45, 47, 37, 16, 2], [25, 19, 29, 3, 25, 19, 29, 3, 25, 27, 48, 49, 50, 34, 36, 55, 56, 65, 62], [19, 29, 3, 1, 0], [53, 64, 66, 33, 5, 35, 23, 56, 65, 40, 54, 63, 31, 29, 3, 25, 19, 29, 3, 25, 19, 29, 3, 25, 27, 15, 66, 33, 5, 35, 23, 56, 65, 40, 42, 52, 26, 49, 50, 34, 52, 63, 31, 29, 3, 6], [22, 13, 15, 66, 33, 5, 35, 23, 56, 65, 40, 55, 56, 65, 40, 54, 26, 24, 45, 28, 50, 34, 52, 63, 31, 29, 3, 6], [15, 21, 23, 56, 65, 62], [5, 35, 23, 56, 65, 62], [44, 45, 47, 37, 16, 2], [18, 39, 46, 43, 20, 6], [64, 66, 33, 5, 35, 23, 56, 65, 40, 55, 56, 65, 40, 42, 32, 46, 43, 13, 48, 24, 45, 47, 59], [33, 5, 35, 23, 56, 65, 62], [35, 23, 56, 65, 62], [47, 59], [55, 56, 65, 40, 55, 56, 65, 40, 55, 56, 65, 62], [39, 30, 34, 36, 38, 62], [64, 66, 33, 5, 35, 23, 56, 65, 40, 42, 61], [55, 56, 65, 62], [40, 54, 26, 49, 50, 34, 52, 26, 49, 50, 34, 36, 54, 64, 66, 33, 5, 35, 23, 56, 65, 62], [18, 11, 41, 47, 30, 34, 61], [29, 3, 22, 13, 48, 49, 50, 34, 52, 26, 49, 50, 34, 52, 26, 49, 50, 34, 52, 26, 49, 50, 34, 52, 63, 31, 29, 3, 1, 2], [18, 11, 41, 28, 50, 34, 52, 26, 24, 45, 47, 30, 51, 50, 34, 61], [25, 27, 15, 21, 23, 56, 65, 62], [16, 0], [51, 50, 34, 61], [24, 45, 28, 50, 34, 61], [21, 23, 56, 65, 62], [64, 21, 23, 56, 65, 40, 54, 63, 31, 29, 3, 6], [1, 2], [64, 21, 23, 56, 65, 62], [21, 23, 56, 65, 62], [56, 65, 62], [47, 37, 11, 44, 45, 28, 50, 34, 61], [42, 52, 26, 49, 50, 34, 36, 54, 63, 31, 29, 3, 22, 17, 27, 48, 49, 50, 34, 61], [63, 31, 29, 3, 1, 0], [36, 38, 62], [25, 27, 15, 21, 23, 56, 65, 40, 42, 53, 64, 66, 33, 5, 35, 23, 56, 65, 62], [64, 21, 23, 56, 65, 40, 55, 56, 65, 40, 54, 64, 66, 33, 5, 35, 23, 56, 65, 40, 55, 56, 65, 62], [50, 34, 36, 55, 56, 65, 62], [27, 15, 31, 29, 3, 6], [54, 63, 31, 29, 3, 22, 17, 27, 15, 21, 23, 56, 65, 62], [64, 21, 23, 56, 65, 62], [24, 45, 28, 50, 34, 52, 26, 24, 45, 47, 37, 11, 13, 48, 24, 45, 47, 37, 16, 0], [54, 63, 31, 29, 3, 1, 18, 11, 13, 15, 31, 29, 3, 6], [5, 35, 23, 56, 65, 62], [39, 46, 43, 20, 6], [48, 24, 45, 28, 50, 34, 61], [41, 47, 37, 16, 0], [50, 34, 36, 55, 56, 65, 40, 54, 64, 66, 33, 5, 35, 23, 56, 65, 62], [28, 50, 34, 52, 63, 31, 29, 3, 22, 44, 45, 28, 50, 34, 36, 55, 56, 65, 62], [21, 23, 56, 65, 62], [25, 27, 15, 31, 29, 3, 22, 17, 27, 48, 24, 45, 47, 37, 11, 20, 6], [63, 31, 29, 3, 1, 2], [24, 45, 28, 50, 34, 36, 54, 63, 31, 29, 3, 25, 27, 15, 21, 23, 56, 65, 62], [45, 47, 37, 16, 0], [19, 29, 3, 25, 27, 15, 31, 29, 3, 6], [47, 30, 34, 36, 55, 56, 65, 62], [30, 51, 50, 34, 61], [45, 28, 50, 34, 52, 63, 31, 29, 3, 6], [47, 30, 34, 52, 63, 31, 29, 3, 25, 27, 48, 24, 45, 47, 30, 51, 50, 34, 61], [63, 31, 29, 3, 6], [1, 2], [19, 29, 3, 1, 2], [32, 46, 28, 50, 34, 61], [51, 50, 34, 61], [27, 15, 66, 33, 5, 35, 23, 56, 65, 62], [28, 50, 34, 52, 26, 49, 50, 34, 61], [21, 23, 56, 65, 62], [48, 49, 50, 34, 52, 63, 31, 29, 3, 22, 44, 45, 47, 30, 51, 50, 34, 36, 55, 56, 65, 62], [50, 34, 36, 54, 64, 66, 33, 5, 35, 23, 56, 65, 40, 55, 56, 65, 40, 54, 63, 31, 29, 3, 1, 18, 11, 44, 45, 28, 50, 34, 52, 63, 31, 29, 3, 1, 18, 39, 30, 34, 36, 55, 56, 65, 40, 54, 64, 21, 23, 56, 65, 40, 54, 64, 66, 33, 5, 35, 23, 56, 65, 62], [28, 50, 34, 36, 55, 56, 65, 40, 54, 64, 66, 33, 5, 35, 23, 56, 65, 40, 54, 26, 24, 45, 47, 59], [46, 28, 50, 34, 36, 38, 62], [36, 54, 26, 49, 50, 34, 61], [5, 35, 23, 56, 65, 40, 42, 52, 63, 31, 29, 3, 6], [51, 50, 34, 61], [31, 29, 3, 25, 27, 15, 21, 23, 56, 65, 40, 55, 56, 65, 62], [53, 64, 21, 23, 56, 65, 40, 42, 32, 37, 16, 2], [51, 50, 34, 36, 38, 62], [17, 19, 29, 3, 6], [63, 31, 29, 3, 6], [66, 33, 5, 35, 23, 56, 65, 40, 42, 53, 64, 21, 23, 56, 65, 62], [18, 39, 30, 51, 50, 34, 61], [5, 35, 23, 56, 65, 40, 54, 26, 49, 50, 34, 52, 26, 49, 50, 34, 36, 54, 64, 66, 33, 5, 35, 23, 56, 65, 40, 55, 56, 65, 62], [34, 61], [52, 63, 31, 29, 3, 6], [26, 24, 45, 47, 59], [38, 62], [51, 50, 34, 61], [33, 5, 35, 23, 56, 65, 62], [47, 30, 51, 50, 34, 36, 54, 63, 31, 29, 3, 22, 44, 45, 47, 37, 11, 20, 6], [37, 16, 0], [5, 35, 23, 56, 65, 62], [18, 39, 46, 43, 13, 15, 66, 33, 5, 35, 23, 56, 65, 40, 42, 32, 46, 28, 50, 34, 36, 38, 62], [26, 49, 50, 34, 36, 38, 62], [31, 29, 3, 1, 18, 39, 59], [66, 33, 5, 35, 23, 56, 65, 40, 54, 63, 31, 29, 3, 1, 0], [51, 50, 34, 36, 54, 26, 24, 45, 47, 37, 11, 20, 1, 18, 39, 30, 34, 61], [35, 23, 56, 65, 62], [28, 50, 34, 61], [26, 24, 45, 28, 50, 34, 36, 55, 56, 65, 62], [64, 66, 33, 5, 35, 23, 56, 65, 62], [31, 29, 3, 25, 19, 29, 3, 22, 17, 27, 15, 31, 29, 3, 6], [56, 65, 62], [65, 40, 42, 61], [55, 56, 65, 62], [16, 2], [50, 34, 61], [23, 56, 65, 62], [42, 53, 64, 66, 33, 5, 35, 23, 56, 65, 40, 55, 56, 65, 40, 42, 61], [27, 48, 24, 45, 28, 50, 34, 36, 54, 64, 66, 33, 5, 35, 23, 56, 65, 62], [29, 3, 6], [13, 48, 24, 45, 28, 50, 34, 61], [47, 30, 34, 36, 54, 64, 21, 23, 56, 65, 40, 55, 56, 65, 62], [63, 31, 29, 3, 6], [33, 5, 35, 23, 56, 65, 40, 54, 26, 49, 50, 34, 61], [50, 34, 52, 26, 24, 45, 28, 50, 34, 61], [20, 1, 0], [54, 26, 24, 45, 47, 37, 11, 41, 28, 50, 34, 61], [32, 37, 11, 13, 15, 21, 23, 56, 65, 62], [43, 13, 15, 66, 33, 5, 35, 23, 56, 65, 40, 55, 56, 65, 62], [22, 44, 45, 47, 59], [31, 29, 3, 6], [33, 5, 35, 23, 56, 65, 62], [65, 40, 42, 53, 64, 66, 33, 5, 35, 23, 56, 65, 62], [48, 49, 50, 34, 52, 63, 31, 29, 3, 6], [55, 56, 65, 62], [27, 48, 49, 50, 34, 61], [36, 54, 64, 21, 23, 56, 65, 40, 55, 56, 65, 62], [40, 54, 26, 24, 45, 47, 59], [44, 45, 47, 59], [1, 0], [19, 29, 3, 25, 19, 29, 3, 22, 17, 19, 29, 3, 6], [48, 24, 45, 28, 50, 34, 52, 63, 31, 29, 3, 1, 0], [42, 53, 64, 21, 23, 56, 65, 40, 55, 56, 65, 62], [50, 34, 36, 55, 56, 65, 62], [5, 35, 23, 56, 65, 40, 55, 56, 65, 40, 42, 32, 59], [15, 21, 23, 56, 65, 40, 55, 56, 65, 62], [35, 23, 56, 65, 40, 42, 61], [63, 31, 29, 3, 22, 17, 19, 29, 3, 6], [41, 43, 20, 1, 0], [43, 13, 48, 24, 45, 47, 59], [45, 47, 30, 51, 50, 34, 61], [18, 11, 20, 1, 0], [18, 39, 59], [53, 64, 66, 33, 5, 35, 23, 56, 65, 40, 54, 26, 49, 50, 34, 52, 26, 49, 50, 34, 61], [47, 37, 11, 20, 1, 18, 11, 41, 47, 59], [44, 45, 28, 50, 34, 52, 63, 31, 29, 3, 1, 18, 11, 20, 6], [43, 20, 6], [29, 3, 25, 19, 29, 3, 25, 27, 15, 21, 23, 56, 65, 62], [40, 54, 64, 66, 33, 5, 35, 23, 56, 65, 40, 54, 64, 21, 23, 56, 65, 40, 42, 32, 59], [37, 11, 20, 1, 18, 11, 44, 45, 47, 30, 34, 52, 26, 24, 45, 28, 50, 34, 36, 55, 56, 65, 62], [19, 29, 3, 22, 13, 15, 66, 33, 5, 35, 23, 56, 65, 62], [24, 45, 47, 59], [22, 17, 19, 29, 3, 1, 18, 11, 20, 1, 0], [5, 35, 23, 56, 65, 62], [16, 0], [3, 1, 18, 39, 30, 51, 50, 34, 61], [36, 55, 56, 65, 40, 54, 26, 24, 45, 28, 50, 34, 36, 38, 62], [25, 27, 15, 31, 29, 3, 6], [48, 49, 50, 34, 36, 55, 56, 65, 40, 42, 52, 26, 24, 45, 47, 30, 51, 50, 34, 36, 55, 56, 65, 40, 54, 64, 66, 33, 5, 35, 23, 56, 65, 40, 54, 64, 66, 33, 5, 35, 23, 56, 65, 62], [21, 23, 56, 65, 40, 55, 56, 65, 40, 54, 26, 24, 45, 47, 30, 51, 50, 34, 52, 26, 24, 45, 47, 59], [66, 33, 5, 35, 23, 56, 65, 40, 55, 56, 65, 40, 42, 53, 64, 21, 23, 56, 65, 62], [50, 34, 61], [15, 31, 29, 3, 22, 17, 19, 29, 3, 22, 44, 45, 28, 50, 34, 36, 38, 62], [36, 54, 63, 31, 29, 3, 6], [63, 31, 29, 3, 22, 44, 45, 28, 50, 34, 61], [27, 15, 21, 23, 56, 65, 62], [54, 63, 31, 29, 3, 25, 27, 15, 31, 29, 3, 6], [51, 50, 34, 52, 26, 24, 45, 47, 59], [36, 54, 26, 24, 45, 47, 37, 16, 2], [3, 22, 17, 27, 48, 49, 50, 34, 52, 63, 31, 29, 3, 25, 27, 48, 24, 45, 28, 50, 34, 36, 54, 26, 24, 45, 47, 59], [19, 29, 3, 22, 17, 27, 48, 24, 45, 47, 59], [35, 23, 56, 65, 40, 54, 64, 21, 23, 56, 65, 40, 42, 61], [34, 52, 63, 31, 29, 3, 6], [31, 29, 3, 1, 18, 39, 59], [37, 11, 44, 45, 28, 50, 34, 52, 26, 24, 45, 47, 30, 34, 36, 55, 56, 65, 62], [27, 15, 21, 23, 56, 65, 62], [21, 23, 56, 65, 62], [30, 34, 52, 26, 49, 50, 34, 61], [32, 37, 16, 0], [41, 28, 50, 34, 61], [11, 20, 1, 18, 11, 44, 45, 47, 59], [39, 59], [1, 0], [35, 23, 56, 65, 40, 55, 56, 65, 62], [44, 45, 28, 50, 34, 52, 63, 31, 29, 3, 6], [13, 48, 49, 50, 34, 52, 26, 49, 50, 34, 52, 63, 31, 29, 3, 22, 44, 45, 47, 30, 51, 50, 34, 61], [30, 51, 50, 34, 36, 38, 62], [1, 18, 39, 59], [31, 29, 3, 1, 2], [40, 55, 56, 65, 40, 54, 64, 66, 33, 5, 35, 23, 56, 65, 62], [51, 50, 34, 61], [17, 19, 29, 3, 25, 19, 29, 3, 25, 27, 15, 21, 23, 56, 65, 40, 55, 56, 65, 40, 54, 26, 49, 50, 34, 36, 55, 56, 65, 62], [33, 5, 35, 23, 56, 65, 40, 42, 32, 37, 16, 0], [28, 50, 34, 61], [35, 23, 56, 65, 62], [19, 29, 3, 22, 17, 27, 48, 24, 45, 28, 50, 34, 52, 63, 31, 29, 3, 22, 13, 48, 49, 50, 34, 36, 54, 63, 31, 29, 3, 25, 27, 15, 31, 29, 3, 6], [5, 35, 23, 56, 65, 62], [41, 43, 20, 1, 2], [5, 35, 23, 56, 65, 40, 42, 32, 59], [19, 29, 3, 22, 44, 45, 28, 50, 34, 36, 38, 62], [11, 13, 15, 21, 23, 56, 65, 62], [34, 52, 26, 24, 45, 28, 50, 34, 36, 55, 56, 65, 40, 54, 63, 31, 29, 3, 6], [42, 53, 64, 21, 23, 56, 65, 40, 42, 61], [42, 32, 59], [42, 61], [54, 64, 21, 23, 56, 65, 40, 55, 56, 65, 40, 42, 52, 26, 24, 45, 47, 30, 51, 50, 34, 36, 38, 62], [50, 34, 36, 54, 26, 24, 45, 28, 50, 34, 52, 26, 24, 45, 28, 50, 34, 36, 55, 56, 65, 40, 55, 56, 65, 40, 42, 61], [23, 56, 65, 62], [30, 51, 50, 34, 36, 54, 64, 66, 33, 5, 35, 23, 56, 65, 40, 42, 52, 26, 24, 45, 28, 50, 34, 36, 55, 56, 65, 62], [38, 62], [45, 28, 50, 34, 36, 54, 64, 66, 33, 5, 35, 23, 56, 65, 62], [11, 20, 6], [28, 50, 34, 61], [31, 29, 3, 6], [46, 28, 50, 34, 61], [17, 19, 29, 3, 25, 19, 29, 3, 25, 27, 48, 24, 45, 28, 50, 34, 52, 63, 31, 29, 3, 1, 0], [41, 47, 59], [45, 47, 30, 51, 50, 34, 61], [22, 13, 48, 24, 45, 28, 50, 34, 36, 54, 64, 66, 33, 5, 35, 23, 56, 65, 62], [23, 56, 65, 62], [32, 59], [64, 21, 23, 56, 65, 62], [46, 43, 13, 48, 24, 45, 28, 50, 34, 61], [27, 48, 24, 45, 47, 30, 34, 36, 54, 63, 31, 29, 3, 25, 27, 15, 31, 29, 3, 1, 2], [39, 30, 34, 61], [11, 41, 28, 50, 34, 36, 54, 26, 49, 50, 34, 52, 26, 24, 45, 47, 30, 34, 61], [33, 5, 35, 23, 56, 65, 62], [1, 0], [66, 33, 5, 35, 23, 56, 65, 40, 42, 61], [48, 49, 50, 34, 61], [32, 37, 16, 0], [17, 27, 15, 21, 23, 56, 65, 40, 55, 56, 65, 62], [47, 37, 11, 20, 1, 18, 39, 30, 51, 50, 34, 52, 26, 24, 45, 28, 50, 34, 61], [18, 39, 59], [56, 65, 40, 42, 32, 59], [11, 20, 1, 18, 11, 20, 6], [54, 26, 49, 50, 34, 61], [18, 39, 46, 28, 50, 34, 36, 38, 62], [50, 34, 52, 26, 24, 45, 47, 30, 34, 52, 63, 31, 29, 3, 22, 17, 19, 29, 3, 1, 2], [64, 21, 23, 56, 65, 62], [40, 42, 32, 37, 11, 41, 43, 20, 1, 18, 39, 46, 43, 20, 6], [37, 11, 44, 45, 47, 30, 34, 52, 26, 24, 45, 47, 59], [16, 0], [45, 47, 37, 16, 2], [20, 1, 2], [26, 49, 50, 34, 52, 63, 31, 29, 3, 6], [25, 19, 29, 3, 1, 2], [46, 28, 50, 34, 36, 55, 56, 65, 62], [56, 65, 40, 54, 63, 31, 29, 3, 6], [21, 23, 56, 65, 40, 55, 56, 65, 40, 55, 56, 65, 62], [56, 65, 40, 55, 56, 65, 62], [48, 49, 50, 34, 52, 63, 31, 29, 3, 25, 27, 15, 31, 29, 3, 25, 27, 15, 31, 29, 3, 25, 27, 15, 66, 33, 5, 35, 23, 56, 65, 40, 42, 52, 63, 31, 29, 3, 22, 44, 45, 28, 50, 34, 61], [22, 17, 19, 29, 3, 22, 44, 45, 47, 30, 34, 36, 55, 56, 65, 40, 42, 52, 63, 31, 29, 3, 25, 27, 15, 66, 33, 5, 35, 23, 56, 65, 62], [13, 15, 66, 33, 5, 35, 23, 56, 65, 40, 42, 53, 64, 21, 23, 56, 65, 40, 55, 56, 65, 62], [5, 35, 23, 56, 65, 62], [39, 30, 34, 36, 55, 56, 65, 40, 54, 63, 31, 29, 3, 6], [66, 33, 5, 35, 23, 56, 65, 40, 54, 64, 66, 33, 5, 35, 23, 56, 65, 62], [45, 47, 59], [24, 45, 47, 30, 34, 61], [53, 64, 21, 23, 56, 65, 40, 55, 56, 65, 40, 42, 53, 64, 66, 33, 5, 35, 23, 56, 65, 62], [33, 5, 35, 23, 56, 65, 62], [39, 30, 51, 50, 34, 52, 63, 31, 29, 3, 22, 17, 27, 48, 49, 50, 34, 61], [48, 49, 50, 34, 36, 38, 62], [20, 6], [7, 10], [20, 1, 2], [16, 0], [19, 29, 3, 6], [16, 2], [52, 63, 31, 29, 3, 22, 44, 45, 28, 50, 34, 36, 38, 62], [42, 52, 26, 24, 45, 47, 30, 34, 52, 26, 49, 50, 34, 61], [65, 62], [17, 19, 29, 3, 25, 19, 29, 3, 6], [38, 62], [13, 48, 49, 50, 34, 61], [51, 50, 34, 61], [13, 15, 31, 29, 3, 1, 2], [44, 45, 47, 30, 34, 36, 55, 56, 65, 62], [38, 62], [54, 63, 31, 29, 3, 25, 27, 15, 21, 23, 56, 65, 62], [22, 17, 27, 15, 31, 29, 3, 1, 18, 39, 30, 34, 36, 38, 62], [31, 29, 3, 22, 13, 15, 66, 33, 5, 35, 23, 56, 65, 40, 55, 56, 65, 40, 42, 53, 64, 66, 33, 5, 35, 23, 56, 65, 40, 54, 63, 31, 29, 3, 6], [63, 31, 29, 3, 1, 2], [55, 56, 65, 40, 42, 61], [47, 59], [24, 45, 28, 50, 34, 52, 26, 49, 50, 34, 36, 54, 63, 31, 29, 3, 22, 17, 27, 48, 49, 50, 34, 61], [37, 16, 0], [36, 38, 62], [31, 29, 3, 25, 19, 29, 3, 6], [42, 61], [18, 39, 46, 43, 20, 1, 2], [15, 31, 29, 3, 1, 0], [30, 34, 61], [27, 48, 49, 50, 34, 52, 26, 24, 45, 47, 30, 34, 36, 38, 62], [33, 5, 35, 23, 56, 65, 40, 54, 26, 49, 50, 34, 61], [41, 47, 59], [33, 5, 35, 23, 56, 65, 40, 54, 63, 31, 29, 3, 25, 27, 15, 31, 29, 3, 25, 19, 29, 3, 22, 17, 19, 29, 3, 6], [11, 13, 15, 31, 29, 3, 6], [40, 55, 56, 65, 40, 55, 56, 65, 40, 54, 64, 66, 33, 5, 35, 23, 56, 65, 62], [22, 17, 19, 29, 3, 25, 19, 29, 3, 6], [47, 37, 11, 20, 1, 18, 39, 46, 28, 50, 34, 36, 54, 63, 31, 29, 3, 1, 18, 39, 59], [38, 62], [38, 62], [65, 40, 42, 32, 37, 16, 2], [40, 42, 32, 46, 43, 13, 15, 31, 29, 3, 22, 44, 45, 28, 50, 34, 61], [54, 26, 49, 50, 34, 36, 54, 26, 49, 50, 34, 36, 55, 56, 65, 40, 42, 53, 64, 21, 23, 56, 65, 40, 55, 56, 65, 40, 55, 56, 65, 40, 42, 53, 64, 21, 23, 56, 65, 40, 54, 26, 24, 45, 47, 30, 34, 36, 38, 62], [40, 54, 64, 21, 23, 56, 65, 40, 55, 56, 65, 40, 42, 61], [3, 25, 27, 48, 49, 50, 34, 61], [65, 40, 54, 26, 49, 50, 34, 61], [13, 48, 49, 50, 34, 61], [11, 44, 45, 28, 50, 34, 52, 63, 31, 29, 3, 6], [1, 0], [24, 45, 28, 50, 34, 61], [27, 48, 24, 45, 47, 30, 34, 36, 55, 56, 65, 40, 42, 53, 64, 66, 33, 5, 35, 23, 56, 65, 40, 55, 56, 65, 62], [40, 55, 56, 65, 62], [5, 35, 23, 56, 65, 40, 42, 53, 64, 66, 33, 5, 35, 23, 56, 65, 62], [34, 36, 55, 56, 65, 62], [55, 56, 65, 40, 54, 63, 31, 29, 3, 22, 13, 15, 31, 29, 3, 25, 27, 15, 66, 33, 5, 35, 23, 56, 65, 62], [37, 11, 41, 43, 20, 1, 2], [13, 15, 31, 29, 3, 22, 13, 48, 24, 45, 28, 50, 34, 61], [33, 5, 35, 23, 56, 65, 40, 54, 63, 31, 29, 3, 1, 2], [37, 11, 20, 6], [54, 64, 66, 33, 5, 35, 23, 56, 65, 40, 42, 53, 64, 21, 23, 56, 65, 40, 42, 52, 26, 24, 45, 28, 50, 34, 61], [63, 31, 29, 3, 1, 2], [52, 63, 31, 29, 3, 6], [13, 48, 24, 45, 28, 50, 34, 52, 26, 49, 50, 34, 52, 63, 31, 29, 3, 1, 2], [63, 31, 29, 3, 22, 44, 45, 47, 59], [52, 26, 24, 45, 28, 50, 34, 61], [7, 3, 25, 19, 29, 3, 1, 2], [45, 47, 30, 51, 50, 34, 36, 55, 56, 65, 62], [64, 21, 23, 56, 65, 40, 55, 56, 65, 40, 55, 56, 65, 62], [28, 50, 34, 52, 63, 31, 29, 3, 25, 27, 48, 24, 45, 28, 50, 34, 36, 54, 26, 49, 50, 34, 36, 38, 62], [26, 49, 50, 34, 36, 55, 56, 65, 40, 55, 56, 65, 40, 55, 56, 65, 62], [44, 45, 28, 50, 34, 61], [64, 21, 23, 56, 65, 40, 54, 26, 49, 50, 34, 36, 38, 62], [42, 52, 63, 31, 29, 3, 1, 18, 39, 59], [44, 45, 47, 59], [47, 59], [37, 11, 41, 43, 20, 1, 2], [18, 11, 13, 15, 21, 23, 56, 65, 40, 55, 56, 65, 62], [66, 33, 5, 35, 23, 56, 65, 40, 54, 26, 24, 45, 28, 50, 34, 52, 26, 49, 50, 34, 36, 54, 64, 21, 23, 56, 65, 62], [42, 61], [44, 45, 28, 50, 34, 61], [48, 49, 50, 34, 61], [35, 23, 56, 65, 62], [37, 16, 2], [35, 23, 56, 65, 40, 55, 56, 65, 40, 55, 56, 65, 62], [54, 26, 24, 45, 47, 30, 51, 50, 34, 52, 63, 31, 29, 3, 25, 19, 29, 3, 6], [35, 23, 56, 65, 62], [22, 13, 48, 24, 45, 28, 50, 34, 61], [63, 31, 29, 3, 25, 27, 48, 24, 45, 28, 50, 34, 52, 26, 49, 50, 34, 52, 63, 31, 29, 3, 22, 13, 15, 21, 23, 56, 65, 62], [16, 2], [22, 13, 48, 49, 50, 34, 61], [35, 23, 56, 65, 40, 55, 56, 65, 62], [20, 1, 0], [51, 50, 34, 52, 26, 49, 50, 34, 61], [37, 11, 41, 47, 37, 11, 44, 45, 47, 37, 16, 2], [54, 64, 21, 23, 56, 65, 40, 42, 52, 63, 31, 29, 3, 1, 18, 11, 13, 15, 31, 29, 3, 22, 13, 48, 24, 45, 28, 50, 34, 52, 63, 31, 29, 3, 6], [44, 45, 28, 50, 34, 52, 26, 49, 50, 34, 61], [39, 59], [20, 6], [11, 41, 47, 30, 51, 50, 34, 52, 63, 31, 29, 3, 1, 18, 11, 41, 43, 20, 6], [17, 27, 15, 21, 23, 56, 65, 40, 55, 56, 65, 40, 55, 56, 65, 62], [53, 64, 66, 33, 5, 35, 23, 56, 65, 62], [63, 31, 29, 3, 1, 18, 11, 44, 45, 47, 59], [33, 5, 35, 23, 56, 65, 62], [38, 62], [23, 56, 65, 62], [31, 29, 3, 22, 13, 15, 31, 29, 3, 1, 0], [30, 51, 50, 34, 61], [46, 43, 20, 6], [55, 56, 65, 40, 42, 32, 46, 43, 13, 15, 31, 29, 3, 1, 2], [41, 28, 50, 34, 61], [24, 45, 47, 37, 16, 0], [37, 16, 0], [47, 30, 34, 61], [35, 23, 56, 65, 40, 42, 52, 26, 24, 45, 47, 37, 11, 20, 6], [15, 66, 33, 5, 35, 23, 56, 65, 62], [22, 13, 48, 49, 50, 34, 36, 54, 26, 24, 45, 47, 37, 11, 44, 45, 47, 59], [5, 35, 23, 56, 65, 40, 55, 56, 65, 62], [55, 56, 65, 62], [46, 28, 50, 34, 36, 54, 64, 21, 23, 56, 65, 40, 54, 26, 49, 50, 34, 52, 63, 31, 29, 3, 6], [13, 48, 24, 45, 28, 50, 34, 36, 38, 62], [35, 23, 56, 65, 40, 55, 56, 65, 40, 55, 56, 65, 62], [53, 64, 66, 33, 5, 35, 23, 56, 65, 62], [39, 46, 28, 50, 34, 36, 54, 64, 21, 23, 56, 65, 62], [36, 38, 62], [34, 61], [13, 48, 24, 45, 28, 50, 34, 36, 54, 63, 31, 29, 3, 25, 27, 48, 24, 45, 28, 50, 34, 52, 26, 49, 50, 34, 36, 38, 62], [5, 35, 23, 56, 65, 62], [24, 45, 47, 30, 51, 50, 34, 52, 63, 31, 29, 3, 6], [47, 30, 51, 50, 34, 61], [40, 54, 26, 49, 50, 34, 61], [38, 62], [33, 5, 35, 23, 56, 65, 40, 54, 26, 49, 50, 34, 61], [13, 48, 24, 45, 28, 50, 34, 52, 63, 31, 29, 3, 6], [45, 47, 30, 34, 36, 54, 64, 66, 33, 5, 35, 23, 56, 65, 40, 55, 56, 65, 62], [7, 3, 25, 27, 15, 21, 23, 56, 65, 40, 42, 61], [18, 39, 30, 34, 52, 26, 49, 50, 34, 52, 26, 24, 45, 47, 59], [7, 3, 6], [5, 35, 23, 56, 65, 62], [25, 27, 48, 49, 50, 34, 36, 55, 56, 65, 62], [19, 29, 3, 6], [24, 45, 28, 50, 34, 61], [53, 64, 66, 33, 5, 35, 23, 56, 65, 40, 42, 32, 59], [38, 62], [13, 15, 21, 23, 56, 65, 62], [64, 21, 23, 56, 65, 62], [52, 63, 31, 29, 3, 25, 27, 15, 21, 23, 56, 65, 62], [36, 55, 56, 65, 40, 55, 56, 65, 62], [22, 17, 19, 29, 3, 25, 27, 48, 49, 50, 34, 52, 63, 31, 29, 3, 6], [13, 48, 49, 50, 34, 36, 54, 63, 31, 29, 3, 1, 18, 11, 13, 15, 21, 23, 56, 65, 62], [49, 50, 34, 61], [22, 13, 15, 66, 33, 5, 35, 23, 56, 65, 40, 55, 56, 65, 62], [16, 0], [51, 50, 34, 52, 26, 24, 45, 47, 30, 34, 52, 26, 49, 50, 34, 61], [22, 17, 27, 15, 66, 33, 5, 35, 23, 56, 65, 40, 54, 26, 24, 45, 47, 59], [34, 52, 26, 24, 45, 47, 37, 16, 2], [40, 55, 56, 65, 40, 55, 56, 65, 40, 54, 64, 21, 23, 56, 65, 40, 55, 56, 65, 62], [29, 3, 6], [29, 3, 6], [64, 21, 23, 56, 65, 62], [37, 11, 20, 1, 2], [21, 23, 56, 65, 40, 54, 63, 31, 29, 3, 1, 0], [41, 47, 37, 11, 13, 15, 31, 29, 3, 1, 0], [42, 61], [26, 24, 45, 28, 50, 34, 61], [23, 56, 65, 62], [65, 62], [34, 36, 54, 64, 66, 33, 5, 35, 23, 56, 65, 62], [55, 56, 65, 40, 55, 56, 65, 62], [23, 56, 65, 40, 42, 32, 46, 28, 50, 34, 36, 55, 56, 65, 62], [20, 6], [42, 61], [7, 10], [35, 23, 56, 65, 62], [32, 37, 16, 2], [51, 50, 34, 61], [17, 19, 29, 3, 22, 44, 45, 28, 50, 34, 52, 63, 31, 29, 3, 22, 44, 45, 28, 50, 34, 36, 54, 26, 24, 45, 47, 30, 51, 50, 34, 61], [16, 0], [54, 63, 31, 29, 3, 25, 27, 48, 24, 45, 28, 50, 34, 36, 54, 64, 66, 33, 5, 35, 23, 56, 65, 40, 54, 63, 31, 29, 3, 6], [45, 28, 50, 34, 52, 63, 31, 29, 3, 25, 27, 15, 31, 29, 3, 6], [48, 49, 50, 34, 36, 54, 26, 24, 45, 28, 50, 34, 52, 63, 31, 29, 3, 1, 2], [44, 45, 28, 50, 34, 36, 38, 62], [33, 5, 35, 23, 56, 65, 62], [55, 56, 65, 40, 54, 63, 31, 29, 3, 25, 19, 29, 3, 1, 18, 11, 20, 1, 18, 39, 30, 51, 50, 34, 36, 55, 56, 65, 40, 42, 61], [53, 64, 66, 33, 5, 35, 23, 56, 65, 62], [55, 56, 65, 62], [34, 36, 55, 56, 65, 62], [64, 66, 33, 5, 35, 23, 56, 65, 40, 55, 56, 65, 62], [42, 53, 64, 21, 23, 56, 65, 40, 54, 26, 49, 50, 34, 61], [17, 27, 48, 49, 50, 34, 61], [43, 20, 6], [41, 47, 30, 51, 50, 34, 61], [45, 47, 37, 11, 44, 45, 28, 50, 34, 61], [15, 66, 33, 5, 35, 23, 56, 65, 40, 54, 26, 49, 50, 34, 36, 54, 63, 31, 29, 3, 1, 2], [37, 16, 2], [40, 42, 61], [23, 56, 65, 40, 54, 63, 31, 29, 3, 22, 13, 15, 66, 33, 5, 35, 23, 56, 65, 40, 54, 64, 66, 33, 5, 35, 23, 56, 65, 62], [46, 28, 50, 34, 61], [31, 29, 3, 6], [33, 5, 35, 23, 56, 65, 62], [47, 37, 11, 41, 43, 20, 1, 2], [28, 50, 34, 36, 54, 64, 66, 33, 5, 35, 23, 56, 65, 40, 55, 56, 65, 40, 54, 26, 49, 50, 34, 52, 26, 49, 50, 34, 61], [28, 50, 34, 61], [46, 43, 13, 15, 66, 33, 5, 35, 23, 56, 65, 62], [23, 56, 65, 40, 55, 56, 65, 62], [55, 56, 65, 62], [29, 3, 25, 27, 15, 66, 33, 5, 35, 23, 56, 65, 40, 54, 26, 49, 50, 34, 36, 54, 26, 24, 45, 47, 59], [16, 0], [37, 11, 13, 48, 49, 50, 34, 61], [33, 5, 35, 23, 56, 65, 40, 55, 56, 65, 40, 54, 26, 49, 50, 34, 61], [15, 21, 23, 56, 65, 62], [63, 31, 29, 3, 6], [51, 50, 34, 36, 54, 64, 66, 33, 5, 35, 23, 56, 65, 40, 54, 64, 21, 23, 56, 65, 62], [20, 6], [23, 56, 65, 62], [45, 47, 37, 16, 2], [29, 3, 25, 27, 15, 66, 33, 5, 35, 23, 56, 65, 62], [13, 15, 21, 23, 56, 65, 40, 55, 56, 65, 40, 54, 63, 31, 29, 3, 6], [34, 61], [45, 28, 50, 34, 52, 26, 24, 45, 28, 50, 34, 36, 54, 63, 31, 29, 3, 1, 0], [7, 10], [51, 50, 34, 52, 26, 24, 45, 28, 50, 34, 36, 55, 56, 65, 62], [7, 10], [63, 31, 29, 3, 22, 17, 27, 15, 31, 29, 3, 25, 27, 48, 49, 50, 34, 52, 26, 24, 45, 47, 59], [30, 51, 50, 34, 61], [34, 61], [48, 49, 50, 34, 52, 26, 49, 50, 34, 61], [66, 33, 5, 35, 23, 56, 65, 62], [50, 34, 61], [52, 63, 31, 29, 3, 6], [53, 64, 21, 23, 56, 65, 62], [36, 55, 56, 65, 40, 42, 32, 59], [64, 21, 23, 56, 65, 40, 42, 53, 64, 66, 33, 5, 35, 23, 56, 65, 40, 55, 56, 65, 62]]
    return internal_lane_car_path_options_store
internal_lane_car_path_options_store = internal_lane_car_path_options_full()
def entry_lane_car_path_options_full():
    entry_lane_car_path_options_store =  [[57, 65, 40, 54, 64, 21, 23, 56, 65, 40, 54, 26, 49, 50, 34, 61], [14, 7, 10], [9, 16, 2], [58, 30, 34, 36, 38, 62], [60, 53, 64, 21, 23, 56, 65, 62], [4, 18, 11, 41, 43, 20, 1, 0], [9, 11, 20, 6], [57, 65, 62], [9, 16, 2], [14, 7, 10], [4, 18, 39, 46, 28, 50, 34, 61], [60, 52, 63, 31, 29, 3, 25, 27, 15, 66, 33, 5, 35, 23, 56, 65, 40, 54, 26, 24, 45, 47, 59], [12, 3, 1, 18, 39, 59], [57, 65, 40, 54, 64, 66, 33, 5, 35, 23, 56, 65, 40, 42, 53, 64, 21, 23, 56, 65, 62], [14, 35, 23, 56, 65, 62], [57, 65, 40, 55, 56, 65, 40, 55, 56, 65, 40, 54, 64, 66, 33, 5, 35, 23, 56, 65, 62], [4, 0], [12, 3, 25, 27, 48, 49, 50, 34, 61], [14, 35, 23, 56, 65, 40, 42, 61], [8, 22, 13, 48, 49, 50, 34, 61], [9, 39, 59], [14, 35, 23, 56, 65, 62], [9, 11, 41, 47, 30, 34, 36, 38, 62], [8, 22, 44, 45, 47, 30, 51, 50, 34, 36, 38, 62], [9, 16, 2], [58, 46, 28, 50, 34, 36, 54, 64, 21, 23, 56, 65, 62], [14, 35, 23, 56, 65, 40, 55, 56, 65, 40, 54, 26, 24, 45, 47, 30, 51, 50, 34, 36, 54, 63, 31, 29, 3, 22, 13, 15, 66, 33, 5, 35, 23, 56, 65, 40, 55, 56, 65, 62], [58, 37, 11, 41, 43, 20, 1, 0], [58, 37, 16, 2], [57, 65, 62], [12, 5, 35, 23, 56, 65, 40, 42, 52, 26, 49, 50, 34, 61], [58, 37, 16, 0], [4, 18, 11, 44, 45, 28, 50, 34, 36, 54, 64, 66, 33, 5, 35, 23, 56, 65, 40, 54, 63, 31, 29, 3, 1, 18, 39, 30, 51, 50, 34, 36, 38, 62], [14, 7, 10], [4, 0], [14, 35, 23, 56, 65, 62], [8, 22, 13, 15, 66, 33, 5, 35, 23, 56, 65, 40, 55, 56, 65, 62], [12, 3, 22, 44, 45, 28, 50, 34, 36, 38, 62], [8, 1, 18, 39, 30, 34, 52, 63, 31, 29, 3, 1, 2], [4, 0], [60, 52, 63, 31, 29, 3, 22, 44, 45, 28, 50, 34, 52, 26, 24, 45, 47, 59], [60, 52, 26, 49, 50, 34, 61], [9, 39, 46, 43, 13, 48, 24, 45, 47, 30, 51, 50, 34, 61], [58, 37, 16, 0], [58, 46, 43, 13, 15, 21, 23, 56, 65, 40, 55, 56, 65, 62], [57, 65, 40, 55, 56, 65, 62], [14, 35, 23, 56, 65, 62], [8, 1, 0], [9, 39, 30, 51, 50, 34, 52, 63, 31, 29, 3, 6], [12, 3, 1, 0], [60, 53, 64, 21, 23, 56, 65, 62], [14, 7, 10], [9, 11, 13, 15, 66, 33, 5, 35, 23, 56, 65, 40, 42, 53, 64, 21, 23, 56, 65, 40, 54, 26, 24, 45, 47, 59], [12, 5, 35, 23, 56, 65, 40, 55, 56, 65, 40, 42, 53, 64, 66, 33, 5, 35, 23, 56, 65, 62], [58, 37, 16, 0], [14, 7, 3, 25, 19, 29, 3, 1, 0], [12, 3, 6], [9, 11, 41, 43, 20, 6], [9, 39, 46, 43, 20, 1, 0], [60, 36, 55, 56, 65, 62], [57, 65, 62], [60, 32, 46, 43, 13, 15, 21, 23, 56, 65, 40, 42, 32, 59], [4, 0], [60, 52, 63, 31, 29, 3, 6], [9, 11, 44, 45, 47, 30, 51, 50, 34, 36, 38, 62], [9, 39, 46, 28, 50, 34, 52, 26, 24, 45, 28, 50, 34, 36, 54, 26, 24, 45, 28, 50, 34, 61], [8, 1, 2], [12, 3, 22, 44, 45, 47, 59], [8, 1, 0], [8, 22, 17, 27, 48, 49, 50, 34, 52, 63, 31, 29, 3, 6], [9, 16, 0], [57, 65, 40, 55, 56, 65, 62], [12, 3, 1, 0], [14, 35, 23, 56, 65, 62], [9, 16, 2], [12, 3, 25, 19, 29, 3, 25, 19, 29, 3, 25, 19, 29, 3, 1, 18, 39, 46, 28, 50, 34, 36, 54, 64, 66, 33, 5, 35, 23, 56, 65, 62], [60, 53, 64, 21, 23, 56, 65, 40, 55, 56, 65, 40, 42, 53, 64, 21, 23, 56, 65, 40, 54, 26, 49, 50, 34, 61], [14, 7, 3, 1, 2], [58, 30, 34, 52, 63, 31, 29, 3, 1, 0], [12, 3, 6], [60, 32, 46, 28, 50, 34, 36, 55, 56, 65, 62], [57, 65, 62], [14, 35, 23, 56, 65, 40, 42, 32, 37, 11, 20, 6], [14, 35, 23, 56, 65, 40, 54, 26, 49, 50, 34, 52, 63, 31, 29, 3, 22, 44, 45, 47, 30, 34, 52, 26, 49, 50, 34, 36, 55, 56, 65, 40, 42, 61], [4, 0], [14, 35, 23, 56, 65, 62], [58, 46, 43, 13, 48, 24, 45, 47, 30, 34, 52, 63, 31, 29, 3, 1, 18, 11, 41, 47, 30, 51, 50, 34, 36, 55, 56, 65, 40, 54, 26, 24, 45, 28, 50, 34, 52, 63, 31, 29, 3, 25, 27, 15, 66, 33, 5, 35, 23, 56, 65, 62], [12, 3, 22, 17, 27, 15, 21, 23, 56, 65, 40, 55, 56, 65, 40, 54, 63, 31, 29, 3, 22, 44, 45, 28, 50, 34, 36, 55, 56, 65, 40, 54, 26, 24, 45, 28, 50, 34, 52, 26, 24, 45, 28, 50, 34, 36, 55, 56, 65, 62], [58, 30, 34, 52, 26, 49, 50, 34, 52, 63, 31, 29, 3, 1, 0], [14, 7, 3, 25, 27, 48, 24, 45, 47, 37, 16, 0], [8, 22, 13, 15, 31, 29, 3, 6], [60, 52, 63, 31, 29, 3, 22, 17, 27, 15, 21, 23, 56, 65, 40, 54, 26, 24, 45, 28, 50, 34, 52, 26, 24, 45, 28, 50, 34, 61], [4, 0], [14, 7, 3, 6], [58, 30, 51, 50, 34, 52, 26, 24, 45, 47, 37, 16, 0], [8, 22, 17, 19, 29, 3, 1, 0], [14, 7, 3, 25, 27, 15, 21, 23, 56, 65, 62], [60, 32, 37, 11, 41, 47, 30, 34, 52, 63, 31, 29, 3, 25, 19, 29, 3, 6], [4, 18, 11, 13, 48, 49, 50, 34, 36, 38, 62], [14, 35, 23, 56, 65, 62], [9, 16, 2], [12, 5, 35, 23, 56, 65, 40, 54, 64, 21, 23, 56, 65, 40, 54, 63, 31, 29, 3, 1, 0], [4, 18, 39, 46, 43, 13, 15, 31, 29, 3, 6], [9, 39, 59], [8, 22, 44, 45, 47, 59], [12, 5, 35, 23, 56, 65, 62], [58, 46, 28, 50, 34, 36, 38, 62], [14, 7, 3, 25, 27, 15, 31, 29, 3, 22, 44, 45, 28, 50, 34, 36, 55, 56, 65, 40, 54, 63, 31, 29, 3, 6], [60, 53, 64, 66, 33, 5, 35, 23, 56, 65, 62], [4, 0], [9, 11, 20, 6], [57, 65, 62], [57, 65, 40, 55, 56, 65, 40, 55, 56, 65, 62], [57, 65, 62], [57, 65, 62], [8, 1, 0], [8, 22, 17, 27, 15, 66, 33, 5, 35, 23, 56, 65, 40, 55, 56, 65, 62], [4, 18, 11, 13, 48, 49, 50, 34, 61], [60, 36, 55, 56, 65, 62], [57, 65, 40, 54, 26, 24, 45, 47, 59], [14, 35, 23, 56, 65, 40, 42, 61], [57, 65, 40, 54, 64, 66, 33, 5, 35, 23, 56, 65, 62], [4, 18, 11, 41, 47, 37, 16, 0], [60, 52, 26, 24, 45, 47, 37, 11, 13, 48, 24, 45, 28, 50, 34, 52, 63, 31, 29, 3, 25, 19, 29, 3, 1, 0], [57, 65, 62], [12, 5, 35, 23, 56, 65, 62], [58, 37, 11, 44, 45, 47, 59], [8, 22, 17, 19, 29, 3, 22, 44, 45, 28, 50, 34, 36, 38, 62], [14, 7, 10], [57, 65, 40, 42, 53, 64, 21, 23, 56, 65, 40, 54, 26, 49, 50, 34, 52, 26, 49, 50, 34, 52, 26, 49, 50, 34, 61], [57, 65, 62], [60, 32, 59], [8, 22, 17, 27, 48, 24, 45, 28, 50, 34, 36, 54, 26, 24, 45, 28, 50, 34, 36, 38, 62], [9, 39, 59], [4, 0], [4, 18, 39, 46, 28, 50, 34, 36, 38, 62], [12, 3, 22, 13, 48, 49, 50, 34, 61], [8, 22, 44, 45, 47, 37, 16, 2], [60, 52, 63, 31, 29, 3, 1, 0], [8, 1, 2], [12, 3, 22, 17, 27, 48, 49, 50, 34, 36, 38, 62], [57, 65, 62], [14, 35, 23, 56, 65, 40, 55, 56, 65, 40, 54, 26, 24, 45, 28, 50, 34, 52, 63, 31, 29, 3, 1, 2], [14, 7, 10], [60, 36, 54, 63, 31, 29, 3, 6], [14, 7, 10], [14, 35, 23, 56, 65, 62], [4, 0], [9, 39, 30, 51, 50, 34, 52, 63, 31, 29, 3, 22, 13, 48, 49, 50, 34, 36, 55, 56, 65, 62], [57, 65, 40, 42, 52, 63, 31, 29, 3, 6], [58, 30, 34, 36, 54, 64, 66, 33, 5, 35, 23, 56, 65, 40, 55, 56, 65, 40, 42, 53, 64, 21, 23, 56, 65, 40, 54, 63, 31, 29, 3, 22, 17, 19, 29, 3, 1, 2], [60, 32, 37, 16, 2], [60, 52, 63, 31, 29, 3, 1, 18, 39, 46, 43, 13, 48, 49, 50, 34, 52, 26, 49, 50, 34, 52, 63, 31, 29, 3, 1, 2], [8, 22, 13, 48, 49, 50, 34, 52, 26, 24, 45, 28, 50, 34, 36, 54, 64, 21, 23, 56, 65, 40, 54, 26, 24, 45, 28, 50, 34, 36, 54, 26, 49, 50, 34, 52, 63, 31, 29, 3, 25, 19, 29, 3, 6], [4, 0], [4, 18, 39, 30, 34, 61], [4, 0], [8, 22, 17, 19, 29, 3, 1, 2], [12, 3, 22, 13, 15, 66, 33, 5, 35, 23, 56, 65, 40, 54, 64, 66, 33, 5, 35, 23, 56, 65, 40, 54, 63, 31, 29, 3, 6], [60, 53, 64, 66, 33, 5, 35, 23, 56, 65, 62], [60, 32, 37, 11, 20, 6], [57, 65, 40, 42, 32, 59], [8, 22, 44, 45, 47, 59], [58, 30, 51, 50, 34, 36, 38, 62], [14, 35, 23, 56, 65, 40, 54, 64, 66, 33, 5, 35, 23, 56, 65, 40, 55, 56, 65, 62], [58, 30, 34, 36, 54, 26, 49, 50, 34, 61], [60, 53, 64, 21, 23, 56, 65, 62], [8, 22, 44, 45, 47, 59], [9, 16, 2], [58, 37, 11, 13, 15, 66, 33, 5, 35, 23, 56, 65, 62], [60, 32, 59], [9, 39, 30, 34, 36, 55, 56, 65, 62], [58, 30, 34, 61], [12, 3, 22, 44, 45, 28, 50, 34, 36, 55, 56, 65, 62], [9, 16, 0], [14, 35, 23, 56, 65, 62], [8, 22, 44, 45, 28, 50, 34, 36, 38, 62], [8, 22, 13, 48, 24, 45, 47, 59], [4, 18, 39, 46, 43, 13, 15, 21, 23, 56, 65, 40, 42, 52, 63, 31, 29, 3, 6], [58, 30, 51, 50, 34, 61], [57, 65, 62], [4, 0], [60, 52, 63, 31, 29, 3, 1, 0], [58, 37, 16, 0], [4, 18, 11, 41, 47, 30, 51, 50, 34, 52, 26, 24, 45, 28, 50, 34, 36, 55, 56, 65, 62], [58, 37, 11, 20, 1, 2], [9, 39, 30, 51, 50, 34, 36, 38, 62], [4, 18, 11, 41, 47, 30, 51, 50, 34, 36, 55, 56, 65, 62], [4, 0], [8, 22, 44, 45, 28, 50, 34, 61], [12, 3, 6], [14, 35, 23, 56, 65, 40, 42, 32, 37, 16, 2], [14, 35, 23, 56, 65, 62], [57, 65, 40, 55, 56, 65, 40, 55, 56, 65, 62], [57, 65, 40, 42, 53, 64, 21, 23, 56, 65, 40, 54, 63, 31, 29, 3, 1, 18, 39, 46, 43, 20, 1, 2], [57, 65, 40, 42, 52, 26, 49, 50, 34, 52, 63, 31, 29, 3, 1, 18, 39, 59], [4, 0], [4, 18, 39, 59], [4, 0], [12, 5, 35, 23, 56, 65, 62], [14, 7, 3, 6], [8, 22, 44, 45, 47, 37, 16, 0], [58, 46, 43, 13, 15, 21, 23, 56, 65, 62], [12, 3, 6], [9, 39, 30, 34, 61], [60, 32, 59], [8, 1, 0], [57, 65, 40, 42, 52, 63, 31, 29, 3, 25, 19, 29, 3, 6], [12, 3, 22, 13, 48, 49, 50, 34, 61], [9, 16, 0], [57, 65, 62], [57, 65, 40, 54, 26, 24, 45, 28, 50, 34, 36, 55, 56, 65, 62], [9, 39, 30, 34, 36, 38, 62], [57, 65, 62], [57, 65, 40, 54, 64, 21, 23, 56, 65, 40, 55, 56, 65, 62], [8, 1, 0], [8, 1, 0], [9, 11, 41, 47, 30, 34, 52, 26, 49, 50, 34, 36, 38, 62], [57, 65, 40, 55, 56, 65, 40, 54, 63, 31, 29, 3, 6], [14, 35, 23, 56, 65, 40, 42, 32, 46, 28, 50, 34, 36, 55, 56, 65, 62], [14, 35, 23, 56, 65, 40, 42, 52, 63, 31, 29, 3, 1, 2], [57, 65, 62], [14, 7, 10], [57, 65, 40, 54, 64, 66, 33, 5, 35, 23, 56, 65, 62], [8, 1, 0], [57, 65, 40, 54, 63, 31, 29, 3, 1, 18, 11, 13, 48, 49, 50, 34, 36, 38, 62], [12, 5, 35, 23, 56, 65, 40, 55, 56, 65, 62], [57, 65, 40, 55, 56, 65, 62], [57, 65, 40, 42, 32, 59], [60, 36, 38, 62], [57, 65, 40, 42, 32, 46, 43, 13, 48, 49, 50, 34, 52, 63, 31, 29, 3, 6], [9, 16, 2], [14, 7, 3, 6], [9, 11, 13, 15, 66, 33, 5, 35, 23, 56, 65, 40, 42, 61], [9, 11, 41, 43, 13, 15, 21, 23, 56, 65, 40, 54, 64, 66, 33, 5, 35, 23, 56, 65, 40, 42, 53, 64, 21, 23, 56, 65, 62], [9, 11, 20, 1, 2], [8, 1, 0], [57, 65, 62], [12, 3, 1, 2], [58, 30, 34, 52, 63, 31, 29, 3, 1, 0], [14, 35, 23, 56, 65, 62], [57, 65, 40, 54, 26, 49, 50, 34, 36, 54, 64, 66, 33, 5, 35, 23, 56, 65, 40, 42, 61], [57, 65, 62], [4, 0], [12, 3, 1, 2], [58, 30, 34, 52, 26, 24, 45, 47, 37, 11, 13, 15, 21, 23, 56, 65, 62], [8, 1, 0], [12, 5, 35, 23, 56, 65, 40, 42, 52, 63, 31, 29, 3, 6], [4, 0], [14, 35, 23, 56, 65, 40, 42, 53, 64, 66, 33, 5, 35, 23, 56, 65, 62], [57, 65, 62], [14, 35, 23, 56, 65, 62], [58, 46, 28, 50, 34, 36, 55, 56, 65, 40, 55, 56, 65, 62], [4, 18, 39, 46, 28, 50, 34, 36, 38, 62], [9, 11, 44, 45, 28, 50, 34, 36, 55, 56, 65, 40, 42, 52, 26, 24, 45, 47, 30, 51, 50, 34, 52, 26, 24, 45, 47, 30, 51, 50, 34, 52, 63, 31, 29, 3, 22, 44, 45, 47, 30, 34, 61], [12, 3, 25, 19, 29, 3, 6], [9, 39, 30, 34, 61], [60, 36, 55, 56, 65, 62], [4, 18, 11, 44, 45, 47, 59], [60, 32, 59], [58, 37, 11, 41, 28, 50, 34, 36, 54, 64, 66, 33, 5, 35, 23, 56, 65, 62], [4, 18, 11, 13, 15, 31, 29, 3, 6], [58, 30, 51, 50, 34, 52, 26, 24, 45, 47, 30, 34, 61], [12, 5, 35, 23, 56, 65, 62], [4, 18, 11, 44, 45, 28, 50, 34, 36, 54, 26, 24, 45, 28, 50, 34, 61], [8, 1, 0], [9, 11, 20, 1, 18, 39, 30, 34, 61], [60, 36, 38, 62], [58, 30, 51, 50, 34, 61], [9, 39, 59], [12, 3, 1, 18, 39, 46, 43, 20, 1, 0], [12, 3, 25, 19, 29, 3, 25, 27, 48, 24, 45, 28, 50, 34, 61], [58, 30, 51, 50, 34, 36, 54, 64, 21, 23, 56, 65, 40, 42, 61], [4, 0], [8, 22, 44, 45, 47, 59], [60, 52, 63, 31, 29, 3, 6], [57, 65, 62], [57, 65, 40, 54, 63, 31, 29, 3, 1, 18, 11, 44, 45, 47, 59], [58, 46, 28, 50, 34, 52, 26, 24, 45, 47, 59], [9, 39, 46, 43, 20, 6], [57, 65, 62], [57, 65, 40, 55, 56, 65, 40, 54, 63, 31, 29, 3, 1, 2], [58, 30, 51, 50, 34, 61], [57, 65, 62], [4, 18, 11, 41, 28, 50, 34, 61], [8, 22, 13, 48, 24, 45, 28, 50, 34, 61], [4, 0], [4, 18, 11, 13, 15, 21, 23, 56, 65, 62], [4, 18, 39, 59], [8, 1, 0], [8, 22, 17, 19, 29, 3, 1, 18, 39, 59], [8, 22, 44, 45, 28, 50, 34, 61], [9, 11, 20, 6], [58, 37, 11, 20, 1, 18, 39, 46, 28, 50, 34, 52, 63, 31, 29, 3, 6], [4, 0], [8, 22, 13, 48, 49, 50, 34, 36, 55, 56, 65, 62], [4, 18, 39, 46, 28, 50, 34, 36, 54, 64, 21, 23, 56, 65, 40, 42, 32, 46, 43, 20, 6], [57, 65, 62], [9, 16, 2], [12, 5, 35, 23, 56, 65, 40, 54, 63, 31, 29, 3, 22, 17, 27, 15, 21, 23, 56, 65, 40, 42, 53, 64, 21, 23, 56, 65, 62], [14, 7, 3, 25, 19, 29, 3, 1, 0], [4, 18, 11, 44, 45, 47, 59], [4, 0], [60, 52, 63, 31, 29, 3, 25, 27, 48, 24, 45, 28, 50, 34, 61], [14, 7, 10], [58, 46, 43, 13, 48, 49, 50, 34, 61], [14, 7, 3, 1, 2], [8, 1, 2], [4, 18, 39, 30, 34, 61], [57, 65, 40, 55, 56, 65, 62], [57, 65, 40, 54, 26, 49, 50, 34, 61], [57, 65, 40, 54, 64, 66, 33, 5, 35, 23, 56, 65, 40, 55, 56, 65, 40, 54, 26, 49, 50, 34, 36, 54, 64, 21, 23, 56, 65, 40, 54, 26, 49, 50, 34, 52, 63, 31, 29, 3, 22, 17, 19, 29, 3, 22, 17, 27, 48, 49, 50, 34, 61], [58, 46, 28, 50, 34, 36, 54, 26, 24, 45, 47, 30, 34, 36, 55, 56, 65, 40, 42, 52, 26, 49, 50, 34, 36, 38, 62], [57, 65, 40, 42, 53, 64, 66, 33, 5, 35, 23, 56, 65, 40, 42, 52, 26, 49, 50, 34, 36, 55, 56, 65, 40, 55, 56, 65, 62], [8, 22, 13, 48, 49, 50, 34, 52, 63, 31, 29, 3, 25, 19, 29, 3, 6], [8, 1, 18, 11, 13, 15, 66, 33, 5, 35, 23, 56, 65, 40, 42, 61], [58, 37, 11, 41, 28, 50, 34, 36, 54, 63, 31, 29, 3, 1, 18, 11, 44, 45, 28, 50, 34, 52, 26, 49, 50, 34, 61], [14, 35, 23, 56, 65, 40, 42, 61], [8, 1, 0], [58, 30, 51, 50, 34, 36, 55, 56, 65, 40, 54, 26, 49, 50, 34, 61], [57, 65, 62], [9, 11, 44, 45, 28, 50, 34, 36, 54, 63, 31, 29, 3, 6], [8, 1, 18, 11, 20, 6], [8, 1, 18, 39, 46, 28, 50, 34, 52, 26, 49, 50, 34, 61], [58, 37, 16, 0], [58, 37, 11, 20, 1, 2], [58, 30, 51, 50, 34, 52, 63, 31, 29, 3, 1, 0], [12, 3, 22, 17, 27, 48, 24, 45, 47, 59], [4, 0], [4, 18, 39, 46, 43, 13, 15, 31, 29, 3, 1, 2], [60, 36, 55, 56, 65, 62], [4, 18, 39, 30, 34, 52, 63, 31, 29, 3, 25, 19, 29, 3, 6], [57, 65, 62], [9, 11, 20, 1, 2], [57, 65, 40, 54, 63, 31, 29, 3, 6], [9, 11, 44, 45, 28, 50, 34, 36, 55, 56, 65, 40, 54, 26, 24, 45, 47, 59], [12, 3, 1, 0], [58, 37, 11, 20, 6], [8, 1, 2], [58, 30, 51, 50, 34, 36, 55, 56, 65, 62], [60, 36, 38, 62], [4, 18, 11, 20, 6], [12, 3, 1, 2], [57, 65, 40, 55, 56, 65, 40, 55, 56, 65, 40, 55, 56, 65, 62], [14, 35, 23, 56, 65, 62], [12, 3, 25, 27, 48, 49, 50, 34, 52, 63, 31, 29, 3, 22, 17, 27, 48, 24, 45, 47, 30, 51, 50, 34, 52, 26, 24, 45, 28, 50, 34, 61], [14, 7, 3, 6], [12, 3, 25, 19, 29, 3, 1, 0], [14, 7, 3, 1, 18, 11, 20, 6], [9, 39, 59], [9, 39, 59], [57, 65, 40, 54, 64, 21, 23, 56, 65, 40, 42, 32, 37, 11, 13, 48, 49, 50, 34, 61], [8, 22, 44, 45, 28, 50, 34, 36, 54, 63, 31, 29, 3, 6], [57, 65, 40, 55, 56, 65, 40, 55, 56, 65, 40, 55, 56, 65, 40, 55, 56, 65, 62], [14, 7, 10], [60, 36, 55, 56, 65, 62], [57, 65, 62], [57, 65, 62], [8, 1, 18, 39, 30, 34, 36, 38, 62], [9, 16, 2], [8, 1, 18, 39, 30, 51, 50, 34, 52, 63, 31, 29, 3, 25, 19, 29, 3, 22, 17, 19, 29, 3, 6], [60, 32, 37, 11, 44, 45, 28, 50, 34, 36, 38, 62], [58, 30, 34, 52, 63, 31, 29, 3, 22, 17, 19, 29, 3, 6], [57, 65, 40, 54, 26, 49, 50, 34, 52, 26, 24, 45, 28, 50, 34, 36, 54, 26, 49, 50, 34, 36, 38, 62], [57, 65, 40, 55, 56, 65, 40, 55, 56, 65, 62], [60, 53, 64, 66, 33, 5, 35, 23, 56, 65, 40, 55, 56, 65, 40, 54, 26, 49, 50, 34, 52, 26, 24, 45, 47, 30, 34, 61], [4, 18, 39, 30, 51, 50, 34, 52, 26, 24, 45, 47, 37, 16, 0], [12, 3, 6], [4, 18, 11, 13, 48, 24, 45, 47, 30, 34, 36, 54, 26, 24, 45, 28, 50, 34, 52, 63, 31, 29, 3, 1, 2], [57, 65, 40, 42, 61], [60, 36, 38, 62], [14, 35, 23, 56, 65, 40, 54, 26, 49, 50, 34, 52, 63, 31, 29, 3, 25, 27, 48, 24, 45, 47, 37, 11, 20, 1, 2], [57, 65, 40, 42, 53, 64, 21, 23, 56, 65, 62], [58, 30, 51, 50, 34, 36, 38, 62], [60, 32, 46, 28, 50, 34, 36, 38, 62], [60, 53, 64, 66, 33, 5, 35, 23, 56, 65, 62], [12, 5, 35, 23, 56, 65, 40, 42, 52, 26, 49, 50, 34, 61], [58, 46, 28, 50, 34, 52, 26, 49, 50, 34, 52, 26, 24, 45, 28, 50, 34, 52, 26, 24, 45, 47, 37, 11, 44, 45, 28, 50, 34, 52, 26, 24, 45, 28, 50, 34, 61], [4, 0], [9, 16, 2], [9, 11, 20, 6], [8, 22, 17, 27, 48, 49, 50, 34, 36, 38, 62], [9, 39, 59], [57, 65, 40, 42, 53, 64, 21, 23, 56, 65, 62], [4, 18, 11, 20, 6], [58, 30, 34, 52, 63, 31, 29, 3, 25, 27, 15, 31, 29, 3, 25, 27, 48, 49, 50, 34, 36, 54, 64, 21, 23, 56, 65, 62], [4, 18, 11, 20, 6], [9, 16, 2], [57, 65, 62], [60, 53, 64, 21, 23, 56, 65, 62], [12, 5, 35, 23, 56, 65, 62], [57, 65, 62], [60, 36, 55, 56, 65, 62], [60, 52, 63, 31, 29, 3, 6], [57, 65, 40, 54, 64, 66, 33, 5, 35, 23, 56, 65, 62], [57, 65, 62], [8, 1, 18, 39, 46, 43, 20, 6], [9, 11, 44, 45, 47, 37, 16, 0], [58, 30, 51, 50, 34, 52, 63, 31, 29, 3, 1, 18, 39, 46, 43, 13, 15, 66, 33, 5, 35, 23, 56, 65, 40, 42, 61], [9, 11, 41, 47, 37, 11, 41, 47, 37, 11, 13, 48, 49, 50, 34, 36, 38, 62], [58, 46, 43, 20, 6], [9, 11, 44, 45, 28, 50, 34, 52, 63, 31, 29, 3, 22, 13, 48, 24, 45, 28, 50, 34, 36, 55, 56, 65, 62], [14, 7, 3, 25, 19, 29, 3, 22, 44, 45, 28, 50, 34, 61], [12, 5, 35, 23, 56, 65, 62], [57, 65, 62], [8, 1, 0], [58, 30, 51, 50, 34, 36, 55, 56, 65, 40, 55, 56, 65, 40, 55, 56, 65, 62], [12, 5, 35, 23, 56, 65, 62], [58, 30, 51, 50, 34, 52, 26, 49, 50, 34, 52, 63, 31, 29, 3, 25, 19, 29, 3, 6], [8, 22, 13, 15, 66, 33, 5, 35, 23, 56, 65, 40, 55, 56, 65, 62], [60, 32, 37, 16, 2], [57, 65, 40, 54, 64, 21, 23, 56, 65, 62], [60, 32, 46, 28, 50, 34, 61], [57, 65, 62], [12, 3, 25, 19, 29, 3, 22, 44, 45, 47, 59], [4, 0], [14, 35, 23, 56, 65, 40, 54, 63, 31, 29, 3, 6], [14, 7, 10], [57, 65, 62], [8, 22, 44, 45, 47, 59], [57, 65, 62], [58, 46, 43, 13, 48, 24, 45, 28, 50, 34, 61], [14, 35, 23, 56, 65, 40, 55, 56, 65, 62], [9, 39, 30, 34, 61], [4, 18, 11, 20, 1, 2], [58, 30, 34, 36, 38, 62], [4, 0], [57, 65, 40, 54, 26, 24, 45, 47, 30, 51, 50, 34, 61], [58, 37, 11, 20, 1, 18, 11, 20, 6], [14, 35, 23, 56, 65, 40, 54, 26, 49, 50, 34, 61], [8, 22, 17, 27, 48, 49, 50, 34, 61], [14, 35, 23, 56, 65, 40, 42, 61], [14, 35, 23, 56, 65, 62], [12, 5, 35, 23, 56, 65, 62], [9, 16, 2], [12, 3, 6], [9, 11, 41, 43, 20, 1, 18, 39, 30, 51, 50, 34, 61], [12, 5, 35, 23, 56, 65, 62], [12, 3, 22, 17, 27, 48, 24, 45, 28, 50, 34, 61], [9, 16, 0], [8, 22, 13, 48, 49, 50, 34, 52, 26, 49, 50, 34, 61], [58, 46, 43, 20, 6], [9, 11, 13, 48, 49, 50, 34, 52, 63, 31, 29, 3, 6], [58, 46, 28, 50, 34, 61], [14, 7, 10], [57, 65, 40, 55, 56, 65, 40, 42, 52, 63, 31, 29, 3, 22, 44, 45, 47, 59], [57, 65, 62], [4, 18, 39, 30, 34, 61], [8, 22, 44, 45, 28, 50, 34, 36, 55, 56, 65, 62], [14, 35, 23, 56, 65, 40, 54, 64, 66, 33, 5, 35, 23, 56, 65, 40, 42, 53, 64, 66, 33, 5, 35, 23, 56, 65, 62], [9, 11, 13, 48, 49, 50, 34, 61], [60, 53, 64, 66, 33, 5, 35, 23, 56, 65, 40, 55, 56, 65, 62], [58, 30, 51, 50, 34, 52, 63, 31, 29, 3, 6], [4, 0], [60, 32, 59], [58, 30, 34, 61], [4, 18, 39, 46, 43, 20, 6], [14, 35, 23, 56, 65, 62], [58, 37, 11, 41, 47, 59], [4, 0], [9, 16, 2], [60, 36, 55, 56, 65, 62], [8, 22, 13, 15, 66, 33, 5, 35, 23, 56, 65, 40, 54, 63, 31, 29, 3, 22, 17, 27, 48, 24, 45, 28, 50, 34, 52, 63, 31, 29, 3, 1, 0], [14, 35, 23, 56, 65, 40, 54, 63, 31, 29, 3, 25, 27, 48, 24, 45, 28, 50, 34, 61], [57, 65, 40, 55, 56, 65, 40, 42, 61], [9, 39, 46, 28, 50, 34, 61], [57, 65, 62], [57, 65, 62], [14, 35, 23, 56, 65, 62], [4, 18, 39, 30, 34, 61], [58, 46, 28, 50, 34, 61], [9, 16, 2], [58, 30, 51, 50, 34, 61], [4, 0], [57, 65, 40, 54, 26, 24, 45, 28, 50, 34, 36, 54, 64, 21, 23, 56, 65, 62], [60, 52, 26, 24, 45, 47, 30, 51, 50, 34, 61], [58, 30, 34, 52, 26, 49, 50, 34, 36, 38, 62], [4, 0], [58, 37, 16, 0], [60, 36, 38, 62], [60, 32, 46, 43, 20, 1, 2], [8, 22, 44, 45, 47, 30, 51, 50, 34, 36, 38, 62], [60, 32, 46, 28, 50, 34, 52, 63, 31, 29, 3, 22, 13, 15, 66, 33, 5, 35, 23, 56, 65, 62], [12, 5, 35, 23, 56, 65, 62], [8, 1, 18, 11, 41, 47, 37, 16, 0], [14, 7, 3, 22, 17, 27, 48, 24, 45, 28, 50, 34, 36, 54, 63, 31, 29, 3, 1, 2], [12, 3, 1, 0], [57, 65, 62], [4, 18, 11, 44, 45, 47, 37, 11, 20, 1, 0], [58, 37, 16, 2], [57, 65, 40, 54, 63, 31, 29, 3, 6], [12, 5, 35, 23, 56, 65, 40, 55, 56, 65, 62], [4, 18, 39, 59], [58, 46, 28, 50, 34, 61], [8, 22, 13, 15, 66, 33, 5, 35, 23, 56, 65, 40, 54, 63, 31, 29, 3, 6], [57, 65, 62], [14, 7, 10], [60, 53, 64, 21, 23, 56, 65, 62], [4, 18, 11, 41, 28, 50, 34, 61], [60, 32, 46, 28, 50, 34, 52, 63, 31, 29, 3, 22, 13, 48, 24, 45, 47, 30, 34, 36, 55, 56, 65, 40, 55, 56, 65, 62]]
    # print("len(car_path_options_store): " + str(len(car_path_options_store)))   # stores 500 path options
    entry_lane_car_path_options_store = [[57, 65, 40, 54, 64, 21, 23, 56, 65, 40, 54, 26, 49, 50, 34, 61, 9999], [14, 7, 10, 9999], [9, 16, 2, 9999], [58, 30, 34, 36, 38, 62, 9999], [60, 53, 64, 21, 23, 56, 65, 62, 9999], [4, 18, 11, 41, 43, 20, 1, 0, 9999], [9, 11, 20, 6, 9999], [57, 65, 62, 9999], [9, 16, 2, 9999], [14, 7, 10, 9999], [4, 18, 39, 46, 28, 50, 34, 61, 9999], [60, 52, 63, 31, 29, 3, 25, 27, 15, 66, 33, 5, 35, 23, 56, 65, 40, 54, 26, 24, 45, 47, 59, 9999], [12, 3, 1, 18, 39, 59, 9999], [57, 65, 40, 54, 64, 66, 33, 5, 35, 23, 56, 65, 40, 42, 53, 64, 21, 23, 56, 65, 62, 9999], [14, 35, 23, 56, 65, 62, 9999], [57, 65, 40, 55, 56, 65, 40, 55, 56, 65, 40, 54, 64, 66, 33, 5, 35, 23, 56, 65, 62, 9999], [4, 0, 9999], [12, 3, 25, 27, 48, 49, 50, 34, 61, 9999], [14, 35, 23, 56, 65, 40, 42, 61, 9999], [8, 22, 13, 48, 49, 50, 34, 61, 9999], [9, 39, 59, 9999], [14, 35, 23, 56, 65, 62, 9999], [9, 11, 41, 47, 30, 34, 36, 38, 62, 9999], [8, 22, 44, 45, 47, 30, 51, 50, 34, 36, 38, 62, 9999], [9, 16, 2, 9999], [58, 46, 28, 50, 34, 36, 54, 64, 21, 23, 56, 65, 62, 9999], [14, 35, 23, 56, 65, 40, 55, 56, 65, 40, 54, 26, 24, 45, 47, 30, 51, 50, 34, 36, 54, 63, 31, 29, 3, 22, 13, 15, 66, 33, 5, 35, 23, 56, 65, 40, 55, 56, 65, 62, 9999], [58, 37, 11, 41, 43, 20, 1, 0, 9999], [58, 37, 16, 2, 9999], [57, 65, 62, 9999], [12, 5, 35, 23, 56, 65, 40, 42, 52, 26, 49, 50, 34, 61, 9999], [58, 37, 16, 0, 9999], [4, 18, 11, 44, 45, 28, 50, 34, 36, 54, 64, 66, 33, 5, 35, 23, 56, 65, 40, 54, 63, 31, 29, 3, 1, 18, 39, 30, 51, 50, 34, 36, 38, 62, 9999], [14, 7, 10, 9999], [4, 0, 9999], [14, 35, 23, 56, 65, 62, 9999], [8, 22, 13, 15, 66, 33, 5, 35, 23, 56, 65, 40, 55, 56, 65, 62, 9999], [12, 3, 22, 44, 45, 28, 50, 34, 36, 38, 62, 9999], [8, 1, 18, 39, 30, 34, 52, 63, 31, 29, 3, 1, 2, 9999], [4, 0, 9999], [60, 52, 63, 31, 29, 3, 22, 44, 45, 28, 50, 34, 52, 26, 24, 45, 47, 59, 9999], [60, 52, 26, 49, 50, 34, 61, 9999], [9, 39, 46, 43, 13, 48, 24, 45, 47, 30, 51, 50, 34, 61, 9999], [58, 37, 16, 0, 9999], [58, 46, 43, 13, 15, 21, 23, 56, 65, 40, 55, 56, 65, 62, 9999], [57, 65, 40, 55, 56, 65, 62, 9999], [14, 35, 23, 56, 65, 62, 9999], [8, 1, 0, 9999], [9, 39, 30, 51, 50, 34, 52, 63, 31, 29, 3, 6, 9999], [12, 3, 1, 0, 9999], [60, 53, 64, 21, 23, 56, 65, 62, 9999], [14, 7, 10, 9999], [9, 11, 13, 15, 66, 33, 5, 35, 23, 56, 65, 40, 42, 53, 64, 21, 23, 56, 65, 40, 54, 26, 24, 45, 47, 59, 9999], [12, 5, 35, 23, 56, 65, 40, 55, 56, 65, 40, 42, 53, 64, 66, 33, 5, 35, 23, 56, 65, 62, 9999], [58, 37, 16, 0, 9999], [14, 7, 3, 25, 19, 29, 3, 1, 0, 9999], [12, 3, 6, 9999], [9, 11, 41, 43, 20, 6, 9999], [9, 39, 46, 43, 20, 1, 0, 9999], [60, 36, 55, 56, 65, 62, 9999], [57, 65, 62, 9999], [60, 32, 46, 43, 13, 15, 21, 23, 56, 65, 40, 42, 32, 59, 9999], [4, 0, 9999], [60, 52, 63, 31, 29, 3, 6, 9999], [9, 11, 44, 45, 47, 30, 51, 50, 34, 36, 38, 62, 9999], [9, 39, 46, 28, 50, 34, 52, 26, 24, 45, 28, 50, 34, 36, 54, 26, 24, 45, 28, 50, 34, 61, 9999], [8, 1, 2, 9999], [12, 3, 22, 44, 45, 47, 59, 9999], [8, 1, 0, 9999], [8, 22, 17, 27, 48, 49, 50, 34, 52, 63, 31, 29, 3, 6, 9999], [9, 16, 0, 9999], [57, 65, 40, 55, 56, 65, 62, 9999], [12, 3, 1, 0, 9999], [14, 35, 23, 56, 65, 62, 9999], [9, 16, 2, 9999], [12, 3, 25, 19, 29, 3, 25, 19, 29, 3, 25, 19, 29, 3, 1, 18, 39, 46, 28, 50, 34, 36, 54, 64, 66, 33, 5, 35, 23, 56, 65, 62, 9999], [60, 53, 64, 21, 23, 56, 65, 40, 55, 56, 65, 40, 42, 53, 64, 21, 23, 56, 65, 40, 54, 26, 49, 50, 34, 61, 9999], [14, 7, 3, 1, 2, 9999], [58, 30, 34, 52, 63, 31, 29, 3, 1, 0, 9999], [12, 3, 6, 9999], [60, 32, 46, 28, 50, 34, 36, 55, 56, 65, 62, 9999], [57, 65, 62, 9999], [14, 35, 23, 56, 65, 40, 42, 32, 37, 11, 20, 6, 9999], [14, 35, 23, 56, 65, 40, 54, 26, 49, 50, 34, 52, 63, 31, 29, 3, 22, 44, 45, 47, 30, 34, 52, 26, 49, 50, 34, 36, 55, 56, 65, 40, 42, 61, 9999], [4, 0, 9999], [14, 35, 23, 56, 65, 62, 9999], [58, 46, 43, 13, 48, 24, 45, 47, 30, 34, 52, 63, 31, 29, 3, 1, 18, 11, 41, 47, 30, 51, 50, 34, 36, 55, 56, 65, 40, 54, 26, 24, 45, 28, 50, 34, 52, 63, 31, 29, 3, 25, 27, 15, 66, 33, 5, 35, 23, 56, 65, 62, 9999], [12, 3, 22, 17, 27, 15, 21, 23, 56, 65, 40, 55, 56, 65, 40, 54, 63, 31, 29, 3, 22, 44, 45, 28, 50, 34, 36, 55, 56, 65, 40, 54, 26, 24, 45, 28, 50, 34, 52, 26, 24, 45, 28, 50, 34, 36, 55, 56, 65, 62, 9999], [58, 30, 34, 52, 26, 49, 50, 34, 52, 63, 31, 29, 3, 1, 0, 9999], [14, 7, 3, 25, 27, 48, 24, 45, 47, 37, 16, 0, 9999], [8, 22, 13, 15, 31, 29, 3, 6, 9999], [60, 52, 63, 31, 29, 3, 22, 17, 27, 15, 21, 23, 56, 65, 40, 54, 26, 24, 45, 28, 50, 34, 52, 26, 24, 45, 28, 50, 34, 61, 9999], [4, 0, 9999], [14, 7, 3, 6, 9999], [58, 30, 51, 50, 34, 52, 26, 24, 45, 47, 37, 16, 0, 9999], [8, 22, 17, 19, 29, 3, 1, 0, 9999], [14, 7, 3, 25, 27, 15, 21, 23, 56, 65, 62, 9999], [60, 32, 37, 11, 41, 47, 30, 34, 52, 63, 31, 29, 3, 25, 19, 29, 3, 6, 9999], [4, 18, 11, 13, 48, 49, 50, 34, 36, 38, 62, 9999], [14, 35, 23, 56, 65, 62, 9999], [9, 16, 2, 9999], [12, 5, 35, 23, 56, 65, 40, 54, 64, 21, 23, 56, 65, 40, 54, 63, 31, 29, 3, 1, 0, 9999], [4, 18, 39, 46, 43, 13, 15, 31, 29, 3, 6, 9999], [9, 39, 59, 9999], [8, 22, 44, 45, 47, 59, 9999], [12, 5, 35, 23, 56, 65, 62, 9999], [58, 46, 28, 50, 34, 36, 38, 62, 9999], [14, 7, 3, 25, 27, 15, 31, 29, 3, 22, 44, 45, 28, 50, 34, 36, 55, 56, 65, 40, 54, 63, 31, 29, 3, 6, 9999], [60, 53, 64, 66, 33, 5, 35, 23, 56, 65, 62, 9999], [4, 0, 9999], [9, 11, 20, 6, 9999], [57, 65, 62, 9999], [57, 65, 40, 55, 56, 65, 40, 55, 56, 65, 62, 9999], [57, 65, 62, 9999], [57, 65, 62, 9999], [8, 1, 0, 9999], [8, 22, 17, 27, 15, 66, 33, 5, 35, 23, 56, 65, 40, 55, 56, 65, 62, 9999], [4, 18, 11, 13, 48, 49, 50, 34, 61, 9999], [60, 36, 55, 56, 65, 62, 9999], [57, 65, 40, 54, 26, 24, 45, 47, 59, 9999], [14, 35, 23, 56, 65, 40, 42, 61, 9999], [57, 65, 40, 54, 64, 66, 33, 5, 35, 23, 56, 65, 62, 9999], [4, 18, 11, 41, 47, 37, 16, 0, 9999], [60, 52, 26, 24, 45, 47, 37, 11, 13, 48, 24, 45, 28, 50, 34, 52, 63, 31, 29, 3, 25, 19, 29, 3, 1, 0, 9999], [57, 65, 62, 9999], [12, 5, 35, 23, 56, 65, 62, 9999], [58, 37, 11, 44, 45, 47, 59, 9999], [8, 22, 17, 19, 29, 3, 22, 44, 45, 28, 50, 34, 36, 38, 62, 9999], [14, 7, 10, 9999], [57, 65, 40, 42, 53, 64, 21, 23, 56, 65, 40, 54, 26, 49, 50, 34, 52, 26, 49, 50, 34, 52, 26, 49, 50, 34, 61, 9999], [57, 65, 62, 9999], [60, 32, 59, 9999], [8, 22, 17, 27, 48, 24, 45, 28, 50, 34, 36, 54, 26, 24, 45, 28, 50, 34, 36, 38, 62, 9999], [9, 39, 59, 9999], [4, 0, 9999], [4, 18, 39, 46, 28, 50, 34, 36, 38, 62, 9999], [12, 3, 22, 13, 48, 49, 50, 34, 61, 9999], [8, 22, 44, 45, 47, 37, 16, 2, 9999], [60, 52, 63, 31, 29, 3, 1, 0, 9999], [8, 1, 2, 9999], [12, 3, 22, 17, 27, 48, 49, 50, 34, 36, 38, 62, 9999], [57, 65, 62, 9999], [14, 35, 23, 56, 65, 40, 55, 56, 65, 40, 54, 26, 24, 45, 28, 50, 34, 52, 63, 31, 29, 3, 1, 2, 9999], [14, 7, 10, 9999], [60, 36, 54, 63, 31, 29, 3, 6, 9999], [14, 7, 10, 9999], [14, 35, 23, 56, 65, 62, 9999], [4, 0, 9999], [9, 39, 30, 51, 50, 34, 52, 63, 31, 29, 3, 22, 13, 48, 49, 50, 34, 36, 55, 56, 65, 62, 9999], [57, 65, 40, 42, 52, 63, 31, 29, 3, 6, 9999], [58, 30, 34, 36, 54, 64, 66, 33, 5, 35, 23, 56, 65, 40, 55, 56, 65, 40, 42, 53, 64, 21, 23, 56, 65, 40, 54, 63, 31, 29, 3, 22, 17, 19, 29, 3, 1, 2, 9999], [60, 32, 37, 16, 2, 9999], [60, 52, 63, 31, 29, 3, 1, 18, 39, 46, 43, 13, 48, 49, 50, 34, 52, 26, 49, 50, 34, 52, 63, 31, 29, 3, 1, 2, 9999], [8, 22, 13, 48, 49, 50, 34, 52, 26, 24, 45, 28, 50, 34, 36, 54, 64, 21, 23, 56, 65, 40, 54, 26, 24, 45, 28, 50, 34, 36, 54, 26, 49, 50, 34, 52, 63, 31, 29, 3, 25, 19, 29, 3, 6, 9999], [4, 0, 9999], [4, 18, 39, 30, 34, 61, 9999], [4, 0, 9999], [8, 22, 17, 19, 29, 3, 1, 2, 9999], [12, 3, 22, 13, 15, 66, 33, 5, 35, 23, 56, 65, 40, 54, 64, 66, 33, 5, 35, 23, 56, 65, 40, 54, 63, 31, 29, 3, 6, 9999], [60, 53, 64, 66, 33, 5, 35, 23, 56, 65, 62, 9999], [60, 32, 37, 11, 20, 6, 9999], [57, 65, 40, 42, 32, 59, 9999], [8, 22, 44, 45, 47, 59, 9999], [58, 30, 51, 50, 34, 36, 38, 62, 9999], [14, 35, 23, 56, 65, 40, 54, 64, 66, 33, 5, 35, 23, 56, 65, 40, 55, 56, 65, 62, 9999], [58, 30, 34, 36, 54, 26, 49, 50, 34, 61, 9999], [60, 53, 64, 21, 23, 56, 65, 62, 9999], [8, 22, 44, 45, 47, 59, 9999], [9, 16, 2, 9999], [58, 37, 11, 13, 15, 66, 33, 5, 35, 23, 56, 65, 62, 9999], [60, 32, 59, 9999], [9, 39, 30, 34, 36, 55, 56, 65, 62, 9999], [58, 30, 34, 61, 9999], [12, 3, 22, 44, 45, 28, 50, 34, 36, 55, 56, 65, 62, 9999], [9, 16, 0, 9999], [14, 35, 23, 56, 65, 62, 9999], [8, 22, 44, 45, 28, 50, 34, 36, 38, 62, 9999], [8, 22, 13, 48, 24, 45, 47, 59, 9999], [4, 18, 39, 46, 43, 13, 15, 21, 23, 56, 65, 40, 42, 52, 63, 31, 29, 3, 6, 9999], [58, 30, 51, 50, 34, 61, 9999], [57, 65, 62, 9999], [4, 0, 9999], [60, 52, 63, 31, 29, 3, 1, 0, 9999], [58, 37, 16, 0, 9999], [4, 18, 11, 41, 47, 30, 51, 50, 34, 52, 26, 24, 45, 28, 50, 34, 36, 55, 56, 65, 62, 9999], [58, 37, 11, 20, 1, 2, 9999], [9, 39, 30, 51, 50, 34, 36, 38, 62, 9999], [4, 18, 11, 41, 47, 30, 51, 50, 34, 36, 55, 56, 65, 62, 9999], [4, 0, 9999], [8, 22, 44, 45, 28, 50, 34, 61, 9999], [12, 3, 6, 9999], [14, 35, 23, 56, 65, 40, 42, 32, 37, 16, 2, 9999], [14, 35, 23, 56, 65, 62, 9999], [57, 65, 40, 55, 56, 65, 40, 55, 56, 65, 62, 9999], [57, 65, 40, 42, 53, 64, 21, 23, 56, 65, 40, 54, 63, 31, 29, 3, 1, 18, 39, 46, 43, 20, 1, 2, 9999], [57, 65, 40, 42, 52, 26, 49, 50, 34, 52, 63, 31, 29, 3, 1, 18, 39, 59, 9999], [4, 0, 9999], [4, 18, 39, 59, 9999], [4, 0, 9999], [12, 5, 35, 23, 56, 65, 62, 9999], [14, 7, 3, 6, 9999], [8, 22, 44, 45, 47, 37, 16, 0, 9999], [58, 46, 43, 13, 15, 21, 23, 56, 65, 62, 9999], [12, 3, 6, 9999], [9, 39, 30, 34, 61, 9999], [60, 32, 59, 9999], [8, 1, 0, 9999], [57, 65, 40, 42, 52, 63, 31, 29, 3, 25, 19, 29, 3, 6, 9999], [12, 3, 22, 13, 48, 49, 50, 34, 61, 9999], [9, 16, 0, 9999], [57, 65, 62, 9999], [57, 65, 40, 54, 26, 24, 45, 28, 50, 34, 36, 55, 56, 65, 62, 9999], [9, 39, 30, 34, 36, 38, 62, 9999], [57, 65, 62, 9999], [57, 65, 40, 54, 64, 21, 23, 56, 65, 40, 55, 56, 65, 62, 9999], [8, 1, 0, 9999], [8, 1, 0, 9999], [9, 11, 41, 47, 30, 34, 52, 26, 49, 50, 34, 36, 38, 62, 9999], [57, 65, 40, 55, 56, 65, 40, 54, 63, 31, 29, 3, 6, 9999], [14, 35, 23, 56, 65, 40, 42, 32, 46, 28, 50, 34, 36, 55, 56, 65, 62, 9999], [14, 35, 23, 56, 65, 40, 42, 52, 63, 31, 29, 3, 1, 2, 9999], [57, 65, 62, 9999], [14, 7, 10, 9999], [57, 65, 40, 54, 64, 66, 33, 5, 35, 23, 56, 65, 62, 9999], [8, 1, 0, 9999], [57, 65, 40, 54, 63, 31, 29, 3, 1, 18, 11, 13, 48, 49, 50, 34, 36, 38, 62, 9999], [12, 5, 35, 23, 56, 65, 40, 55, 56, 65, 62, 9999], [57, 65, 40, 55, 56, 65, 62, 9999], [57, 65, 40, 42, 32, 59, 9999], [60, 36, 38, 62, 9999], [57, 65, 40, 42, 32, 46, 43, 13, 48, 49, 50, 34, 52, 63, 31, 29, 3, 6, 9999], [9, 16, 2, 9999], [14, 7, 3, 6, 9999], [9, 11, 13, 15, 66, 33, 5, 35, 23, 56, 65, 40, 42, 61, 9999], [9, 11, 41, 43, 13, 15, 21, 23, 56, 65, 40, 54, 64, 66, 33, 5, 35, 23, 56, 65, 40, 42, 53, 64, 21, 23, 56, 65, 62, 9999], [9, 11, 20, 1, 2, 9999], [8, 1, 0, 9999], [57, 65, 62, 9999], [12, 3, 1, 2, 9999], [58, 30, 34, 52, 63, 31, 29, 3, 1, 0, 9999], [14, 35, 23, 56, 65, 62, 9999], [57, 65, 40, 54, 26, 49, 50, 34, 36, 54, 64, 66, 33, 5, 35, 23, 56, 65, 40, 42, 61, 9999], [57, 65, 62, 9999], [4, 0, 9999], [12, 3, 1, 2, 9999], [58, 30, 34, 52, 26, 24, 45, 47, 37, 11, 13, 15, 21, 23, 56, 65, 62, 9999], [8, 1, 0, 9999], [12, 5, 35, 23, 56, 65, 40, 42, 52, 63, 31, 29, 3, 6, 9999], [4, 0, 9999], [14, 35, 23, 56, 65, 40, 42, 53, 64, 66, 33, 5, 35, 23, 56, 65, 62, 9999], [57, 65, 62, 9999], [14, 35, 23, 56, 65, 62, 9999], [58, 46, 28, 50, 34, 36, 55, 56, 65, 40, 55, 56, 65, 62, 9999], [4, 18, 39, 46, 28, 50, 34, 36, 38, 62, 9999], [9, 11, 44, 45, 28, 50, 34, 36, 55, 56, 65, 40, 42, 52, 26, 24, 45, 47, 30, 51, 50, 34, 52, 26, 24, 45, 47, 30, 51, 50, 34, 52, 63, 31, 29, 3, 22, 44, 45, 47, 30, 34, 61, 9999], [12, 3, 25, 19, 29, 3, 6, 9999], [9, 39, 30, 34, 61, 9999], [60, 36, 55, 56, 65, 62, 9999], [4, 18, 11, 44, 45, 47, 59, 9999], [60, 32, 59, 9999], [58, 37, 11, 41, 28, 50, 34, 36, 54, 64, 66, 33, 5, 35, 23, 56, 65, 62, 9999], [4, 18, 11, 13, 15, 31, 29, 3, 6, 9999], [58, 30, 51, 50, 34, 52, 26, 24, 45, 47, 30, 34, 61, 9999], [12, 5, 35, 23, 56, 65, 62, 9999], [4, 18, 11, 44, 45, 28, 50, 34, 36, 54, 26, 24, 45, 28, 50, 34, 61, 9999], [8, 1, 0, 9999], [9, 11, 20, 1, 18, 39, 30, 34, 61, 9999], [60, 36, 38, 62, 9999], [58, 30, 51, 50, 34, 61, 9999], [9, 39, 59, 9999], [12, 3, 1, 18, 39, 46, 43, 20, 1, 0, 9999], [12, 3, 25, 19, 29, 3, 25, 27, 48, 24, 45, 28, 50, 34, 61, 9999], [58, 30, 51, 50, 34, 36, 54, 64, 21, 23, 56, 65, 40, 42, 61, 9999], [4, 0, 9999], [8, 22, 44, 45, 47, 59, 9999], [60, 52, 63, 31, 29, 3, 6, 9999], [57, 65, 62, 9999], [57, 65, 40, 54, 63, 31, 29, 3, 1, 18, 11, 44, 45, 47, 59, 9999], [58, 46, 28, 50, 34, 52, 26, 24, 45, 47, 59, 9999], [9, 39, 46, 43, 20, 6, 9999], [57, 65, 62, 9999], [57, 65, 40, 55, 56, 65, 40, 54, 63, 31, 29, 3, 1, 2, 9999], [58, 30, 51, 50, 34, 61, 9999], [57, 65, 62, 9999], [4, 18, 11, 41, 28, 50, 34, 61, 9999], [8, 22, 13, 48, 24, 45, 28, 50, 34, 61, 9999], [4, 0, 9999], [4, 18, 11, 13, 15, 21, 23, 56, 65, 62, 9999], [4, 18, 39, 59, 9999], [8, 1, 0, 9999], [8, 22, 17, 19, 29, 3, 1, 18, 39, 59, 9999], [8, 22, 44, 45, 28, 50, 34, 61, 9999], [9, 11, 20, 6, 9999], [58, 37, 11, 20, 1, 18, 39, 46, 28, 50, 34, 52, 63, 31, 29, 3, 6, 9999], [4, 0, 9999], [8, 22, 13, 48, 49, 50, 34, 36, 55, 56, 65, 62, 9999], [4, 18, 39, 46, 28, 50, 34, 36, 54, 64, 21, 23, 56, 65, 40, 42, 32, 46, 43, 20, 6, 9999], [57, 65, 62, 9999], [9, 16, 2, 9999], [12, 5, 35, 23, 56, 65, 40, 54, 63, 31, 29, 3, 22, 17, 27, 15, 21, 23, 56, 65, 40, 42, 53, 64, 21, 23, 56, 65, 62, 9999], [14, 7, 3, 25, 19, 29, 3, 1, 0, 9999], [4, 18, 11, 44, 45, 47, 59, 9999], [4, 0, 9999], [60, 52, 63, 31, 29, 3, 25, 27, 48, 24, 45, 28, 50, 34, 61, 9999], [14, 7, 10, 9999], [58, 46, 43, 13, 48, 49, 50, 34, 61, 9999], [14, 7, 3, 1, 2, 9999], [8, 1, 2, 9999], [4, 18, 39, 30, 34, 61, 9999], [57, 65, 40, 55, 56, 65, 62, 9999], [57, 65, 40, 54, 26, 49, 50, 34, 61, 9999], [57, 65, 40, 54, 64, 66, 33, 5, 35, 23, 56, 65, 40, 55, 56, 65, 40, 54, 26, 49, 50, 34, 36, 54, 64, 21, 23, 56, 65, 40, 54, 26, 49, 50, 34, 52, 63, 31, 29, 3, 22, 17, 19, 29, 3, 22, 17, 27, 48, 49, 50, 34, 61, 9999], [58, 46, 28, 50, 34, 36, 54, 26, 24, 45, 47, 30, 34, 36, 55, 56, 65, 40, 42, 52, 26, 49, 50, 34, 36, 38, 62, 9999], [57, 65, 40, 42, 53, 64, 66, 33, 5, 35, 23, 56, 65, 40, 42, 52, 26, 49, 50, 34, 36, 55, 56, 65, 40, 55, 56, 65, 62, 9999], [8, 22, 13, 48, 49, 50, 34, 52, 63, 31, 29, 3, 25, 19, 29, 3, 6, 9999], [8, 1, 18, 11, 13, 15, 66, 33, 5, 35, 23, 56, 65, 40, 42, 61, 9999], [58, 37, 11, 41, 28, 50, 34, 36, 54, 63, 31, 29, 3, 1, 18, 11, 44, 45, 28, 50, 34, 52, 26, 49, 50, 34, 61, 9999], [14, 35, 23, 56, 65, 40, 42, 61, 9999], [8, 1, 0, 9999], [58, 30, 51, 50, 34, 36, 55, 56, 65, 40, 54, 26, 49, 50, 34, 61, 9999], [57, 65, 62, 9999], [9, 11, 44, 45, 28, 50, 34, 36, 54, 63, 31, 29, 3, 6, 9999], [8, 1, 18, 11, 20, 6, 9999], [8, 1, 18, 39, 46, 28, 50, 34, 52, 26, 49, 50, 34, 61, 9999], [58, 37, 16, 0, 9999], [58, 37, 11, 20, 1, 2, 9999], [58, 30, 51, 50, 34, 52, 63, 31, 29, 3, 1, 0, 9999], [12, 3, 22, 17, 27, 48, 24, 45, 47, 59, 9999], [4, 0, 9999], [4, 18, 39, 46, 43, 13, 15, 31, 29, 3, 1, 2, 9999], [60, 36, 55, 56, 65, 62, 9999], [4, 18, 39, 30, 34, 52, 63, 31, 29, 3, 25, 19, 29, 3, 6, 9999], [57, 65, 62, 9999], [9, 11, 20, 1, 2, 9999], [57, 65, 40, 54, 63, 31, 29, 3, 6, 9999], [9, 11, 44, 45, 28, 50, 34, 36, 55, 56, 65, 40, 54, 26, 24, 45, 47, 59, 9999], [12, 3, 1, 0, 9999], [58, 37, 11, 20, 6, 9999], [8, 1, 2, 9999], [58, 30, 51, 50, 34, 36, 55, 56, 65, 62, 9999], [60, 36, 38, 62, 9999], [4, 18, 11, 20, 6, 9999], [12, 3, 1, 2, 9999], [57, 65, 40, 55, 56, 65, 40, 55, 56, 65, 40, 55, 56, 65, 62, 9999], [14, 35, 23, 56, 65, 62, 9999], [12, 3, 25, 27, 48, 49, 50, 34, 52, 63, 31, 29, 3, 22, 17, 27, 48, 24, 45, 47, 30, 51, 50, 34, 52, 26, 24, 45, 28, 50, 34, 61, 9999], [14, 7, 3, 6, 9999], [12, 3, 25, 19, 29, 3, 1, 0, 9999], [14, 7, 3, 1, 18, 11, 20, 6, 9999], [9, 39, 59, 9999], [9, 39, 59, 9999], [57, 65, 40, 54, 64, 21, 23, 56, 65, 40, 42, 32, 37, 11, 13, 48, 49, 50, 34, 61, 9999], [8, 22, 44, 45, 28, 50, 34, 36, 54, 63, 31, 29, 3, 6, 9999], [57, 65, 40, 55, 56, 65, 40, 55, 56, 65, 40, 55, 56, 65, 40, 55, 56, 65, 62, 9999], [14, 7, 10, 9999], [60, 36, 55, 56, 65, 62, 9999], [57, 65, 62, 9999], [57, 65, 62, 9999], [8, 1, 18, 39, 30, 34, 36, 38, 62, 9999], [9, 16, 2, 9999], [8, 1, 18, 39, 30, 51, 50, 34, 52, 63, 31, 29, 3, 25, 19, 29, 3, 22, 17, 19, 29, 3, 6, 9999], [60, 32, 37, 11, 44, 45, 28, 50, 34, 36, 38, 62, 9999], [58, 30, 34, 52, 63, 31, 29, 3, 22, 17, 19, 29, 3, 6, 9999], [57, 65, 40, 54, 26, 49, 50, 34, 52, 26, 24, 45, 28, 50, 34, 36, 54, 26, 49, 50, 34, 36, 38, 62, 9999], [57, 65, 40, 55, 56, 65, 40, 55, 56, 65, 62, 9999], [60, 53, 64, 66, 33, 5, 35, 23, 56, 65, 40, 55, 56, 65, 40, 54, 26, 49, 50, 34, 52, 26, 24, 45, 47, 30, 34, 61, 9999], [4, 18, 39, 30, 51, 50, 34, 52, 26, 24, 45, 47, 37, 16, 0, 9999], [12, 3, 6, 9999], [4, 18, 11, 13, 48, 24, 45, 47, 30, 34, 36, 54, 26, 24, 45, 28, 50, 34, 52, 63, 31, 29, 3, 1, 2, 9999], [57, 65, 40, 42, 61, 9999], [60, 36, 38, 62, 9999], [14, 35, 23, 56, 65, 40, 54, 26, 49, 50, 34, 52, 63, 31, 29, 3, 25, 27, 48, 24, 45, 47, 37, 11, 20, 1, 2, 9999], [57, 65, 40, 42, 53, 64, 21, 23, 56, 65, 62, 9999], [58, 30, 51, 50, 34, 36, 38, 62, 9999], [60, 32, 46, 28, 50, 34, 36, 38, 62, 9999], [60, 53, 64, 66, 33, 5, 35, 23, 56, 65, 62, 9999], [12, 5, 35, 23, 56, 65, 40, 42, 52, 26, 49, 50, 34, 61, 9999], [58, 46, 28, 50, 34, 52, 26, 49, 50, 34, 52, 26, 24, 45, 28, 50, 34, 52, 26, 24, 45, 47, 37, 11, 44, 45, 28, 50, 34, 52, 26, 24, 45, 28, 50, 34, 61, 9999], [4, 0, 9999], [9, 16, 2, 9999], [9, 11, 20, 6, 9999], [8, 22, 17, 27, 48, 49, 50, 34, 36, 38, 62, 9999], [9, 39, 59, 9999], [57, 65, 40, 42, 53, 64, 21, 23, 56, 65, 62, 9999], [4, 18, 11, 20, 6, 9999], [58, 30, 34, 52, 63, 31, 29, 3, 25, 27, 15, 31, 29, 3, 25, 27, 48, 49, 50, 34, 36, 54, 64, 21, 23, 56, 65, 62, 9999], [4, 18, 11, 20, 6, 9999], [9, 16, 2, 9999], [57, 65, 62, 9999], [60, 53, 64, 21, 23, 56, 65, 62, 9999], [12, 5, 35, 23, 56, 65, 62, 9999], [57, 65, 62, 9999], [60, 36, 55, 56, 65, 62, 9999], [60, 52, 63, 31, 29, 3, 6, 9999], [57, 65, 40, 54, 64, 66, 33, 5, 35, 23, 56, 65, 62, 9999], [57, 65, 62, 9999], [8, 1, 18, 39, 46, 43, 20, 6, 9999], [9, 11, 44, 45, 47, 37, 16, 0, 9999], [58, 30, 51, 50, 34, 52, 63, 31, 29, 3, 1, 18, 39, 46, 43, 13, 15, 66, 33, 5, 35, 23, 56, 65, 40, 42, 61, 9999], [9, 11, 41, 47, 37, 11, 41, 47, 37, 11, 13, 48, 49, 50, 34, 36, 38, 62, 9999], [58, 46, 43, 20, 6, 9999], [9, 11, 44, 45, 28, 50, 34, 52, 63, 31, 29, 3, 22, 13, 48, 24, 45, 28, 50, 34, 36, 55, 56, 65, 62, 9999], [14, 7, 3, 25, 19, 29, 3, 22, 44, 45, 28, 50, 34, 61, 9999], [12, 5, 35, 23, 56, 65, 62, 9999], [57, 65, 62, 9999], [8, 1, 0, 9999], [58, 30, 51, 50, 34, 36, 55, 56, 65, 40, 55, 56, 65, 40, 55, 56, 65, 62, 9999], [12, 5, 35, 23, 56, 65, 62, 9999], [58, 30, 51, 50, 34, 52, 26, 49, 50, 34, 52, 63, 31, 29, 3, 25, 19, 29, 3, 6, 9999], [8, 22, 13, 15, 66, 33, 5, 35, 23, 56, 65, 40, 55, 56, 65, 62, 9999], [60, 32, 37, 16, 2, 9999], [57, 65, 40, 54, 64, 21, 23, 56, 65, 62, 9999], [60, 32, 46, 28, 50, 34, 61, 9999], [57, 65, 62, 9999], [12, 3, 25, 19, 29, 3, 22, 44, 45, 47, 59, 9999], [4, 0, 9999], [14, 35, 23, 56, 65, 40, 54, 63, 31, 29, 3, 6, 9999], [14, 7, 10, 9999], [57, 65, 62, 9999], [8, 22, 44, 45, 47, 59, 9999], [57, 65, 62, 9999], [58, 46, 43, 13, 48, 24, 45, 28, 50, 34, 61, 9999], [14, 35, 23, 56, 65, 40, 55, 56, 65, 62, 9999], [9, 39, 30, 34, 61, 9999], [4, 18, 11, 20, 1, 2, 9999], [58, 30, 34, 36, 38, 62, 9999], [4, 0, 9999], [57, 65, 40, 54, 26, 24, 45, 47, 30, 51, 50, 34, 61, 9999], [58, 37, 11, 20, 1, 18, 11, 20, 6, 9999], [14, 35, 23, 56, 65, 40, 54, 26, 49, 50, 34, 61, 9999], [8, 22, 17, 27, 48, 49, 50, 34, 61, 9999], [14, 35, 23, 56, 65, 40, 42, 61, 9999], [14, 35, 23, 56, 65, 62, 9999], [12, 5, 35, 23, 56, 65, 62, 9999], [9, 16, 2, 9999], [12, 3, 6, 9999], [9, 11, 41, 43, 20, 1, 18, 39, 30, 51, 50, 34, 61, 9999], [12, 5, 35, 23, 56, 65, 62, 9999], [12, 3, 22, 17, 27, 48, 24, 45, 28, 50, 34, 61, 9999], [9, 16, 0, 9999], [8, 22, 13, 48, 49, 50, 34, 52, 26, 49, 50, 34, 61, 9999], [58, 46, 43, 20, 6, 9999], [9, 11, 13, 48, 49, 50, 34, 52, 63, 31, 29, 3, 6, 9999], [58, 46, 28, 50, 34, 61, 9999], [14, 7, 10, 9999], [57, 65, 40, 55, 56, 65, 40, 42, 52, 63, 31, 29, 3, 22, 44, 45, 47, 59, 9999], [57, 65, 62, 9999], [4, 18, 39, 30, 34, 61, 9999], [8, 22, 44, 45, 28, 50, 34, 36, 55, 56, 65, 62, 9999], [14, 35, 23, 56, 65, 40, 54, 64, 66, 33, 5, 35, 23, 56, 65, 40, 42, 53, 64, 66, 33, 5, 35, 23, 56, 65, 62, 9999], [9, 11, 13, 48, 49, 50, 34, 61, 9999], [60, 53, 64, 66, 33, 5, 35, 23, 56, 65, 40, 55, 56, 65, 62, 9999], [58, 30, 51, 50, 34, 52, 63, 31, 29, 3, 6, 9999], [4, 0, 9999], [60, 32, 59, 9999], [58, 30, 34, 61, 9999], [4, 18, 39, 46, 43, 20, 6, 9999], [14, 35, 23, 56, 65, 62, 9999], [58, 37, 11, 41, 47, 59, 9999], [4, 0, 9999], [9, 16, 2, 9999], [60, 36, 55, 56, 65, 62, 9999], [8, 22, 13, 15, 66, 33, 5, 35, 23, 56, 65, 40, 54, 63, 31, 29, 3, 22, 17, 27, 48, 24, 45, 28, 50, 34, 52, 63, 31, 29, 3, 1, 0, 9999], [14, 35, 23, 56, 65, 40, 54, 63, 31, 29, 3, 25, 27, 48, 24, 45, 28, 50, 34, 61, 9999], [57, 65, 40, 55, 56, 65, 40, 42, 61, 9999], [9, 39, 46, 28, 50, 34, 61, 9999], [57, 65, 62, 9999], [57, 65, 62, 9999], [14, 35, 23, 56, 65, 62, 9999], [4, 18, 39, 30, 34, 61, 9999], [58, 46, 28, 50, 34, 61, 9999], [9, 16, 2, 9999], [58, 30, 51, 50, 34, 61, 9999], [4, 0, 9999], [57, 65, 40, 54, 26, 24, 45, 28, 50, 34, 36, 54, 64, 21, 23, 56, 65, 62, 9999], [60, 52, 26, 24, 45, 47, 30, 51, 50, 34, 61, 9999], [58, 30, 34, 52, 26, 49, 50, 34, 36, 38, 62, 9999], [4, 0, 9999], [58, 37, 16, 0, 9999], [60, 36, 38, 62, 9999], [60, 32, 46, 43, 20, 1, 2, 9999], [8, 22, 44, 45, 47, 30, 51, 50, 34, 36, 38, 62, 9999], [60, 32, 46, 28, 50, 34, 52, 63, 31, 29, 3, 22, 13, 15, 66, 33, 5, 35, 23, 56, 65, 62, 9999], [12, 5, 35, 23, 56, 65, 62, 9999], [8, 1, 18, 11, 41, 47, 37, 16, 0, 9999], [14, 7, 3, 22, 17, 27, 48, 24, 45, 28, 50, 34, 36, 54, 63, 31, 29, 3, 1, 2, 9999], [12, 3, 1, 0, 9999], [57, 65, 62, 9999], [4, 18, 11, 44, 45, 47, 37, 11, 20, 1, 0, 9999], [58, 37, 16, 2, 9999], [57, 65, 40, 54, 63, 31, 29, 3, 6, 9999], [12, 5, 35, 23, 56, 65, 40, 55, 56, 65, 62, 9999], [4, 18, 39, 59, 9999], [58, 46, 28, 50, 34, 61, 9999], [8, 22, 13, 15, 66, 33, 5, 35, 23, 56, 65, 40, 54, 63, 31, 29, 3, 6, 9999], [57, 65, 62, 9999], [14, 7, 10, 9999], [60, 53, 64, 21, 23, 56, 65, 62, 9999], [4, 18, 11, 41, 28, 50, 34, 61, 9999], [60, 32, 46, 28, 50, 34, 52, 63, 31, 29, 3, 22, 13, 48, 24, 45, 47, 30, 34, 36, 55, 56, 65, 40, 55, 56, 65, 62, 9999]]
    return entry_lane_car_path_options_store
entry_lane_car_path_options_store = entry_lane_car_path_options_full()
for t in range(len(internal_lane_car_path_options_store)):
    internal_lane_car_path_options_store[t].append(9999)

cars = []
cars_in_system = []
cars_entered_system = []
cars_exited_system = []
num_cars = 500
num_initial_internal_cars = 75
for i in range(num_cars):
    cars.append(Car(100,100,i))
    cars[i].id = i
    car_angle_from_vert = 0
    cars[i].angle = car_angle_from_vert
    Car.car_on_angle(cars[i],cars[i].pos_x,cars[i].pos_y,car_width,car_length,car_angle_from_vert)
    # cars_in_system.append(i)
    # cars_entered_system.append(i)
    # cars[i].current_lane = 30
    # cars[i].current_lane = random.choice(entry_lanes)
    # cars[i].current_lane = 20
    if i < num_initial_internal_cars:
        cars[i].path = internal_lane_car_path_options_store[i]
    else:
        # car path taken from the
        cars[i].path = entry_lane_car_path_options_store[i]
    # cars[i].path = internal_lane_car_path_options_store[i]
    # cars[i].path = entry_lane_car_path_options_store[12]
    cars[i].path_step = 0
    cars[i].current_lane = cars[i].path[cars[i].path_step]
    # cars[i].next_lane = random.choice(lanes_test[cars[i].current_lane].next_lanes)
    cars[i].next_lane = cars[i].path[(cars[i].path_step + 1)]
    # if i == 76:
    #     cars[i].path = [60, 53, 64, 21, 23, 56, 65, 62, 9999]
    # cars[i].next_lane = 51

    # cars[i].next_lane = random.choice(lanes_test[cars[i].current_lane].next_lanes)
#
# print("juncs_test[2].light_lanes_at_junc: " + str(juncs_test[2].light_lanes_at_junc))
# input("winv")
### threads
class SetTimeLights(Thread):
    def run(self):
        while running_check == 1:
            # time.sleep(time_between_loops)
            time.sleep(1)
            for i in range(len(juncs_test)):
                if juncs_test[i].ready_for_green == 1: # junction ready for next green light
                    green_lane_index = juncs_test[i].same_light_lanes_link.index(juncs_test[i].green_lanes_at_junc)
                    # green_lane_index = juncs_test[i].light_lanes_at_junc.index(juncs_test[i].green_lanes_at_junc)
                    # green_lane_index = juncs_test[i].lanes_at_junc.index(juncs_test[i].green_lanes_at_junc)
                    next_green_lane_index = green_lane_index + 1
                    if next_green_lane_index == len(juncs_test[i].light_lanes_at_junc):
                        next_green_lane_index = 0
                    # print("time_between_loops: " + str(time_between_loops))
                    next_green_lane = juncs_test[i].same_light_lanes_link[next_green_lane_index]
                    if type(next_green_lane) == int:
                        # ie. only one lane from this junction
                        lane_selected = next_green_lane
                        lanes_test[lane_selected].green_light = 1 # acts as indicator that this lane now has a green light
                        lanes_test[lane_selected].time_green = 6

                    else:
                        # more than one lane from this junction, thus is a list
                        for p in next_green_lane:
                            lane_selected = p
                            lanes_test[lane_selected].green_light = 1 # acts as indicator that this lane now has a green light
                            lanes_test[lane_selected].time_green = 6
                    juncs_test[i].green_lanes_at_junc = next_green_lane
                    juncs_test[i].ready_for_green = 0 # green light lane allocaated to junction so turn off (set to 0) ready_for_green, this cycles thorugh the lights at a junction giving a set time to each

class Find_Lane_Localisation(Thread):
    def run(self):
        time.sleep(0.5)
        running_timer = 1
        sampling_counter = 0
        time_tracker = 0
        system_check_counter = 0
        cars[0].sampling_checker = 0
        while running_check == 1:
            if running_timer == 1:
                cars[0].sampling_checker = 1
                # time.sleep(time_interval)
                cars[0].sampling_checker = 0

                for i in cars_in_system: #(38,39):  #(cars_in_system): #(0,1) check this
                    if cars[i].id not in cars_in_system:
                        # print("car left system")
                        return
                    else:
                    # for i in cars_in_system:
                        # print("sampling")
                        # if cars[i].id == 10:
                        #     print("cars[10]_in_system_check: " + str(system_check_counter))
                        #     system_check_counter += 1
                        #     print("cars[10].pl1: " + str(cars[10].potential_lanes_1))
                        create_coord(cars,i,rad_gps)
                        # if cars[i].id == 10:
                        #     print("cars[10].localised_stage1: " + str(cars[i].localised_stage))
                        if cars[i].localised_stage == 2: # car has been alledgedly localised, however, perform to check as may have moved to another lane, update the guessed lane
                            # check consists of checking car is in the guess lane, if not check car is in the next_lanes leading from the guessed lane, if not meeting either of these critieria car has been lost and need to restart the localisation process
                            cars[i].localised_stage = 2
                            cars[i].recent_coords = cars[i].coords
                            # check for potential lanes
                            # find_potential_lanes_1(cars,lanes,i)
                            find_potential_lane_1_angle_method(cars,lanes_test,i)
                            # if cars[i].id == 10:
                            #     print("cars[i].potential_lanes_1 ls2: " + str(cars[i].potential_lanes_1))
                            # check if g_lane is in potential_lanes
                            if len(cars[i].potential_lanes_1) == 0: # sampling has taken place when car in middle of junction so no results
                                cars[i].potential_lanes_1 = lanes_test[cars[i].g_lane].next_lanes
                                # need to add that potential_lanes_lines_1 will need to  populate with the all points going forward             # decided not necessary s BUT MAY NEED TO CHECK
                                cars[i].localised_stage = 3 # this means it has once been localised but lost in junc so potential_points won't work

                            elif cars[i].g_lane in cars[i].potential_lanes_1:
                                # car is ok and assumed to still be in g_lane
                                cars[i].localised_stage = 2
                                # print("car.g_lane same_lane: " + str(cars[i].g_lane))
                            elif len(cars[i].potential_lanes_1) > 0 and (cars[i].g_lane not in cars[i].potential_lanes_1):
                                # car has potenitally moved into a new lane
                                # add g_lane.next_lanes and g_lane.assoc_lanes to potential_lanes_1 and set car_localised_stage to 3
                                # check to see if any pl1 are in g_lane,next_lane
                                cars[i].localised_stage = 3
                                new_lane_temp = []
                                # if cars[i].id == 10:
                                #     print("u cars[i].potential_lanes_1: " + str(cars[i].potential_lanes_1))
                                #     print("u cars[i].g_lane: " + str(cars[i].g_lane))
                                #     print("u lanes_test[cars[i].g_lane].next_lanes: " + str(lanes_test[cars[i].g_lane].next_lanes))
                                for u in cars[i].potential_lanes_1: # check to see if car has moved in a next_lane
                                    if u in lanes_test[cars[i].g_lane].next_lanes:
                                        new_lane_temp.append(u)
                                for u in cars[i].potential_lanes_1: # check to see if car has moved into an associated lane
                                    if u in lanes_test[cars[i].g_lane].assoc_lanes:
                                        new_lane_temp.append(u)
                                if len(new_lane_temp) == 1: #only one lane option so must be g_lane
                                    # car has moved to next lane so and update its g_lane to the new next_lane
                                    cars[i].g_lane = new_lane_temp[0]
                                    cars[i].g_track_path.append(cars[i].g_lane)
                                    cars[i].localised_stage = 2
                                    cars[i].localised = 1
                                    # if cars[i].id == 0:
                                        # print("refound here 3")

                                if cars[i].localised_stage == 3:
                                # add g_lane.next_lanes and g_lane.assoc_lanes to potential_lanes_1 and set car_localised_stage to 3
                                    # potential_lanes_temp = []
                                    potential_lane_temp = lanes_test[cars[i].g_lane].next_lanes + lanes_test[cars[i].g_lane].assoc_lanes
                                    # cars[i].potential_lanes_1 = lanes_test[cars[i].g_lane].next_lanes
                                    cars[i].potential_lanes_1 = potential_lane_temp
                                    cars[i].localised_stage = 3 # this means it has once been localised but lost in junc won't work, wait for next sample
                                    # del(cars[i].g_lane)
                                    # if cars[i].id == 0:
                                    #     print("lost here 1")
                            else:
                                # first assume lost
                                cars[i].localised_stage = 0 # car is lost, if finsihes section in this state the localisation process will restart
                                cars[i].localised = 0 # car not localised, has been unlocalised

                        else:
                            if cars[i].localised_stage == 0: # first notion of this car or moved lane before localising in previous lane ie. location is unknown
                                # print("car localising")
                                cars[i].orig_coords = cars[i].coords
                                # find_potential_lanes_1(cars,lanes,i)
                                find_potential_lane_1_angle_method(cars,lanes_test,i)
                                find_dist_to_lane_points_method_potential_lane_1(cars,lanes_test,i,rad_gps)
                                # if i == 10:
                                #     print("     here 11 cars[car_id].dist_lane_forward_points_1: " + str(cars[i].dist_lane_forward_points_1))
                                cars[i].localised_stage = 1 # original potential lanes and points stored#
                                if len(cars[i].potential_lanes_1) == 1: # ie. only one lane option,
                                    # we know the car must be in this lane]
                                    cars[i].g_lane = cars[i].potential_lanes_1[0] # the first and only entry of the pl1
                                    cars[i].g_track_path.append(cars[i].g_lane)
                                    cars[i].localised_stage = 2
                                    cars[i].localised = 1
                                # if cars[i].id == 10:
                                #     print("cars[i].potential_lanes_1 ls0: " + str(cars[i].potential_lanes_1))
                                #     print("cars[i].potential_lanes_lines_1 ls0: " + str(cars[i].potential_lanes_lines_1))
                                #     print("cars[i].dist_lane_forward_points_1 ls0: " + str(cars[i].dist_lane_forward_points_1))

                            elif cars[i].localised_stage == 3: # car has been locaised previously but was lost, as potential_lanes_1 was empty (or g_lane was not in pl1) but now is populated by g_lane.next_lanes
                                # potential_lanes_1 has previously been created from the g_lane.next_lanes want to check if there is one of the potential_lanes_2 is common with potential_lanes_1
                                # if cars[i].id == 10:
                                    # print("here 2")
                                find_potential_lane_2_angle_method(cars,lanes_test,i)
                                # if cars[i].id == 10:
                                #     print("here 1")
                                #     print("cars[i].potential_lanes_2: " + str(cars[i].potential_lanes_2))
                                #     print("cars[i].potential_lanes_lines_2: " + str(cars[i].potential_lanes_lines_2))
                                #     print("cars[i].potential_lanes_1: " + str(cars[i].potential_lanes_1))
                                #     print("cars[i].potential_lanes_lines_1: " + str(cars[i].potential_lanes_lines_1))
                                if len(cars[i].potential_lanes_2) == 0: #empty pl2, car still stuck in junc or another junc
                                    # keep in this sectoin for the next sample
                                    cars[i].localised_stage = 3

                                if len(cars[i].potential_lanes_2) != 0:
                                    lanes_common = []
                                    for check_lane in cars[i].potential_lanes_1:
                                        if check_lane in cars[i].potential_lanes_2:
                                            lanes_common.append(check_lane)
                                    if len(lanes_common) == 1:
                                        if (len(cars[i].potential_lanes_1) == 1) and (len(cars[i].potential_lanes_2) == 1):
                                            # we can confirm that the car must have moved into this lane
                                            cars[i].g_lane = lanes_common[0] # the first and only entry of the lanes_common list
                                            cars[i].g_track_path.append(cars[i].g_lane)
                                            cars[i].localised_stage = 2
                                            cars[i].localised = 1
                                    elif len(lanes_common) == 0:
                                        # car lost, need to start localisation process again ie. zero lanes_common
                                        cars[i].localised_stage = 0
                                        # here should update potential_lanes_1 and trigger find_dist_to_lane_points_method_potential_lane_1
                                        cars[i].potential_lanes_1 = cars[i].potential_lanes_2 # pl2 becomes pl1
                                        cars[i].potential_lanes_lines_1 = cars[i].potential_lanes_lines_2 # pl2 lines becomes pl1 lines
                                        find_dist_to_lane_points_method_potential_lane_1(cars,lanes_test,i,rad_gps)
                                        # if i == 10:
                                        #     print("     here 12 cars[car_id].dist_lane_forward_points_1: " + str(cars[i].dist_lane_forward_points_1))
                                        cars[i].localised_stage = 1
                                    elif len(lanes_common) > 1:
                                     # ie. more than 1 so can not decide so try again on next loop, ie. just pause for next sample                  #### THIS AREA MIGHT NEED ATTENTION
                                        cars[i].localised_stage = 3

                            elif  cars[i].localised_stage == 1: # original potential lanes and
                                find_potential_lane_2_angle_method(cars,lanes_test,i)
                                # if cars[i].id == 10:
                                #     print("here 2")
                                #     print("cars[i].potential_lanes_2: " + str(cars[i].potential_lanes_2))
                                #     print("cars[i].potential_lanes_lines_2: " + str(cars[i].potential_lanes_lines_2))
                                #     print("cars[i].potential_lanes_1: " + str(cars[i].potential_lanes_1))
                                #     print("cars[i].potential_lanes_lines_1: " + str(cars[i].potential_lanes_lines_1))
                                #     print("cars[i].dist")
                                # find lanes_common between pl1 and pl2
                                # find distance between forward points for lanes_common
                                # find distance chagne for common lanes and lane points between potential_lanes_1 and potential_lanes_lines_2
                                if len(cars[i].potential_lanes_2) != 0:
                                    # check if common lanes between potential_lanes_1 and potential_lanes_2
                                    lanes_common = []
                                    for check_lane in cars[i].potential_lanes_1:
                                        if check_lane in cars[i].potential_lanes_2:
                                            lanes_common.append(check_lane)
                                    cars[i].localisation_lanes_common = lanes_common
                                    # if cars[i].id == 10:
                                    #     print("cars[i].localisation_lanes_common: " + str(cars[i].localisation_lanes_common))
                                    if len(cars[i].localisation_lanes_common) > 1:
                                        # find the distances between car coords and the forward points in the common lanes compare these to the dist from 1. if closer to 1 point in a lane must be in that lane, if closer to a point in both lanes inconclusive and wait for next loop to find pl2
                                        # find index of common_lane in potential_lanes_2
                                        # extract the line and point_of_intersection for this lane
                                        # find the distance between point_of_intersection forward points for this lane
                                        # store these in the same method as dist_lane_forward_points_1, and call it dist_lane_forward_points_2
                                        # find index of common_lane in potential_lanes_2
                                        cars[i].dist_lane_forward_points_lanes_common = []
                                        find_dist_to_lane_points_method_lanes_common(cars,lanes_test,i,rad_gps)
                                        # if cars[i].id == 10:
                                        #     print("cars[i].dist_lane_forward_points_lanes_common: " + str(cars[i].dist_lane_forward_points_lanes_common))
                                            # input("press 14")
                                        # now compare dist_lane_forward_points_1 and dist_lane_forward_points_lanes_common
                                         # filter out lanes in dist_lane_forward_points_1 that are not in lanes_common, only interested in lanes_common
                                        lane_common_temp = []
                                        lane_point_index_common_temp = []
                                        cars[i].potential_lanes_3 = []
                                        for r in range(len(cars[i].dist_lane_forward_points_lanes_common)): # loop through the lanes_common
                                            lane_common_extract_lane = cars[i].dist_lane_forward_points_lanes_common[r][0]
                                            for t in range(len(cars[i].dist_lane_forward_points_1)): # loop through lanes
                                                extract_lane_t = cars[i].dist_lane_forward_points_1[t][0]
                                                for q in range(1,len(cars[i].dist_lane_forward_points_1[t])): # loop through the points associated with lane
                                                    # check if a lane and point are common to both
                                                    # extract_lane_t = cars[i].dist_lane_forward_points_1[t][q]
                                                    extract_point = cars[i].dist_lane_forward_points_1[t][q][0]
                                                    extract_dist = cars[i].dist_lane_forward_points_1[t][q][1]
                                                    old_dist = extract_dist

                                                    # extract_point and dists from cars[i].dist_lane_forward_points_lanes_common
                                                    for s in range(1,len(cars[i].dist_lane_forward_points_lanes_common[r])): # loop through the points associated with this common lane
                                                        lane_com_extract_point = cars[i].dist_lane_forward_points_lanes_common[r][s][0]
                                                        lane_com_extract_dist = cars[i].dist_lane_forward_points_lanes_common[r][s][1]
                                                        new_dist = lane_com_extract_dist

                                                        # print("extract_lane_t: " + str(extract_lane_t) + " extract_point: " + str(extract_point) + " extract_dist: " + str(extract_dist))
                                                        # print("lane_common_extract_lane: " + str(lane_common_extract_lane) + " lane_com_extract_point: " + str(lane_com_extract_point) + " lane_com_extract_dist: " + str(lane_com_extract_dist))
                                                        # input("please press enter 11...")

                                                        if (extract_lane_t == lane_common_extract_lane) and (extract_point == lane_com_extract_point):
                                                            # we know that there is a common lane forward point in the dist_lane_forward_points_1 and dist_lane_forward_points_lanes_common
                                                            # now check the distance change betweeen the points
                                                            # change_dist = abs(extract_dist - lane_com_extract_dist)
                                                            # how many closer is the new point than the old point
                                                            change_dist = old_dist - new_dist
                                                            # if cars[i].id == 10:
                                                            #     print("extract_lane_t: " + str(extract_lane_t))
                                                            #     print("extract_dist: " + str(extract_dist))
                                                            #     print("lane_com_extract_dist: " + str(lane_com_extract_dist))
                                                            #     print("change_dist: " + str(change_dist))
                                                            # input("please press enter 12...")
                                                            if change_dist > (2*rad_gps):
                                                                # highly liekly car is in the this lane
                                                                cars[i].potential_lanes_3.append(extract_lane_t)
                                                            # which ever lane has the highest frequency in high_chance_lane, set that lane to be car[i].g_lane   #####   THIS MIGHT NEED ATTENTION
                                        #find the most frequent lane number in cars[i].potential_lanes_3
                                        if len(cars[i].potential_lanes_3) > 0:
                                            # if cars[i].id == 10:
                                            #     print("cars[i].potential_lanes_3: " + str(cars[i].potential_lanes_3))
                                            # lane_freq = 0
                                            lanes_and_freq = []
                                            lanes_freq = []
                                            for lane_id in cars[i].potential_lanes_3:
                                                lane_freq = cars[i].potential_lanes_3.count(lane_id)
                                                lanes_freq.append(lane_freq)
                                                lanes_and_freq.append([lane_id,lane_freq])
                                            max_freq = max(lanes_freq)
                                            count_lanes_with_mode = lanes_freq.count(max_freq)
                                            #find lanes that have the freq = amx_freq
                                            lanes_with_max_freq = []
                                            for t in range(len(lanes_and_freq)):
                                                # count_lane_freq = lanes_and_freq[t][1]
                                                if lanes_and_freq[t][1] == max_freq:
                                                    lanes_with_max_freq.append(lanes_and_freq[t][0])
                                            unique_lanes_with_max_freq = []
                                            for p in lanes_with_max_freq:
                                                if p not in unique_lanes_with_max_freq:
                                                    unique_lanes_with_max_freq.append(p)
                                            # if cars[i].id == 10:
                                            #     print("lanes_freq: " + str(lanes_freq))
                                            #     print("lanes_and_freq: " + str(lanes_and_freq))
                                            #     print("count_lanes_with_mode: " + str(count_lanes_with_mode))
                                            #     print("unique_lanes_with_max_freq: " + str(unique_lanes_with_max_freq))
                                            #     input("uni pasue")

                                            if len(unique_lanes_with_max_freq) == 1:
                                                cars[i].g_lane = unique_lanes_with_max_freq[0]
                                                cars[i].g_track_path.append(cars[i].g_lane)
                                                cars[i].localised_stage = 2
                                            elif len(unique_lanes_with_max_freq) > 2:
                                                # check for associated lanes
                                                for lane_q in unique_lanes_with_max_freq:
                                                    # check_assoc_lane_temp = any(check_lane in lanes_test[lane_q].assoc_lanes for check_lane in unique_lanes_with_max_freq)
                                                    # out = any(check in list1 for check in list2)
                                                    check_lane_combo_temp = []
                                                    check_lane_combo_temp.append(lane_q)
                                                    for check_lane in lanes_test[lane_q].assoc_lanes:
                                                        if check_lane in unique_lanes_with_max_freq:
                                                            check_lane_combo_temp.append(check_lane)
                                                assoc_lane_present_temp = []
                                                for lane_temp_p in check_lane_combo_temp:
                                                    if check_lane_combo_temp.count(lane_temp_p) > 1:
                                                        #lane features more than once so is assoicated to another lane in unique_lanes_with_max_freq
                                                        if lane_temp_p not in assoc_lane_present_temp:
                                                            assoc_lane_present_temp.append(lane_temp_p)

                                                # now check if assoc_lane_present_temp is completely equal to unique_lanes_with_max_freq
                                                assoc_lane_present_temp_sorted = sorted(assoc_lane_present_temp)
                                                unique_lanes_with_max_freq_sorted = sorted(unique_lanes_with_max_freq)
                                                if assoc_lane_present_temp_sorted == unique_lanes_with_max_freq_sorted:
                                                    # car has localised in associated lanes, therefore, localised function ,ust randomly pick between either of these associated lanes
                                                    cars[i].g_lane = random.choice(assoc_lane_present_temp_sorted)
                                                    cars[i].g_track_path.append(cars[i].g_lane)
                                                    cars[i].localised_stage = 2

                                                else:
                                                    # asscciated lanes present but also another unrelated lane so can't confirm car localisation in this loop
                                                    # wait for next sample and repeat this section
                                                    cars[i].localised_stage = 1





                                            else:
                                                # two or more lanes with same max freq so there is no distinct mode
                                                # wait for next sample and repeat this section
                                                cars[i].localised_stage = 1


                                            #
                                            # if count_lanes_with_mode > 1:
                                            #     # two or more lanes with same max freq so there is no distinct mode
                                            #     # wait for next sample and repeat this section
                                            #     cars[i].localised_stage = 1
                                            # else:   # there if a lane with mode
                                            #     cars[i].g_lane = mode(cars[i].potential_lanes_3)
                                            #     cars[i].g_track_path.append(cars[i].g_lane)
                                            #     cars[i].localised_stage = 2 # car is localised

                                            # print("cars[i].localised_stage: " + str(cars[i].localised_stage))
                                            # input("please press enter 13...")


                                        if len(cars[i].potential_lanes_3) == 0: # car has moved enough in any lane
                                            # restart this section and find a new pl2, keep pl2 the same
                                            # if cars[i].id == 0:
                                            #     print("localised_stage set back to 1")
                                            cars[i].localised_stage = 1

                                    if len(cars[i].localisation_lanes_common) == 1:
                                        cars[i].g_lane = cars[i].localisation_lanes_common[0]
                                        cars[i].g_track_path.append(cars[i].g_lane)
                                        cars[i].localised_stage = 2 # car is localised
                                    if len(cars[i].localisation_lanes_common) == 0: # no common lanes between checks, therefore, car has moved into a new lane between checks, thus triggered find_side_points_1 and don't need to wait for next sample to check
                                        cars[i].potential_lanes_1 = cars[i].potential_lanes_2 # update potential_lanes_1 for input into find_side_points_1, # pl2 becomes pl1
                                        cars[i].potential_lanes_lines_1 = cars[i].potential_lanes_lines_2
                                        find_dist_to_lane_points_method_potential_lane_1(cars,lanes_test,i,rad_gps)
                                        # if i == 0:
                                        #     print("     here 13 cars[car_id].dist_lane_forward_points_1: " + str(cars[i].dist_lane_forward_points_1))
                                        cars[i].localised_stage = 1
                                else: # pl2 is empty
                                    cars[i].localised_stage = 1 # wait for next sample and take pl2 again


                # print("c_lane: " + str(cars[0].current_lane) + " g_lane: " + str(cars[0].g_lane))
                # print("car_in_lane_12: " + str(lanes_test[12].cars_in_lane_id))
                # print("localised_stage: " + str(cars[0].localised_stage))
                # time.sleep(sampling_time)
            running_timer = 0
            time_tracker += time_interval
            time.sleep(time_interval)
            if time_tracker >= sampling_time:
                time_tracker = 0
                running_timer = 1

class Find_Lane_Localisation_from_RealTest(Thread):
    def run(self):
        time.sleep(0.5)
        running_timer = 1
        sampling_counter = 0
        time_tracker = 0
        system_check_counter = 0
        # cars[0].sampling_checker = 0
        print_checker = 0
        sample = 0
        running_check = 1
        while running_check == 1:
            if running_timer == 1:
                # input("start stage ") # for testing
                # cars[0].sampling_checker = 1
                # time.sleep(time_interval)
                # cars[0].sampling_checker = 0
                print("sample: " + str(sample))
                # get_coord(cars,cars_in_system,car_store,cars_in_system_userID) ## not for testing
                for i in cars_in_system: #(38,39):  #(cars_in_system): #(0,1) check this
                    tr = 1
                    if tr != 1:
                        tr = 1
                    else:
                        create_coord(cars,i,rad_gps)

                        sample += 1
                        if cars[i].localised_stage == 2: # car has been alledgedly localised, however, perform to check as may have moved to another lane, update the guessed lane
                            # check consists of checking car is in the guess lane, if not check car is in the next_lanes leading from the guessed lane, if not meeting either of these critieria car has been lost and need to restart the localisation process
                            cars[i].localised_stage = 2
                            cars[i].recent_coords = cars[i].coords
                            # check for potential lanes
                            # find_potential_lanes_1(cars,lanes,i)
                            find_potential_lane_1_angle_method(cars,lanes_test,i)
                            # check if g_lane is in potential_lanes
                            if len(cars[i].potential_lanes_1) == 0: # sampling has taken place when car in middle of junction so no results
                                cars[i].potential_lanes_1 = lanes_test[cars[i].g_lane].next_lanes
                                # need to add that potential_lanes_lines_1 will need to  populate with the all points going forward             # decided not necessary s BUT MAY NEED TO CHECK
                                cars[i].localised_stage = 3 # this means it has once been localised but lost in junc so potential_points won't work
                                cars[i].g_lane = 99 # car not longer in previous lane so remove car's assignment to previous lane
                                cars[i].g_lane_line_tracker.append(cars[i].g_lane)

                            elif cars[i].g_lane in cars[i].potential_lanes_1:
                                # car is ok and assumed to still be in g_lane
                                cars[i].localised_stage = 2
                                # now check to see if the car has done a U-turn and is travelling back along the same road but in the opposite direction
                                # perform if car is in the same plotenial_lane_line of moved to one in front, is the lane_line equal to or greater than previous, need to find previous
                                # compare
                                # update the potenital_2 = potential_1
                                # cars[i].g_lane UNCHANGED
                                current_lane_line = 99
                                for t in range(len(cars[i].potential_lanes_lines_1)):
                                    if cars[i].g_lane == cars[i].potential_lanes_lines_1[t][0]:
                                        current_lane_line = cars[i].potential_lanes_lines_1[t][1]
                                # cuurent_lane_line = cars[i].potential_lanes_1[0][1]
                                if cars[i].g_lane_line <= current_lane_line:
                                    cars[i].g_lane_line = current_lane_line
                                    cars[i].g_lane_line_tracker.append([cars[i].g_lane,cars[i].g_lane_line])
                                else:
                                    #car performed a U-turn
                                    # set localised_stage to localised_stage_1
                                    cars[i].localised_stage = 1
                                    cars[i].g_lane = 99 # car not longer in previous lane so remove car's assignment to previous lane
                                    cars[i].g_lane_line_tracker.append(cars[i].g_lane)
                                    # cars[i].g_lane_line_tracker.append([cars[i].g_lane,current_lane_line])

                            elif len(cars[i].potential_lanes_1) > 0 and (cars[i].g_lane not in cars[i].potential_lanes_1):
                                # car has potenitally moved into a new lane
                                # add g_lane.next_lanes and g_lane.assoc_lanes to potential_lanes_1 and set car_localised_stage to 3
                                # check to see if any pl1 are in g_lane,next_lane
                                cars[i].localised_stage = 3
                                new_lane_temp = []
                                for u in cars[i].potential_lanes_1: # check to see if car has moved in a next_lane
                                    if u in lanes_test[cars[i].g_lane].next_lanes:
                                        new_lane_temp.append(u)
                                for u in cars[i].potential_lanes_1: # check to see if car has moved into an associated lane
                                    if u in lanes_test[cars[i].g_lane].assoc_lanes:
                                        new_lane_temp.append(u)
                                if len(new_lane_temp) == 1: #only one lane option so must be g_lane
                                    # car has moved to next lane so and update its g_lane to the new next_lane
                                    cars[i].g_lane = new_lane_temp[0]
                                    # print("before")
                                    # print("new_lane_temp: " + str(new_lane_temp))
                                    # print("cars[i].g_lane: " + str(cars[i].g_lane))
                                    # print("cars[i].potential_lanes_1: " + str(cars[i].potential_lanes_1))
                                    # print("cars[i].potential_lanes_lines_1: " + str(cars[i].potential_lanes_lines_1))
                                    # print("len(cars[i].potential_lanes_lines_1): " + str(len(cars[i].potential_lanes_lines_1)))
                                    # find the position of 41 in the potential_lanes_lines_1, can not assume it is a potential_lanes_lines_1[0]
                                    car_g_lane_in_pll_1 = 0
                                    for q in range(len(cars[i].potential_lanes_lines_1)):
                                        # print("cars[i].potential_lanes_lines_1[q][0]: " + str(cars[i].potential_lanes_lines_1[q][0]))
                                        # print("inner cars[i].g_lane: " + str(cars[i].g_lane))
                                        if cars[i].potential_lanes_lines_1[q][0] == cars[i].g_lane:
                                            cars[i].g_lane_line = cars[i].potential_lanes_lines_1[q][1]
                                            car_g_lane_in_pll_1 = 1
                                        # else:
                                        #     print("after")
                                        #     print("not found error")
                                        #     print("not found error car_id: " + str(i))
                                        #     print("new_lane_temp: " + str(new_lane_temp))
                                        #     print("cars[i].g_lane: " + str(cars[i].g_lane))
                                        #     print("cars[i].potential_lanes_1: " + str(cars[i].potential_lanes_1))
                                        #     print("cars[i].potential_lanes_lines_1: " + str(cars[i].potential_lanes_lines_1))
                                        #     input("enter not found")
                                    if car_g_lane_in_pll_1 == 0:
                                        print("not found error")
                                        input("enter not found")

                                    cars[i].g_lane_line_tracker.append([cars[i].g_lane,cars[i].g_lane_line])
                                    cars[i].g_track_path.append(cars[i].g_lane)
                                    cars[i].localised_stage = 2
                                    cars[i].localised = 1
                                if len(new_lane_temp) > 1:
                                    # perfrom the dist to points function, same as when pl1 is first found
                                    potential_lane_temp = new_lane_temp
                                    cars[i].potential_lanes_1 = potential_lane_temp
                                    find_dist_to_lane_points_method_potential_lane_1(cars,lanes_test,i,rad_gps)
                                    cars[i].localised_stage = 1
                                    cars[i].g_lane = 99 # car not longer in previous lane so remove car's assignment to previous lane
                                    cars[i].g_lane_line_tracker.append(cars[i].g_lane)

                                if cars[i].localised_stage == 3:
                                # add g_lane.next_lanes and g_lane.assoc_lanes to potential_lanes_1 and set car_localised_stage to 3
                                    # potential_lanes_temp = []
                                    # potential_lane_temp = lanes_test[cars[i].g_lane].next_lanes + lanes_test[cars[i].g_lane].assoc_lanes
                                    potential_lane_temp = new_lane_temp
                                    # cars[i].potential_lanes_1 = lanes_test[cars[i].g_lane].next_lanes
                                    cars[i].potential_lanes_1 = potential_lane_temp
                                    cars[i].localised_stage = 3 # this means it has once been localised but lost in junc won't work, wait for next sample
                                    cars[i].g_lane = 99 # car not longer in previous lane so remove car's assignment to previous lane
                                    cars[i].g_lane_line_tracker.append(cars[i].g_lane)
                                    # del(cars[i].g_lane)
                                    # if cars[i].id == 0:
                                    #     print("lost here 1")
                            else:
                                # first assume lost
                                cars[i].localised_stage = 0 # car is lost, if finsihes section in this state the localisation process will restart
                                cars[i].localised = 0 # car not localised, has been unlocalised
                                cars[i].g_lane = 99 # car not longer in previous lane so remove car's assignment to previous lane
                                cars[i].g_lane_line_tracker.append(cars[i].g_lane)
                            # print("local_stage: " + str(cars[i].localised_stage))

                        else:
                            if cars[i].localised_stage == 0: # first notion of this car or moved lane before localising in previous lane ie. location is unknown
                                # print("car localising")
                                cars[i].orig_coords = cars[i].coords
                                # find_potential_lanes_1(cars,lanes,i)
                                find_potential_lane_1_angle_method(cars,lanes_test,i)
                                find_dist_to_lane_points_method_potential_lane_1(cars,lanes_test,i,rad_gps)
                                # if i == 10:
                                #     print("     here 11 cars[car_id].dist_lane_forward_points_1: " + str(cars[i].dist_lane_forward_points_1))
                                cars[i].localised_stage = 1 # original potential lanes and points stored#
                                if len(cars[i].potential_lanes_1) == 1: # ie. only one lane option,
                                    # we know the car must be in this lane]
                                    cars[i].g_lane = cars[i].potential_lanes_1[0] # the first and only entry of the pl1
                                    cars[i].g_lane_line = cars[i].potential_lanes_lines_1[0][1]
                                    cars[i].g_lane_line_tracker.append([cars[i].g_lane,cars[i].g_lane_line])
                                    cars[i].g_track_path.append(cars[i].g_lane)
                                    cars[i].localised_stage = 2
                                    cars[i].localised = 1
                                # if cars[i].id == 10:
                                #     print("cars[i].potential_lanes_1 ls0: " + str(cars[i].potential_lanes_1))
                                #     print("cars[i].potential_lanes_lines_1 ls0: " + str(cars[i].potential_lanes_lines_1))
                                #     print("cars[i].dist_lane_forward_points_1 ls0: " + str(cars[i].dist_lane_forward_points_1))

                            elif cars[i].localised_stage == 3: # car has been locaised previously but was lost, as potential_lanes_1 was empty (or g_lane was not in pl1) but now is populated by g_lane.next_lanes
                                # potential_lanes_1 has previously been created from the g_lane.next_lanes want to check if there is one of the potential_lanes_2 is common with potential_lanes_1
                                find_potential_lane_2_angle_method(cars,lanes_test,i)
                                # print("pl2_in: " + str(cars[0].potential_lanes_2))
                                if len(cars[i].potential_lanes_2) == 0: #empty pl2, car still stuck in junc or another junc
                                    # keep in this sectoin for the next sample
                                    cars[i].localised_stage = 3

                                if len(cars[i].potential_lanes_2) != 0:
                                    lanes_common = []
                                    for check_lane in cars[i].potential_lanes_1:
                                        if check_lane in cars[i].potential_lanes_2:
                                            lanes_common.append(check_lane)
                                    if len(lanes_common) == 1:
                                        if (len(cars[i].potential_lanes_1) == 1) and (len(cars[i].potential_lanes_2) == 1):
                                            # we can confirm that the car must have moved into this lane
                                            cars[i].g_lane = lanes_common[0] # the first and only entry of the lanes_common list
                                            # find g_lane_line in potential_lanes_2
                                            for t in range(len(cars[i].potential_lanes_lines_2)):
                                                if cars[i].g_lane == cars[i].potential_lanes_lines_2[t][0]:
                                                    cars[i].g_lane_line = cars[i].potential_lanes_lines_2[t][1]
                                                    cars[i].g_lane_line_tracker.append([cars[i].g_lane,cars[i].g_lane_line])
                                            cars[i].g_track_path.append(cars[i].g_lane)
                                            cars[i].localised_stage = 2
                                            cars[i].localised = 1
                                    elif len(lanes_common) == 0:
                                        # car lost, need to start localisation process again ie. zero lanes_common
                                        cars[i].localised_stage = 0
                                        # here should update potential_lanes_1 and trigger find_dist_to_lane_points_method_potential_lane_1
                                        cars[i].potential_lanes_1 = cars[i].potential_lanes_2 # pl2 becomes pl1
                                        cars[i].potential_lanes_lines_1 = cars[i].potential_lanes_lines_2 # pl2 lines becomes pl1 lines
                                        find_dist_to_lane_points_method_potential_lane_1(cars,lanes_test,i,rad_gps)
                                        # if i == 10:
                                        #     print("     here 12 cars[car_id].dist_lane_forward_points_1: " + str(cars[i].dist_lane_forward_points_1))
                                        cars[i].localised_stage = 1
                                    elif len(lanes_common) > 1: # this is WRONG
                                     # ie. more than 1 so can not decide so try again on next loop, ie. just pause for next sample                  #### THIS AREA MIGHT NEED ATTENTION
                                        # cars[i].localised_stage = 3 # is was the the previous case
                                        find_dist_to_lane_points_method_potential_lane_1(cars,lanes_test,i,rad_gps)
                                        cars[i].localised_stage = 1 # which will take pl2 and find lane in the next sample
                                        # add find_dist_to_lane_points_method_lanes_common
#######################################################################
                            elif  cars[i].localised_stage == 1: # original potential lanes and
                                find_potential_lane_2_angle_method(cars,lanes_test,i)
                                # find lanes_common between pl1 and pl2
                                # find distance between forward points for lanes_common
                                # find distance chagne for common lanes and lane points between potential_lanes_1 and potential_lanes_lines_2
                                # print("localised_stage_1")
                                # print("cars[i].potential_lanes_2: " + str(cars[i].potential_lanes_2))
                                # print("cars[i].potential_lanes_1: " + str(cars[i].potential_lanes_1))
                                # print("cars[i].dist_lane_forward_points_1: " + str(cars[i].dist_lane_forward_points_1))
                                if len(cars[i].potential_lanes_2) != 0:
                                    # check if common lanes between potential_lanes_1 and potential_lanes_2
                                    lanes_common = []
                                    for check_lane in cars[i].potential_lanes_1:
                                        if check_lane in cars[i].potential_lanes_2:
                                            lanes_common.append(check_lane)
                                    cars[i].localisation_lanes_common = lanes_common
                                    # if cars[i].id == 10:
                                    #     print("cars[i].localisation_lanes_common: " + str(cars[i].localisation_lanes_common))
                                    if len(cars[i].localisation_lanes_common) > 1:
                                        # find the distances between car coords and the forward points in the common lanes compare these to the dist from 1. if closer to 1 point in a lane must be in that lane, if closer to a point in both lanes inconclusive and wait for next loop to find pl2
                                        # find index of common_lane in potential_lanes_2
                                        # extract the line and point_of_intersection for this lane
                                        # find the distance between point_of_intersection forward points for this lane
                                        # store these in the same method as dist_lane_forward_points_1, and call it dist_lane_forward_points_2
                                        # find index of common_lane in potential_lanes_2
                                        cars[i].dist_lane_forward_points_lanes_common = []
                                        find_dist_to_lane_points_method_lanes_common(cars,lanes_test,i,rad_gps)
                                        # need to update dist_to_lane_points_method_potential_lane_1
                                        find_dist_to_lane_points_method_potential_lane_1(cars,lanes_test,i,rad_gps)
                                        # print("cars[i].dist_lane_forward_points_lanes_common: " + str(cars[i].dist_lane_forward_points_lanes_common))
                                        # if cars[i].id == 10:
                                        #     print("cars[i].dist_lane_forward_points_lanes_common: " + str(cars[i].dist_lane_forward_points_lanes_common))
                                            # input("press 14")
                                        # now compare dist_lane_forward_points_1 and dist_lane_forward_points_lanes_common
                                         # filter out lanes in dist_lane_forward_points_1 that are not in lanes_common, only interested in lanes_common
                                        # print("cars[i].dist_lane_forward_points_lanes_common: " + str(cars[i].dist_lane_forward_points_lanes_common))
                                        # print("cars[i].dist_lane_forward_points_1: " + str(cars[i].dist_lane_forward_points_1))
                                        lane_common_temp = []
                                        lane_point_index_common_temp = []
                                        cars[i].potential_lanes_3 = []
                                        for r in range(len(cars[i].dist_lane_forward_points_lanes_common)): # loop through the lanes_common
                                            lane_common_extract_lane = cars[i].dist_lane_forward_points_lanes_common[r][0]
                                            for t in range(len(cars[i].dist_lane_forward_points_1)): # loop through lanes
                                                extract_lane_t = cars[i].dist_lane_forward_points_1[t][0]
                                                for q in range(1,len(cars[i].dist_lane_forward_points_1[t])): # loop through the points associated with lane
                                                    # check if a lane and point are common to both
                                                    # extract_lane_t = cars[i].dist_lane_forward_points_1[t][q]
                                                    extract_point = cars[i].dist_lane_forward_points_1[t][q][0]
                                                    extract_dist = cars[i].dist_lane_forward_points_1[t][q][1]
                                                    old_dist = extract_dist

                                                    # extract_point and dists from cars[i].dist_lane_forward_points_lanes_common
                                                    for s in range(1,len(cars[i].dist_lane_forward_points_lanes_common[r])): # loop through the points associated with this common lane
                                                        lane_com_extract_point = cars[i].dist_lane_forward_points_lanes_common[r][s][0]
                                                        lane_com_extract_dist = cars[i].dist_lane_forward_points_lanes_common[r][s][1]
                                                        new_dist = lane_com_extract_dist

                                                        # print("extract_lane_t: " + str(extract_lane_t) + " extract_point: " + str(extract_point) + " extract_dist: " + str(extract_dist))
                                                        # print("lane_common_extract_lane: " + str(lane_common_extract_lane) + " lane_com_extract_point: " + str(lane_com_extract_point) + " lane_com_extract_dist: " + str(lane_com_extract_dist))
                                                        # input("please press enter 11...")

                                                        if (extract_lane_t == lane_common_extract_lane) and (extract_point == lane_com_extract_point):
                                                            # we know that there is a common lane forward point in the dist_lane_forward_points_1 and dist_lane_forward_points_lanes_common
                                                            # now check the distance change betweeen the points
                                                            # change_dist = abs(extract_dist - lane_com_extract_dist)
                                                            # how many closer is the new point than the old point
                                                            change_dist = old_dist - new_dist
                                                            # change_dist = abs(change_dist)
                                                            # if cars[i].id == 10:
                                                            #     print("extract_lane_t: " + str(extract_lane_t))
                                                            #     print("extract_dist: " + str(extract_dist))
                                                            #     print("lane_com_extract_dist: " + str(lane_com_extract_dist))
                                                            #     print("change_dist: " + str(change_dist))
                                                            # input("please press enter 12...")
                                                            # print("change_dist: " + str(change_dist))
                                                            if change_dist > (2*rad_gps):
                                                                # highly liekly car is in the this lane
                                                                cars[i].potential_lanes_3.append(extract_lane_t)
                                                            # which ever lane has the highest frequency in high_chance_lane, set that lane to be car[i].g_lane   #####   THIS MIGHT NEED ATTENTION
                                        #find the most frequent lane number in cars[i].potential_lanes_3
                                        if len(cars[i].potential_lanes_3) > 0:
                                            # if cars[i].id == 10:
                                            #     print("cars[i].potential_lanes_3: " + str(cars[i].potential_lanes_3))
                                            # lane_freq = 0
                                            # if i == 76:
                                            #     print("made it here")
                                            #     input("end it here now")
                                            lanes_and_freq = []
                                            lanes_freq = []
                                            for lane_id in cars[i].potential_lanes_3:
                                                lane_freq = cars[i].potential_lanes_3.count(lane_id)
                                                lanes_freq.append(lane_freq)
                                                lanes_and_freq.append([lane_id,lane_freq])
                                            max_freq = max(lanes_freq)
                                            count_lanes_with_mode = lanes_freq.count(max_freq)
                                            #find lanes that have the freq = amx_freq
                                            lanes_with_max_freq = []
                                            for t in range(len(lanes_and_freq)):
                                                # count_lane_freq = lanes_and_freq[t][1]
                                                if lanes_and_freq[t][1] == max_freq:
                                                    lanes_with_max_freq.append(lanes_and_freq[t][0])
                                            unique_lanes_with_max_freq = []
                                            for p in lanes_with_max_freq:
                                                if p not in unique_lanes_with_max_freq:
                                                    unique_lanes_with_max_freq.append(p)
                                            # if i == 76:
                                            #     print("made it here")
                                            #     print("         unique_lanes_with_max_freq: " + str(unique_lanes_with_max_freq))
                                                # input("end it here now")
                                            if len(unique_lanes_with_max_freq) == 1:
                                                cars[i].g_lane = unique_lanes_with_max_freq[0]
                                                # find g_lane_line in potential_lanes_2
                                                for t in range(len(cars[i].potential_lanes_lines_2)):
                                                    if cars[i].g_lane == cars[i].potential_lanes_lines_2[t][0]:
                                                        cars[i].g_lane_line = cars[i].potential_lanes_lines_2[t][1]
                                                        cars[i].g_lane_line_tracker.append([cars[i].g_lane,cars[i].g_lane_line])
                                                cars[i].g_track_path.append(cars[i].g_lane)
                                                cars[i].localised_stage = 2
                                            elif len(unique_lanes_with_max_freq) > 1:
                                                # check for associated lanes
                                                for lane_q in unique_lanes_with_max_freq:
                                                    # check_assoc_lane_temp = any(check_lane in lanes_test[lane_q].assoc_lanes for check_lane in unique_lanes_with_max_freq)
                                                    # out = any(check in list1 for check in list2)
                                                    check_lane_combo_temp = []
                                                    check_lane_combo_temp.append(lane_q)
                                                    for check_lane in lanes_test[lane_q].assoc_lanes:
                                                        if check_lane in unique_lanes_with_max_freq:
                                                            check_lane_combo_temp.append(check_lane)
                                                # if i == 76:
                                                #     print("made it here")
                                                #     print("         check_lane_combo_temp: " + str(check_lane_combo_temp))
                                                assoc_lane_present_temp = []
                                                for lane_temp_p in check_lane_combo_temp:
                                                    if check_lane_combo_temp.count(lane_temp_p) > 1:
                                                        #lane features more than once so is assoicated to another lane in unique_lanes_with_max_freq
                                                        if lane_temp_p not in assoc_lane_present_temp:
                                                            assoc_lane_present_temp.append(lane_temp_p)

                                                # now check if assoc_lane_present_temp is completely equal to unique_lanes_with_max_freq
                                                assoc_lane_present_temp_sorted = sorted(assoc_lane_present_temp)
                                                unique_lanes_with_max_freq_sorted = sorted(unique_lanes_with_max_freq)
                                                ####### this scetion does not appear in the real test localisation
                                                if len(assoc_lane_present_temp_sorted) == 0:
                                                    assoc_lane_present_temp_sorted = unique_lanes_with_max_freq_sorted
                                                ####### end of section

                                                # if i == 76:
                                                #     print("made it here")
                                                #     print("         unique_lanes_with_max_freq_sorted: " + str(unique_lanes_with_max_freq_sorted))
                                                #     print("         assoc_lane_present_temp_sorted: " + str(assoc_lane_present_temp_sorted))
                                                if assoc_lane_present_temp_sorted == unique_lanes_with_max_freq_sorted:
                                                    # car has localised in associated lanes, therefore, localised function must randomly pick between either of these associated lanes
                                                    cars[i].g_lane = random.choice(assoc_lane_present_temp_sorted)
                                                    # find g_lane_line in potential_lanes_2
                                                    for t in range(len(cars[i].potential_lanes_lines_2)):
                                                        if cars[i].g_lane == cars[i].potential_lanes_lines_2[t][0]:
                                                            cars[i].g_lane_line = cars[i].potential_lanes_lines_2[t][1]
                                                            cars[i].g_lane_line_tracker.append([cars[i].g_lane,cars[i].g_lane_line])
                                                    cars[i].g_track_path.append(cars[i].g_lane)
                                                    cars[i].localised_stage = 2
                                                else:
                                                    # asscciated lanes present but also another unrelated lane so can't confirm car localisation in this loop
                                                    # wait for next sample and repeat this section
                                                    cars[i].localised_stage = 1
                                            else:
                                                # two or more lanes with same max freq so there is no distinct mode
                                                # wait for next sample and repeat this section
                                                cars[i].localised_stage = 1

                                        if len(cars[i].potential_lanes_3) == 0: # car has moved enough in any lane
                                            # restart this section and find a new pl2, keep pl2 the same
                                            # if cars[i].id == 0:
                                                # print("localised_stage set back to 1")
                                            cars[i].localised_stage = 1

                                    if len(cars[i].localisation_lanes_common) == 1:
                                        cars[i].g_lane = cars[i].localisation_lanes_common[0]
                                        # find g_lane_line in potential_lanes_2
                                        for t in range(len(cars[i].potential_lanes_lines_2)):
                                            if cars[i].g_lane == cars[i].potential_lanes_lines_2[t][0]:
                                                cars[i].g_lane_line = cars[i].potential_lanes_lines_2[t][1]
                                                cars[i].g_lane_line_tracker.append([cars[i].g_lane,cars[i].g_lane_line])
                                        cars[i].g_track_path.append(cars[i].g_lane)
                                        cars[i].localised_stage = 2 # car is localised
                                    if len(cars[i].localisation_lanes_common) == 0: # no common lanes between checks, therefore, car has moved into a new lane between checks, thus triggered find_side_points_1 and don't need to wait for next sample to check
                                        cars[i].potential_lanes_1 = cars[i].potential_lanes_2 # update potential_lanes_1 for input into find_side_points_1, # pl2 becomes pl1
                                        cars[i].potential_lanes_lines_1 = cars[i].potential_lanes_lines_2
                                        find_dist_to_lane_points_method_potential_lane_1(cars,lanes_test,i,rad_gps)
                                        # if i == 0:
                                        #     print("     here 13 cars[car_id].dist_lane_forward_points_1: " + str(cars[i].dist_lane_forward_points_1))
                                        cars[i].localised_stage = 1
                                else: # pl2 is empty
                                    cars[i].localised_stage = 1 # wait for next sample and take pl2 again
                # print("localised_stage: " + str(cars[0].localised_stage))
                    # if i == 2:
                    #     print("car: " + str(cars[i].id) + " pl1: " + str(cars[i].potential_lanes_1))
                    #     print("car: " + str(cars[i].id) + " pl2: " + str(cars[i].potential_lanes_2))
                    #     print("car: " + str(cars[i].id) + " g_lane: " + str(cars[i].g_lane) + " cur_lane: " + str(cars[i].current_lane))
                    #     print("car: " + str(cars[i].id) + " g_lane_line_tracker: " + str(cars[i].g_lane_line_tracker))
                    #     print("car: " + str(cars[i].id) + " localised_stage: " + str(cars[i].localised_stage))

                    # print("car: " + str(cars[i].id) + " pl1: " + str(cars[i].potential_lanes_1))
                    # print("car: " + str(cars[i].id) + " pl2: " + str(cars[i].potential_lanes_2))
                    # print("car: " + str(cars[i].id) + " g_lane: " + str(cars[i].g_lane))
                    # print("car: " + str(cars[i].id) + " g_lane_line_tracker: " + str(cars[i].g_lane_line_tracker))
                    # print("car: " + str(cars[i].id) + " localised_stage: " + str(cars[i].localised_stage))
                # time.sleep(sampling_time)
            running_timer = 0
            time_tracker += time_interval
            print_checker += time_interval
            # print("print_checker: " + str(print_checker))
            if print_checker >= 60:
                print_checker = 0
                # print("car_store: " + str(car_store))
                # for t in range(len(car_store)):
                #     print("cars[t].id: " + str(cars[t].id))
                #     print("cars[t].userID: "+ str(cars[t].userID) + " car_id: " + str(cars[t].id))
                #     print("cars[t].coord_tracker: " + str(cars[t].coord_tracker))
                #     print("g_lane_line_tracker: " + str(cars[t].g_lane_line_tracker))
                #     print("traffic_light_store: " + str(traffic_light_store))
                # for q in range(len(juncs_test)):
                #     print("junc_id: " + str(q)  + " light_change_history: " + str(juncs_test[q].light_change_history))
            if time_tracker >= sampling_time:
                time_tracker = 0
                running_timer = 1
                print("print_checker: " + str(print_checker))
            time.sleep(time_interval) # not for testing

time_between_loops = 1
class ExtractCarInfo(Thread):
    def run(self):
        while running_check == 1:
            # print("runnung")
            time.sleep(time_between_loops)
            # print(cars[21].g_wait_time)
            for i in cars_in_system:
                if cars[i].g_lane != cars[i].g_lane_temp: # cars has changed lane since last loop
                    lanes_test[cars[i].g_lane].g_cars_in_lane_id.append(cars[i].id)  # update g_cars_in_lane_id
                    if cars[i].g_lane_temp != 99:
                        lanes_test[cars[i].g_lane_temp].g_cars_in_lane_id.remove(cars[i].id) # update g_cars_in_lane_id
                    cars[i].g_lane_temp = cars[i].g_lane # update g_lane_temp
                    cars[i].g_wait_time = 0 # set g_wait_time back to zero as car has moved
                elif cars[i].g_lane == cars[i].g_lane_temp: # cars in the same lane since last loop
                    # do not need to update g_cars_in_lane_id for any lane
                    cars[i].g_wait_time += time_between_loops # increase g_wait_time as car still in lane

class FindWaitTimeForLanes(Thread):    ################ need to check all these loops give the desired answer
    def run(self):
        # time.sleep(2)
        while running_check == 1:
            time.sleep(time_between_loops)
            # print("junc2_wtt: " + str(juncs[2].g_junc_wait_time_total))
            # print("lane2_wtt: " + str(lanes[2].g_lane_wait_time_total))
            # find the wait times for each lane and junction
            for i in range(len(juncs_test)):
                juncs_test[i].g_junc_wait_time_total = 0
                for k in juncs_test[i].lanes_at_junc:
                    lanes_test[k].g_lane_wait_time_total = 0
                    # g_tot_lane_wait_time = 0
                    for s in lanes_test[k].g_cars_in_lane_id:
                        lanes_test[k].g_lane_wait_time_total += cars[s].g_wait_time
                    juncs_test[i].g_junc_wait_time_total += lanes_test[k].g_lane_wait_time_total

class FindGreenLightLanes(Thread): # this is the algo for assign green light to lanes based on weighted
    def run(self):
        while running_check == 1:
            time.sleep(time_between_loops)
            for i in range(len(juncs_test)):
                if juncs_test[i].ready_for_green == 1: # junction ready for next green light
                    lane_selection_options = []
                    for k in juncs_test[i].light_lanes_at_junc:
                        if juncs_test[i].g_junc_wait_time_total > 0: # need this if statement as can't divide by zero
                            lane_freq = math.ceil((lanes_test[k].g_lane_wait_time_total / juncs_test[i].g_junc_wait_time_total) * 12) # num_times_lane_will_feature_in_selection_matrix
                        else:
                            lane_freq = 0
                        if lane_freq < 2: # want each to lane in the junc to appear, as can't be cetain there isn't a car there
                            lane_freq = 2
                        for t in range(lane_freq - 1):
                            lane_selection_options.append(k)  # store the lane number as many times as its frequency, so if lane[1] had a lane_freq of 4 the number 1  will appear 4 times in lane_selection
                            # lane_selection_options.append(lanes_test[k].lane_id[0])  # store the lane number as many times as its frequency, so if lane[1] had a lane_freq of 4 the number 1  will appear 4 times in lane_selection
                    lane_selected = random.choice(lane_selection_options)
                    lanes_test[lane_selected].green_light = 1 # acts as indicator that this lane now has a green light
                    lanes_test[lane_selected].time_green = 3
                    if len(lanes_test[lane_selected].assoc_lanes) > 0:
                        for k in lanes_test[lane_selected].assoc_lanes:
                            t = 0
                            lanes_test[k].green_light = 1
                            lanes_test[k].time_green = 3
                    # turn_light_green(lane_selected)
                    juncs_test[i].ready_for_green = 0 # green light lane allocaated to junction so turn off (set to 0) ready_for_green

def fut_pos_change_lane(car_id,lanes_test,cars,Car): # populate cars[car_id].fut_pos with the future points between current lane and next lane
    next_lane = cars[car_id].next_lane
    # current_lane = 0
    # next_lane_index = lanes_test[current_lane].next_lanes.index(next_lane)
    next_lane_index = lanes_test[cars[car_id].current_lane].next_lanes.index(next_lane)
    # temp_fut_pos_between_lanes = lanes_test[current_lane].move_points_next_lanes[next_lane_index]
    temp_fut_pos_between_lanes = lanes_test[cars[car_id].current_lane].move_points_next_lanes[next_lane_index]
    # print("temp_fut_pos_between_lanes: " + str(temp_fut_pos_between_lanes))
    for i in range(len(temp_fut_pos_between_lanes)):
        cars[car_id].fut_pos.append(temp_fut_pos_between_lanes[i])
def fut_pos_current_lane(car_id,lanes_test,cars,Car): # populate cars[car_id].fut_pos with the future points from the start to the end of the current lane
    #cehck if next_lane in free_turn_next_lanes
    if cars[car_id].next_lane in lanes_test[cars[car_id].current_lane].free_turn_next_lanes:
        # find the fut_pos to the end of the lane and call it sometihing different
        cars[car_id].fut_pos_psuedo = cars[car_id].fut_pos[:]
        for j in range(len(lanes_test[cars[car_id].current_lane].move_points)):
            cars[car_id].fut_pos_psuedo.append(lanes_test[cars[car_id].current_lane].move_points[j]) # store the x and     y points and angle for the future pos in this lane, to take car to end of lane
        if lanes_test[cars[car_id].current_lane].next_lanes[0] == 9999:
            cars[car_id].fut_pos_psuedo.append([50,50,(math.pi/2)])
        # find index of next_lane in free_turn_next_lane_move_points
        for k in range(len(lanes_test[cars[car_id].current_lane].free_turn_next_lane_move_points)):
            if cars[car_id].next_lane == lanes_test[cars[car_id].current_lane].free_turn_next_lane_move_points[k][0]:
                for q in range(1,len(lanes_test[cars[car_id].current_lane].free_turn_next_lane_move_points[k])):
                    cars[car_id].fut_pos.append(lanes_test[cars[car_id].current_lane].free_turn_next_lane_move_points[k][q])
    else:
        for j in range(len(lanes_test[cars[car_id].current_lane].move_points)):
            cars[car_id].fut_pos.append(lanes_test[cars[car_id].current_lane].move_points[j]) # store the x and     y points and angle for the future pos in this lane, to take car to end of lane
        if lanes_test[cars[car_id].current_lane].next_lanes[0] == 9999:
            cars[car_id].fut_pos.append([50,50,(math.pi/2)])
def find_current_end_step(car_id,lanes_test,cars,Car): # find the step the car should move to in the current lane
    # car is going into a free_turn_next_lane use the samller of the two between fut_pos and fut_pos_psuedo
    if lanes_test[cars[car_id].current_lane].next_lanes[0] == 9999:
        cars[car_id].current_end_step = (len(cars[car_id].fut_pos)) - 1
    elif cars[car_id].next_lane in lanes_test[cars[car_id].current_lane].free_turn_next_lanes:
        pos_in_queue = lanes_test[cars[car_id].current_lane].cars_in_lane_id.index(cars[car_id].id)
        offset_first = 4
        offset = 5
        # set the current_lane_end_step as the last step the in this lane for the car to take
        cars[car_id].current_lane_end_step = (len(cars[car_id].fut_pos)) - offset_first
        ###############
        if pos_in_queue == 0:
            cars[car_id].current_end_step = cars[car_id].current_lane_end_step
        else: # ie . pos_in_queue !=0
            car_in_front_id =  lanes_test[cars[car_id].current_lane].cars_in_lane_id[(pos_in_queue - 1)]
            car_in_front_current_end_step_move_point = cars[car_in_front_id].fut_pos[cars[car_in_front_id].current_end_step]
            if car_in_front_current_end_step_move_point in cars[car_id].fut_pos[cars[car_id].step:]: # check if car_in_front.current)end_step in the cars.fut_pos
                start_looking_after_value = cars[car_id].step
                index_step_temp = cars[car_id].fut_pos.index(car_in_front_current_end_step_move_point,start_looking_after_value)
                cars[car_id].current_end_step = index_step_temp - offset
            else:
                cars[car_id].current_end_step = cars[car_id].current_lane_end_step



        ###############
        # # now find the current_end_step accounting for cars in the lane
        # # current_end_step_from_fut_pos_psuedo = (len(cars[car_id].fut_pos_psuedo)) - (pos_in_queue * offset) - offset_first
        # current_end_step_from_fut_pos_psuedo = (len(cars[car_id].fut_pos_psuedo)) - offset_first
        # current_end_step_from_fut_pos = (len(cars[car_id].fut_pos)) - offset_first
        # if pos_in_queue != 0: # ie. pos_in_queue != 0
        #     offset = 5 # for solution 2, was changed from offset = 5
        #     #find current move_point of car in fornt
        #     car_in_front_id =  lanes_test[cars[car_id].current_lane].cars_in_lane_id[(pos_in_queue - 1)]
        #     car_in_front_move_point = cars[car_in_front_id].fut_pos[cars[car_in_front_id].step]
        #     # now find the index of car_in_front_move_point in cars[car_id].fut_pos
        #     if car_in_front_move_point in cars[car_id].fut_pos[cars[car_id].step:]: # in fut_pos between current step to the end
        #         start_looking_after_value = cars[car_id].step
        #         index_step_temp = cars[car_id].fut_pos.index(car_in_front_move_point,start_looking_after_value)
        #         updated_current_end_step_from_fut_pos_psuedo = index_step_temp - offset
        #         # cars[car_id].updated_current_end_step = index_step_temp - offset
        #         # if index_step_temp <= start_looking_after_value:
        #         if (updated_current_end_step_from_fut_pos_psuedo < current_end_step_from_fut_pos_psuedo) and (cars[car_in_front_id].step == cars[car_in_front_id].current_end_step): # ie. car_in_front has moved into lane  # solution 1
        #         # if (updated_current_end_step_from_fut_pos_psuedo < current_end_step_from_fut_pos_psuedo): # solution 2 reduce the offset value from 5 to 4
        #             current_end_step_from_fut_pos_psuedo = updated_current_end_step_from_fut_pos_psuedo
        #             if car_id == 20:
        #                 print("20 updated_psuedo: " + str(updated_current_end_step_from_fut_pos_psuedo) + " cur_psuedo: " + str(current_end_step_from_fut_pos_psuedo))
        #                 print("20 current_end_step_from_fut_pos: " + str(current_end_step_from_fut_pos) + " car_step: " + str(cars[car_id].step))
        #     else:
        #         updated_current_end_step_from_fut_pos_psuedo = current_end_step_from_fut_pos_psuedo
        # # do cmpareiosn between psuedo and other to set .current_end_step to the smaller step
        # if current_end_step_from_fut_pos_psuedo < current_end_step_from_fut_pos:
        #     cars[car_id].current_end_step = current_end_step_from_fut_pos_psuedo
        # else:
        #     cars[car_id].current_end_step = current_end_step_from_fut_pos
        ##########
    else:
        pos_in_queue = lanes_test[cars[car_id].current_lane].cars_in_lane_id.index(cars[car_id].id)
        # cars[car_id].current_end_step = ((len(cars[car_id].fut_pos)) - (pos_in_queue * 5))  - 1
        offset_first = 4
        cars[car_id].current_lane_end_step = (len(cars[car_id].fut_pos)) - offset_first
        if pos_in_queue == 0: # car at front
            # offset = int(half_car_length/move_val)
            # offset_first = 4
            # print("offset: " + str(offset))
            cars[car_id].current_end_step = (len(cars[car_id].fut_pos)) - offset_first
            # if car_id == 0:
            #     print("ran  pos_in_queue: " + str(pos_in_queue))
            #     print("current_end_step: " + str(cars[car_id].current_end_step))
            cars[car_id].end_step_for_current_lane = len(lanes_test[cars[car_id].current_lane].move_points) - offset_first
            cars[car_id].step_in_current_lane = cars[car_id].end_step_for_current_lane
            cars[car_id].front_queue_check = 1
            if lanes_test[cars[car_id].current_lane].next_lanes[0] == 9999:
                cars[car_id].current_end_step = (len(cars[car_id].fut_pos)) - 1

        # else:
        #     # position of car in front
        #     offset = 5
        #     cars[car_id].current_end_step = (len(cars[car_id].fut_pos)) - (pos_in_queue * offset) - offset_first
        #     cars[car_id].end_step_for_current_lane = len(lanes_test[cars[car_id].current_lane].move_points) - (pos_in_queue * offset) - offset_first

        if lanes_test[cars[car_id].current_lane].next_lanes[0] == 9999:
            cars[car_id].current_end_step = (len(cars[car_id].fut_pos)) - 1
        # cars[car_id].current_end_step = ((len(cars[car_id].fut_pos)) - (pos_in_queue * 5))  - 1
        pos_in_queue = lanes_test[cars[car_id].current_lane].cars_in_lane_id.index(cars[car_id].id)
        if pos_in_queue != 0:
            offset = 5
            # if (car_id == 308) or (car_id == 373) or (car_id == 425):
            #     print("     running find_current_end_step car_id: " + str(car_id))
            #find current move_point of car in fornt
            car_in_front_id =  lanes_test[cars[car_id].current_lane].cars_in_lane_id[(pos_in_queue - 1)]
            car_in_front_move_point = cars[car_in_front_id].fut_pos[cars[car_in_front_id].step]
            car_in_front_move_point_current_end_step = cars[car_in_front_id].fut_pos[cars[car_in_front_id].current_end_step]
            # now find the index of car_in_front_move_point in cars[car_id].fut_pos
            if car_in_front_move_point_current_end_step in cars[car_id].fut_pos[cars[car_id].step:]: # in fut_pos between current step to the end
                start_looking_after_value = cars[car_id].step
                index_step_temp = cars[car_id].fut_pos.index(car_in_front_move_point_current_end_step,start_looking_after_value)
                cars[car_id].updated_current_end_step = index_step_temp - offset

                # if index_step_temp <= start_looking_after_value:
                #     print("car: " + str())
                # if car_id == 89:
                #     print("inside 1     section updated_current_end_step: " + str(cars[car_id].updated_current_end_step))
                #     print("car_in_front_id: " + str(car_in_front_id))
                #     print("car_in_front_move_point: " + str(car_in_front_move_point))
                #     print("start_looking_after_value: " + str(start_looking_after_value))
                #     print("index_step_temp: " + str(index_step_temp))

                # if cars[car_id].updated_current_end_step < cars[car_id].current_end_step:
                #     cars[car_id].updated_current_end_step = cars[car_id].current_end_step
                # else:



                    # if cars[car_id].current_lane == 30:
                    #     print("find_current_end_step for lane 30")
                    #     print("car_id: " + str(car_id) + " nt_lane: " + str(cars[car_id].next_lane))
                    #     print("car_in_front_id: " + str(car_in_front_id) + " nt_lane: " + str(cars[car_in_front_id].next_lane))
                cars[car_id].current_end_step = cars[car_id].updated_current_end_step
            else:
                # car in front passed the current_lane_end_step, could be that the car is taking a free turn but car_in_front is not
                # or could be the car in front is taking the free turn lane and their fut_pos contains transition points that the car in question will not take, but don't see how this would be the case
                cars[car_id].current_end_step = cars[car_id].current_lane_end_step
                # if (cars[car_id].current_lane == 30) and (cars[car_id].next_lane == 34):
                #     # print("find_current_end_step for lane 30")
                    # print("car_id: " + str(car_id) + " nt_lane: " + str(cars[car_id].next_lane))
                    # print("cars_in_lane_id: " + str(lanes_test[30].cars_in_lane_id))
                    # print("car_id pos_in_queue: " + str(pos_in_queue))
                    # print("car_in_front: " + str(car_in_front_id) + " nt_lane: " + str(cars[car_in_front_id].next_lane))
                    # print("cars[car_id].step: " + str(cars[car_id].step) + "  cars[car_id].fut_pos: " + str(cars[car_id].fut_pos))
                    # print("car_in_front_move_point: " + str(car_in_front_move_point) + " car_in_front_move_point_current_end_step: " + str(car_in_front_move_point_current_end_step))
                    # print("cars[car_in_front_id].step: " + str(cars[car_in_front_id].step) + " cars[car_in_front_id].current_end_step: " + str(cars[car_in_front_id].current_end_step))
                    #
                    # canvas.itemconfig(cars[car_id].body, fill='red')
                    # canvas.itemconfig(cars[car_in_front_id].body, fill='yellow')
                    # tk.update()
                    # input("end it here 30")
                # if cars[car_id].current_lane == 30:
                #     print("find_current_end_step for lane 30")
                #     print("car_id: " + str(car_id) + " nt_lane: " + str(cars[car_id].next_lane))
                #     input("end it here 30")
    cars[car_id].current_end_step_tracker.append(cars[car_id].current_end_step)

def find_current_end_step_for_start_internal_lane(car_id,lanes_test,cars,Car): # find the step the car should move to in the current lane
    # if car_id == 51:
    #     print("51 through function ")
    #     input("51")
    for j in range(len(lanes_test[cars[car_id].current_lane].move_points)):
        cars[car_id].fut_pos.append(lanes_test[cars[car_id].current_lane].move_points[j])
    pos_in_queue = lanes_test[cars[car_id].current_lane].cars_in_lane_id.index(cars[car_id].id)
    offset_first = 4
    offset = 5
    cars[car_id].current_lane_end_step = (len(cars[car_id].fut_pos)) - offset_first
    if pos_in_queue == 0: # car at front
        # offset = int(half_car_length/move_val)
        # offset_first = 4
        # print("offset: " + str(offset))
        cars[car_id].current_end_step = (len(cars[car_id].fut_pos)) - offset_first
        # if car_id == 0:
        #     print("ran  pos_in_queue: " + str(pos_in_queue))
        #     print("current_end_step: " + str(cars[car_id].current_end_step))
        cars[car_id].end_step_for_current_lane = len(lanes_test[cars[car_id].current_lane].move_points) - offset_first
        cars[car_id].step_in_current_lane = cars[car_id].end_step_for_current_lane
        cars[car_id].front_queue_check = 1
        if lanes_test[cars[car_id].current_lane].next_lanes[0] == 9999:
            cars[car_id].current_end_step = (len(cars[car_id].fut_pos)) - 1
    else:
        # position of car in front
        offset = 5
        cars[car_id].current_end_step = (len(cars[car_id].fut_pos)) - (pos_in_queue * offset) - offset_first
        cars[car_id].end_step_for_current_lane = len(lanes_test[cars[car_id].current_lane].move_points) - (pos_in_queue * offset) - offset_first
        cars[car_id].step_in_current_lane = cars[car_id].end_step_for_current_lane

def find_updated_current_end_step(car_id,lanes_test,cars,Car): # find the step the car should move to in the current lane
    if cars[car_id].id not in lanes_test[cars[car_id].current_lane].cars_in_lane_id:
        print("car_id: " + str(car_id) + " cars[car_id].id: " + str(cars[car_id].id) + " cur_lane: " + str(cars[car_id].current_lane) + " car_in_lane_id: " + str(lanes_test[cars[car_id].current_lane].cars_in_lane_id))
        canvas.itemconfig(cars[car_id].body, fill='red')
        tk.update()
        input("car not in current_lane")
    pos_in_queue = lanes_test[cars[car_id].current_lane].cars_in_lane_id.index(cars[car_id].id)
    # cars[car_id].current_end_step = ((len(cars[car_id].fut_pos)) - (pos_in_queue * 5))  - 1
    offset_first = 4
    # cars[car_id].current_lane_end_step = (len(cars[car_id].fut_pos)) - offset_first
    if pos_in_queue == 0: # car at front
        cars[car_id].updated_current_end_step = (len(cars[car_id].fut_pos)) - offset_first
        cars[car_id].end_step_for_current_lane = len(lanes_test[cars[car_id].current_lane].move_points) - offset_first
        if lanes_test[cars[car_id].current_lane].next_lanes[0] == 9999:
            cars[car_id].updated_current_end_step = (len(cars[car_id].fut_pos)) - 1
            cars[car_id].end_step_for_current_lane = len(lanes_test[cars[car_id].current_lane].move_points) - 1

    else:
        # position of car in front
        offset = 5
        cars[car_id].updated_current_end_step = (len(cars[car_id].fut_pos)) - (pos_in_queue * offset) - offset_first

        if lanes_test[cars[car_id].current_lane].next_lanes[0] == 9999:
            cars[car_id].updated_current_end_step = (len(cars[car_id].fut_pos)) - 1
            cars[car_id].end_step_for_current_lane = (len(cars[car_id].fut_pos)) - 1
        # cars[car_id].current_end_step = ((len(cars[car_id].fut_pos)) - (pos_in_queue * 5))  - 1
        t = 1
        cars[car_id].end_step_for_current_lane = len(lanes_test[cars[car_id].current_lane].move_points) - (pos_in_queue * offset) - offset_first
    # if car_id == 89:
    #     print("first section updated_current_end_step: " + str(cars[car_id].updated_current_end_step))

    if pos_in_queue != 0:
        offset = 5
        # if (car_id == 308) or (car_id == 373) or (car_id == 425):
        #     print("     running find_updated_current_end_step car_id: " + str(car_id))
        #find current move_point of car in fornt
        car_in_front_id =  lanes_test[cars[car_id].current_lane].cars_in_lane_id[(pos_in_queue - 1)]
        car_in_front_move_point = cars[car_in_front_id].fut_pos[cars[car_in_front_id].step] # could change to .current_end_step
        car_in_front_move_point_current_end_step = cars[car_in_front_id].fut_pos[cars[car_in_front_id].current_end_step]
        # now find the index of car_in_front_move_point in cars[car_id].fut_pos
        if car_in_front_move_point in cars[car_id].fut_pos[cars[car_id].step:]: # in fut_pos between current step to the end
            start_looking_after_value = cars[car_id].step
            index_step_temp = cars[car_id].fut_pos.index(car_in_front_move_point,start_looking_after_value)
            cars[car_id].updated_current_end_step = index_step_temp - offset
            # if index_step_temp <= start_looking_after_value:
            #     print("car: " + str())
            # if car_id == 89:
            #     print("inside 1     section updated_current_end_step: " + str(cars[car_id].updated_current_end_step))
            #     print("car_in_front_id: " + str(car_in_front_id))
            #     print("car_in_front_move_point: " + str(car_in_front_move_point))
            #     print("start_looking_after_value: " + str(start_looking_after_value))
            #     print("index_step_temp: " + str(index_step_temp))
            if cars[car_id].updated_current_end_step < cars[car_id].current_end_step:
                cars[car_id].updated_current_end_step = cars[car_id].current_end_step
            # if car_id == 89:
            #     print("inside 2     section updated_current_end_step: " + str(cars[car_id].updated_current_end_step))
            #     print("car_in_front_id: " + str(car_in_front_id))
            #     print("car_in_front_move_point: " + str(car_in_front_move_point))
            #     print("start_looking_after_value: " + str(start_looking_after_value))
            #     print("index_step_temp: " + str(index_step_temp))

        else:
            # car in front passed the current_lane_end_step, could be that the car is taking a free turn but car_in_front is not
            cars[car_id].updated_current_end_step = cars[car_id].current_lane_end_step


def move_function_new(cars,lanes_test,Car,green_light_lanes):
    for i in cars_in_system:

        if cars[i].move_status == 3:
            # car is moving towards current end step so don't need to do anything
            t = 0
            cars[i].move_status = 3
            cars[i].move_status_tracker.append([cars[i].move_status,time_current,cars[i].step,cars[i].current_end_step,cars[i].current_lane_end_step])

        else:
            # update current_end_step
            find_updated_current_end_step(cars[i].id,lanes_test,cars,Car)
            # print("79update_cur_end_step: " + str(cars[79].updated_current_end_step) + " cur_end_step: " + str(cars[79].current_end_step))
            if cars[i].updated_current_end_step < cars[i].current_end_step:
                cars[i].updated_current_end_step = cars[i].current_end_step

            if cars[i].updated_current_end_step != cars[i].current_end_step:
                # update current_end_step
                # print("updated_current_end_step: " + str(cars[i].updated_current_end_step))
                # print("current_end_step: " + str(cars[i].current_end_step))
                if i == 326:
                    print("updated_current_end_step_326: " + str(cars[i].updated_current_end_step) + " current_end_step: " + str(cars[i].current_end_step))
                # if i == 51:
                #     print("updated_current_end_step_51: " + str(cars[i].updated_current_end_step) + " current_end_step: " + str(cars[i].current_end_step))
                #     print("51 updated")

                cars[i].current_end_step = cars[i].updated_current_end_step
                cars[car_id].current_end_step_tracker.append(cars[car_id].current_end_step)
                cars[i].move_status = 3
                cars[i].move_status_tracker.append([cars[i].move_status,time_current,cars[i].step,cars[i].current_end_step,cars[i].current_lane_end_step,cars[i].updated_current_end_step])
            else:
                cars[i].car_waiting_in_queue = 1  # ie. TRUE as car has joined a queue
                cars[i].car_moving = 0 # ie. FALSE as car has come to a temporary stop


        if cars[i].move_status == 3:
            if cars[i].step > cars[i].current_end_step:
                # if this continues to be an issue, current_end_step equal tp len(fut_pos) or somthing like that
                # canvas.itemconfig(cars[i].body, fill='red')
                # print("move_status_tracker: " + str(cars[i].move_status_tracker))
                print("i: " + str(i))
                print("cars[i].current_lane: " + str(cars[i].current_lane))
                print("curret_lane_map_id: " + str(lanes_test[cars[i].current_lane].map_lane_id))
                print("cars[i].next_lane: " + str(cars[i].next_lane))
                print("next_lane_map_id: " + str(lanes_test[cars[i].next_lane].map_lane_id))
                pos_in_queue_test = lanes_test[cars[i].current_lane].cars_in_lane_id.index(i)
                print("car_pos_in_queue: " + str(pos_in_queue_test))
                print("cars[i].step_tracker: " + str(cars[i].step_tracker))
                print("cars[i].step: " + str(cars[i].step))
                print("cars[i].step_in_current_lane: " + str(cars[i].step_in_current_lane))
                print("cars[i].current_end_step: "+ str(cars[i].current_end_step))
                print("cars[i].current_end_step_tracker: "+ str(cars[i].current_end_step_tracker))
                print("cars[i].current_lane_end_step: " + str(cars[i].current_lane_end_step))
                print("cars[i].end_step_for_current_lane: " + str(cars[i].end_step_for_current_lane))
                print("curre_lane: " + str(cars[i].current_lane) + " next_lane: " + str(cars[i].next_lane))
                print("len(cars[i].fut_pos): " + str(len(cars[i].fut_pos)))

                print("car_in_lane_id: " + str(lanes_test[cars[i].current_lane].cars_in_lane_id))

                car_in_front = lanes_test[cars[i].current_lane].cars_in_lane_id[(pos_in_queue_test - 1)]
                print("car_in_front: " + str(car_in_front))
                print("cars[car_in_front].current_lane: " + str(cars[car_in_front].current_lane))
                print("curret_lane_map_id: " + str(lanes_test[cars[car_in_front].current_lane].map_lane_id))
                print("cars[car_in_front].next_lane: " + str(cars[car_in_front].next_lane))
                print("next_lane_map_id: " + str(lanes_test[cars[car_in_front].next_lane].map_lane_id))
                pos_in_queue_test = lanes_test[cars[car_in_front].current_lane].cars_in_lane_id.index(car_in_front)
                print("car_pos_in_queue: " + str(pos_in_queue_test))
                print("cars[car_in_front].step_tracker: " + str(cars[car_in_front].step_tracker))
                print("cars[car_in_front].step: " + str(cars[car_in_front].step))
                print("cars[car_in_front].step_in_current_lane: " + str(cars[car_in_front].step_in_current_lane))
                print("cars[car_in_front].current_end_step: "+ str(cars[car_in_front].current_end_step))
                print("cars[car_in_front].current_end_step_tracker: "+ str(cars[car_in_front].current_end_step_tracker))
                print("cars[car_in_front].current_lane_end_step: " + str(cars[car_in_front].current_lane_end_step))
                print("cars[car_in_front].end_step_for_current_lane: " + str(cars[car_in_front].end_step_for_current_lane))
                print("curre_lane: " + str(cars[car_in_front].current_lane) + " next_lane: " + str(cars[car_in_front].next_lane))
                print("len(cars[car_in_front].fut_pos): " + str(len(cars[car_in_front].fut_pos)))


                canvas.itemconfig(cars[i].body, fill='red')
                canvas.itemconfig(cars[car_in_front].body, fill='yellow')
                tk.update()
                input("Please press enter to continue...")
            # check to see if current step is equal to current_end_step
            if cars[i].step < cars[i].current_end_step:
                # keep move_sataus the same, car still in process of moving to new position
                cars[i].move_status = 3
                cars[i].move_status_tracker.append([cars[i].move_status,time_current,cars[i].step,cars[i].current_end_step,cars[i].current_lane_end_step])
            elif cars[i].step == cars[i].current_end_step:
                # set move_ stauts = 0, which will check if in a green_light_lane and at front of queue
                # car reached its temporary end step
                # cars[i].car_waiting_in_queue = 1  # ie. TRUE as car has joined a queue
                # cars[i].car_moving = 0 # ie. FALSE as car has come to a temporary stop
                cars[i].move_status = 0
                cars[i].move_status_tracker.append([cars[i].move_status,time_current,cars[i].step,cars[i].current_end_step,cars[i].current_lane_end_step])
            # elif cars[i].current_lane in green_light_lanes:
            #     # check to see if car is moving/ approacin the end of the queue in a lane which now has a green light
            #     cars[i].move_status = 1
            #     cars[i].move_status_tracker.append([cars[i].move_status,time_current,cars[i].step,cars[i].current_end_step,cars[i].current_lane_end_step])

        if cars[i].move_status == 0:
            # we know car has reached the its current_end_step
            # check to see if car is at end of exit lane
            if lanes_test[cars[i].current_lane].next_lanes[0] == 9999:
                # car has left exit lane
                # remove car from system
                cars_in_system.remove(i)
                cars[i].car_in_system = 0
                # set all time checker parameters to zero
                cars[i].car_moving = 0
                cars[i].car_waiting_in_queue = 0
                cars[i].car_waiting_to_enter_system = 0
                # remove car from exot (current) lane
                lanes_test[cars[i].current_lane].cars_in_lane_id.remove(i)
                #
            # check to see if the car is moving into free_turn_next_lane so current_lane doesn't need to be in green_light_lanes
            elif cars[i].next_lane in lanes_test[cars[i].current_lane].free_turn_next_lanes:
                # if cars[i].step == cars[i].current_lane_end_step: # this will confirm if the car is at the correct pointin current_lane to move to next_lane
                # check if there is space for car to move into next_lane
                pos_in_queue = lanes_test[cars[i].current_lane].cars_in_lane_id.index(i)
                if cars[i].step == cars[i].current_lane_end_step:
                # if cars[i].step == cars[i].current_end_step:   ###### here now
                    cars[i].move_status = 0 # initially assume car can't move (not enough space)
                    cars[i].move_status_tracker.append([cars[i].move_status,time_current,cars[i].step,cars[i].current_end_step,cars[i].current_lane_end_step])
                    #### assign cars next lane
                    if cars[i].next_lane in lanes_test[cars[i].current_lane].next_lanes: # car already has a next_lane
                        t = 1
                    else:
                        t = 0
                    #### check for space for the car to move into the next lane
                    space_check = 0 # initially assume there is NoT enough space for the car
                    # if car entering an exit lane there will always be space
                    if lanes_test[cars[i].next_lane].next_lanes[0] == 9999:
                        # car can enter next_lane
                        cars[i].move_status = 2
                        cars[i].move_status_tracker.append([cars[i].move_status,time_current,cars[i].step,cars[i].current_end_step,cars[i].current_lane_end_step])
                    # need more than 5 steps of space in the next lane, ie. need more than 5 move_points
                    # if car is entering a lane that is currently empty, there will obviously be space
                    elif len(lanes_test[cars[i].next_lane].cars_in_lane_id) == 0:
                        # car can enter next_lane
                        space_check = 1
                        cars[i].move_status = 2
                        cars[i].move_status_tracker.append([cars[i].move_status,time_current,cars[i].step,cars[i].current_end_step,cars[i].current_lane_end_step])
                    # all other cases check to see if there enough space in the next_lane
                    else:
                        # can the lane fit another car?
                        ## add here
                        car_id_back_of_queue_in_next_lane = lanes_test[cars[i].next_lane].cars_in_lane_id[-1]
                        # car_id_back_of_queue_in_next_lane_step = cars[car_id_back_of_queue_in_next_lane].step
                        # car_id_back_of_queue_in_next_lane_current_move_point = cars[car_id_back_of_queue_in_next_lane].fut_pos[cars[car_id_back_of_queue_in_next_lane].step]
                        car_id_back_of_queue_in_next_lane_step_current_end_step = cars[car_id_back_of_queue_in_next_lane].current_end_step
                        car_id_back_of_queue_in_next_lane_current_move_point = cars[car_id_back_of_queue_in_next_lane].fut_pos[car_id_back_of_queue_in_next_lane_step_current_end_step]
                        if car_id_back_of_queue_in_next_lane_current_move_point in lanes_test[cars[i].next_lane].move_points:
                            index_car_at_back_move_point_in_lane_move_point = lanes_test[cars[i].next_lane].move_points.index(car_id_back_of_queue_in_next_lane_current_move_point)
                            offset = 5
                            if index_car_at_back_move_point_in_lane_move_point > offset:
                                # room of next car to enter
                                space_check = 1 # not enough space so set space_check = 0
                                # car can enter next_lane
                                cars[i].move_status = 2
                                cars[i].move_status_tracker.append([cars[i].move_status,time_current,cars[i].step,cars[i].current_end_step,cars[i].current_lane_end_step])



                        # lane_length = len(lanes_test[cars[i].next_lane].move_points)
                        # num_cars_in_next_lane = len(lanes_test[cars[i].next_lane].cars_in_lane_id)
                        # pos_in_queue = num_cars_in_next_lane + 1
                        # # assume each car needs/occupies 5 move_vals
                        # if (pos_in_queue * 5) < lane_length: # there IS enough space
                        # # if pos_in_queue < 5:
                        #     space_check = 1 # not enough space so set space_check = 0
                        #     # car can enter next_lane
                        #     cars[i].move_status = 2
                        #     cars[i].move_status_tracker.append([cars[i].move_status,time_current,cars[i].step,cars[i].current_end_step,cars[i].current_lane_end_step])

            # check if car in a green light lane, then check position of car in lane
            elif cars[i].current_lane in green_light_lanes:
                cars[i].move_status = 1
                cars[i].move_status_tracker.append([cars[i].move_status,time_current,cars[i].step,cars[i].current_end_step,cars[i].current_lane_end_step])
                # check to see if car at first in lane, not necessarily at the end point of lane
                pos_in_queue = lanes_test[cars[i].current_lane].cars_in_lane_id.index(i)
                if cars[i].step == cars[i].current_lane_end_step: # this will confirm if the car is that the front position of the lane
                # if pos_in_queue == 0:
                    cars[i].move_status = 0 # initially assume car can't move (not enough space)
                    cars[i].move_status_tracker.append([cars[i].move_status,time_current,cars[i].step,cars[i].current_end_step,cars[i].current_lane_end_step])
                    #### assign cars next lane
                    if cars[i].next_lane in lanes_test[cars[i].current_lane].next_lanes: # car already has a next_lane
                        t = 1
                    else:
                        t = 0
                        # cars[i].next_lane = random.choice(lanes_test[cars[i].current_lane].next_lanes)   ##### changes this in the future
                    #### check for space for the car to move into the next lane
                    space_check = 0 # initially assume there is NOT enough space for the car
                    # if car entering an exit lane there will always be space
                    if lanes_test[cars[i].next_lane].next_lanes[0] == 9999:
                        # car can enter next_lane
                        cars[i].move_status = 2
                        cars[i].move_status_tracker.append([cars[i].move_status,time_current,cars[i].step,cars[i].current_end_step,cars[i].current_lane_end_step])
                    # need more than 5 steps of space in the next lane, ie. need more than 5 move_points
                    # if car is entering a lane that is currently empty, there will obviously be space
                    elif len(lanes_test[cars[i].next_lane].cars_in_lane_id) == 0:
                        # car can enter next_lane
                        space_check = 1
                        cars[i].move_status = 2
                        cars[i].move_status_tracker.append([cars[i].move_status,time_current,cars[i].step,cars[i].current_end_step,cars[i].current_lane_end_step])
                    # all other cases check to see if there enough space in the next_lane
                    else:
                        # can the lane fit another car?
                        ##### add here
                        car_id_back_of_queue_in_next_lane = lanes_test[cars[i].next_lane].cars_in_lane_id[-1]
                        # car_id_back_of_queue_in_next_lane_step = cars[car_id_back_of_queue_in_next_lane].step
                        # car_id_back_of_queue_in_next_lane_current_move_point = cars[car_id_back_of_queue_in_next_lane].fut_pos[cars[car_id_back_of_queue_in_next_lane].step]
                        car_id_back_of_queue_in_next_lane_step_current_end_step = cars[car_id_back_of_queue_in_next_lane].current_end_step
                        car_id_back_of_queue_in_next_lane_current_move_point = cars[car_id_back_of_queue_in_next_lane].fut_pos[car_id_back_of_queue_in_next_lane_step_current_end_step]
                        if car_id_back_of_queue_in_next_lane_current_move_point in lanes_test[cars[i].next_lane].move_points:
                            index_car_at_back_move_point_in_lane_move_point = lanes_test[cars[i].next_lane].move_points.index(car_id_back_of_queue_in_next_lane_current_move_point)
                            offset = 5
                            if index_car_at_back_move_point_in_lane_move_point > offset:
                                # room of next car to enter
                                space_check = 1 # not enough space so set space_check = 0
                                # car can enter next_lane
                                cars[i].move_status = 2
                                cars[i].move_status_tracker.append([cars[i].move_status,time_current,cars[i].step,cars[i].current_end_step,cars[i].current_lane_end_step])

                        # lane_length = len(lanes_test[cars[i].next_lane].move_points)
                        # num_cars_in_next_lane = len(lanes_test[cars[i].next_lane].cars_in_lane_id)
                        # pos_in_queue = num_cars_in_next_lane + 1
                        # # assume each car needs/occupies 5 move_vals
                        # if (pos_in_queue * 5) < lane_length: # there IS enough space
                        # # if pos_in_queue < 5:
                        #     space_check = 1 # not enough space so set space_check = 0
                        #     # car can enter next_lane
                        #     cars[i].move_status = 2
                        #     cars[i].move_status_tracker.append([cars[i].move_status,time_current,cars[i].step,cars[i].current_end_step,cars[i].current_lane_end_step])
            #check if the queue has moved forward since the car entered and starting moving towards current_end_step ie. does current_end_step need to be updated


        if cars[i].move_status == 2:
            # we know at this point that the car is going to change lane, so need to find fut_pos transition points,
            # and need to find fut_pos move_points for next_lane and the a end_step
            cars[i].car_waiting_in_queue = 0  # ie. FALSE
            cars[i].car_moving = 1 # ie. TRUE
            # find fut_pos for transition to next lane
            fut_pos_change_lane(cars[i].id,lanes_test,cars,Car)
            # should leave curent_lane here and enter next_lane
            lanes_test[cars[i].current_lane].cars_in_lane_id.remove(i)
            lanes_test[cars[i].next_lane].cars_in_lane_id.append(i)
            # cars[i].current_lane = cars[i].next_lane
            cars[i].path_step += 1
            cars[i].current_lane = cars[i].path[cars[i].path_step]
            cars[i].step_in_current_lane = 0
            cars[i].next_lane = []
            #### assign cars next lane
            if cars[i].next_lane in lanes_test[cars[i].current_lane].next_lanes: # car already has a next_lane
                t = 1
            else:
                t = 0
                # cars[i].next_lane = random.choice(lanes_test[cars[i].current_lane].next_lanes)   ##### changes this in the future
                # print("path: " + str(cars[i].path))
                # print("i: " + str(i) + " cur_lane: " + str(cars[i].current_lane) + " path_step: " + str(cars[i].path_step))
                cars[i].next_lane = cars[i].path[(cars[i].path_step + 1)]
                # cars[i].next_lane = cars[i].path[(cars[i].path_step)] # line 2175 the cars[i].path_step += 1
            # find fut_pos in new current_lane
            fut_pos_current_lane(cars[i].id,lanes_test,cars,Car)
            # find current end_step
            find_current_end_step(cars[i].id,lanes_test,cars,Car)
            # set move_status = 3, so the car will move a step forward
            cars[i].move_status = 3
            cars[i].move_status_tracker.append([cars[i].move_status,time_current,cars[i].step,cars[i].current_end_step,cars[i].current_lane_end_step])

        if cars[i].move_status == 1:
            # we know car is in a lane with a green light BUT it is not at the front of the queue
            # so most update the end_step as cars in front be moving and hence this car's end step will need to change to keep up with cars in front
            ####
            # find_current_end_step(cars[i].id,lanes_test,cars,Car)
            # # set move_status = 3, so the car will move a step forward
            # cars[i].move_status = 3
            # cars[i].move_status_tracker.append([cars[i].move_status,time_current,cars[i].step,cars[i].current_end_step,cars[i].current_lane_end_step])
            ####
            find_updated_current_end_step(cars[i].id,lanes_test,cars,Car)
            if cars[i].updated_current_end_step != cars[i].current_end_step:
                # update current_end_step
                # print("updated_current_end_step2: " + str(cars[i].updated_current_end_step))
                # print("current_end_step2: " + str(cars[i].current_end_step))
                if i == 326:
                    print("updated_current_end_step_326: " + str(cars[i].updated_current_end_step) + " current_end_step: " + str(cars[i].current_end_step))
                if cars[i].updated_current_end_step < cars[i].current_end_step:
                    print("updated lower car: " + str(i) + " updated_current_end_step: " + str(cars[i].updated_current_end_step) + " current_end_step: " + str(cars[i].current_end_step))
                    print("car_current_lane: " + str(cars[i].current_lane) + " next_lane: " + str(cars[i].next_lane))
                else:
                    cars[i].current_end_step = cars[i].updated_current_end_step
                    cars[i].current_end_step_tracker.append(cars[i].current_end_step)
                    cars[i].move_status = 3
                    cars[i].move_status_tracker.append([cars[i].move_status,time_current,cars[i].step,cars[i].current_end_step,cars[i].current_lane_end_step])
            ####

        if cars[i].move_status == 3:
            # we know car is not at its current_end_step, so move car forward one step and draw new position
            # print("i: " + str(i))
            # print("cars[i].step: " + str(cars[i].step))
            # print("cars[i].current_end_step: "+ str(cars[i].current_end_step))
            # print("len(cars[i].fut_pos): " + str(len(cars[i].fut_pos)))
            cars[i].step += 1
            cars[i].step_tracker.append(cars[i].step)
            cars[i].step_in_current_lane += 1
            cars[i].pos_x = cars[i].fut_pos[cars[i].step][0]
            cars[i].pos_y = cars[i].fut_pos[cars[i].step][1]
            cars[i].angle = cars[i].fut_pos[cars[i].step][2]
            # draw car
            Car.car_on_angle(cars[i],cars[i].pos_x,cars[i].pos_y,car_width,car_length,cars[i].angle)
def car_entering_function(cars,lanes_test,Car,car_id,cars_in_system,cars_entered_system,cars_intending_to_enter,cars_to_wait_this_iter,cars_entering_this_iter):
    # space_check = 1 # initially assume there is sapce for the car/ previous car has moved forward enough in lane for new car to enter
    space_check = 0 # initially assume there is NO space for the car intending to enter
    car_intended_entry_lane = cars[car_id].current_lane
    if len(lanes_test[car_intended_entry_lane].cars_in_lane_id) == 0: # guaranteed space in the lane
        space_check = 1

    # need more than 5 steps of space in the entry lane, ie. need more than 5 move_points
    if len(lanes_test[car_intended_entry_lane].cars_in_lane_id) > 0: # ie. there are cars in the intended lane
        car_in_front = lanes_test[car_intended_entry_lane].cars_in_lane_id[-1]
        # print("cars[car_in_front].pos_x: " + str(cars[car_in_front].pos_x) + " cars[car_in_front].pos_y: " + str(cars[car_in_front].pos_y) + " cars[car_in_front].angle: " + str(cars[car_in_front].angle))
        # print("lanes_test[car_intended_entry_lane].move_points: " + str(lanes_test[car_intended_entry_lane].move_points))
        # print("lane: " + str(car_intended_entry_lane) + " cars_in_lane: " + str(lanes_test[car_intended_entry_lane].cars_in_lane_id))
        # print("map_lane: " + str(lanes_test[car_intended_entry_lane].map_lane_id))
        # print("car_id: " + str(car_id) + " car_in_front: " + str(car_in_front))
        # print("car_in_fron cut_lane: " + str(cars[car_in_front].current_lane))
        # car_in_front_index = lanes_test[car_intended_entry_lane].move_points.index([cars[car_in_front].pos_x,cars[car_in_front].pos_y,cars[car_in_front].angle])
        car_in_front_index = lanes_test[car_intended_entry_lane].cars_in_lane_id.index(car_in_front) # changed to this from the above
        # print("car_in_front_index: " + str(car_in_front_index))

        lane_length = len(lanes_test[car_intended_entry_lane].move_points)
        num_cars_in_intended_lane = len(lanes_test[car_intended_entry_lane].cars_in_lane_id)
        pos_in_queue = num_cars_in_intended_lane + 1

        #####
        # can the lane fit another car?
        ## add here
        car_id_back_of_queue_in_next_lane = lanes_test[car_intended_entry_lane].cars_in_lane_id[-1]
        # car_id_back_of_queue_in_next_lane_step = cars[car_id_back_of_queue_in_next_lane].step
        # car_id_back_of_queue_in_next_lane_current_move_point = cars[car_id_back_of_queue_in_next_lane].fut_pos[cars[car_id_back_of_queue_in_next_lane].step]
        car_id_back_of_queue_in_next_lane_step_current_end_step = cars[car_id_back_of_queue_in_next_lane].current_end_step
        car_id_back_of_queue_in_next_lane_current_move_point = cars[car_id_back_of_queue_in_next_lane].fut_pos[car_id_back_of_queue_in_next_lane_step_current_end_step]
        if car_id_back_of_queue_in_next_lane_current_move_point in lanes_test[car_intended_entry_lane].move_points:
            index_car_at_back_move_point_in_lane_move_point = lanes_test[car_intended_entry_lane].move_points.index(car_id_back_of_queue_in_next_lane_current_move_point)
            offset = 5
            if index_car_at_back_move_point_in_lane_move_point > offset:
                # room of next car to enter
                space_check = 1 # not enough space so set space_check = 0
                # car can enter next_lane
        #####


        ############
        # # assume each car needs/occupies 5 move_vals
        # if (pos_in_queue * 5) > lane_length: # there IS NOT enough space
        # # if car_in_front_index > 6: # there is NO space of the car to enter the next_lane
        #     # print("cars_in_lane_id: " + str(lanes_test[car_intended_entry_lane].cars_in_lane_id))
        #     # print("car_id: " + str(car_id) + " car_in_front: " + str(car_in_front))
        #     # print("cars[car_in_front].pos_x: " + str(cars[car_in_front].pos_x) + " cars[car_in_front].pos_y: " + str(cars[car_in_front].pos_y) + " cars[car_in_front].angle: " + str(cars[car_in_front].angle))
        #     # car will not enter system this iteration and car will remain in cars_to_enter list
        #     cars[car_id].move_status = 0
        #     space_check = 0 # not enough space so set space_check = 0
        #     cars_to_wait_this_iter.append(car_id)
        #     # print("no_space_car_id: " + str(car_id) + "intended_lane: " + str(car_intended_entry_lane))
        ###############
    if space_check == 0:
        cars[car_id].move_status = 0
        space_check = 0 # not enough space so set space_check = 0
        cars_to_wait_this_iter.append(car_id)

    if space_check == 1: # space for car to enter into system
        cars_in_system.append(car_id)
        cars[car_id].car_in_system = 1
        cars[car_id].car_waiting_to_enter_system = 0
        cars_entered_system.append(car_id)
        cars_entering_this_iter.append(car_id)
        # add car to cars_in_lane_id store
        lanes_test[cars[car_id].current_lane].cars_in_lane_id.append(cars[car_id].id)
        # remove car from list of cars_intending_to_enter
        # temp_cars_intending_to_enter.remove(car_id)
        # find fut_pos for car
        fut_pos_current_lane(cars[car_id].id,lanes_test,cars,Car)
        # find current end step
        if (cars[car_id].current_lane == cars[car_id].path[0]) and (cars[car_id].current_lane not in entry_lanes): # car is going to start in an internal lane
            find_current_end_step_for_start_internal_lane(car_id,lanes_test,cars,Car)
        else:
            find_current_end_step(cars[car_id].id,lanes_test,cars,Car)
        # if car_id == 0:
        #     print("ran 3 current_end_step: " + str(cars[car_id].current_end_step))
        if cars[car_id].current_lane not in entry_lanes: # the car is starting in an internal lane
            # print("run")
            # set move_status to 1
            cars[car_id].move_status = 3
            cars[car_id].step = cars[car_id].current_end_step - 1
            # print("step: " + str(cars[car_id].step))
            cars[car_id].pos_x = cars[car_id].fut_pos[cars[car_id].step][0]
            cars[car_id].pos_y = cars[car_id].fut_pos[cars[car_id].step][1]
            cars[car_id].angle = cars[car_id].fut_pos[cars[car_id].step][2]
            # print("pos_x: " + str(cars[car_id].pos_x) + " pos_y: " + str(cars[car_id].pos_y) )
        else: # car is starting in an entry lane
            # print("not run")
            # set move_status to 3
            cars[car_id].move_status = 3
            # cars[car_id].step += 1
            cars[car_id].pos_x = cars[car_id].fut_pos[cars[car_id].step][0]
            cars[car_id].pos_y = cars[car_id].fut_pos[cars[car_id].step][1]
            cars[car_id].angle = cars[car_id].fut_pos[cars[car_id].step][2]
def light_control_function(juncs_test,lanes_test,green_light_lanes,time_interval,red_light_lanes_pause_temp):
    # red_light_lanes_pause_temp = []
    for t in range(len(lanes_test)):
        if (lanes_test[t].green_light == 1) and (t not in green_light_lanes):
            green_light_lanes.append(t)
            turn_light_green(t)

            for p in range(len(juncs_test)):
                if t in juncs_test[p].light_lanes_at_junc:
                    juncs_test[p].lane_at_junc_green = t
    # if 33 in green_light_lanes:
    #     print("33 " + " green_light_lanes: " + str(green_light_lanes))
    green_light_lanes_temp = green_light_lanes
    for k in green_light_lanes:
        # print("checking_1")
        if lanes_test[k].time_green <= 0: # ie one of the lights has run out of time
            # check if associated lane is also has time.green = 0
            turn_light_red(k)
            lanes_test[k].green_light = 0
            green_light_lanes_temp.remove(k)
            lanes_test[k].light_time_pause = 0.5 #time_interval * 12
            red_light_lanes_pause_temp.append(k)
            # print("checking_2")

    # print("rrl :"  + str(red_light_lanes_pause_temp))
    red_light_lanes_pause = red_light_lanes_pause_temp
    # print("new_loop")
    # print("red_light_lanes_pause: " + str(red_light_lanes_pause))
    for k in red_light_lanes_pause:
        # print("rrl :"  + str(red_light_lanes_pause_temp))
        # print("rrl_t :"  + str(lanes_test[k].light_time_pause))
        if lanes_test[k].light_time_pause <= 0:  # red light pause has finshed and now llok for a new lane to turn green at the junction
            # print("checking_3")
            red_light_lanes_pause_temp.remove(k)
            lanes_test[k].light_time_pause = 0

            # find the next lane in the junction to turn green, by triggering the thread
            for t in range(len(juncs_test)):
                if k in juncs_test[t].light_lanes_at_junc:
                    juncs_test[t].ready_for_green = 1 # junction all reds and pause finsihed so so turn on (set to 1) ready_for_green, which will trigger the thread to act on this junction
            # print("ready for green")

    red_light_lanes_pause = red_light_lanes_pause_temp
    green_light_lanes = green_light_lanes_temp

    for k in green_light_lanes:
        lanes_test[k].time_green -= time_interval # new time step so subtract the time_interval
        # print("time_green: " + str(lanes_test[k].time_green))

    for k in red_light_lanes_pause:
        lanes_test[k].light_time_pause -= time_interval # new time step so subtract the time_interval

def find_potential_lane_1_angle_method(cars,lanes_test,car_id):
    cars[car_id].potential_lanes_1 = []
    potential_lane_temp = []
    potential_lane_line_temp = []
    for i in range(len(lanes_test)):
        # now loop thorugh all the lines in the lane
        num_lines_in_lane = len(lanes_test[i].points_with_angles) - 1
        for j in range(num_lines_in_lane):
            line_point_1_x = lanes_test[i].points_with_angles[j][0]
            line_point_1_y = lanes_test[i].points_with_angles[j][1]
            line_point_2_x = lanes_test[i].points_with_angles[j + 1][0]
            line_point_2_y = lanes_test[i].points_with_angles[j + 1][1]
            line_angle = lanes_test[i].points_with_angles[j][2]

            gps_line_angle = line_angle - (math.pi/2)
            gps_point_1_x = cars[car_id].coords[0]
            gps_point_1_y = cars[car_id].coords[1]
            gps_point_2_x = gps_point_1_x + rad_gps*math.sin(gps_line_angle)
            gps_point_2_y = gps_point_1_y - rad_gps*math.cos(gps_line_angle)
            #####
            line_in_lane = [[line_point_1_x,line_point_1_y],[line_point_2_x,line_point_2_y]]
            gps_line = [[gps_point_1_x,gps_point_1_y],[gps_point_2_x,gps_point_2_y]]
            # find point of interssection between lane lane and gps_line
            point_of_intersection = find_intersection_point_between_lines(line_in_lane,gps_line)
            # print("lane_line: " + str([i,j]))
            # print("point_of_intersection: " + str(point_of_intersection))

            # find distance between point_of_intersection and the gps coord
            dist = math.sqrt(((gps_point_1_y - point_of_intersection[1])**2) + ((gps_point_1_x - point_of_intersection[0])**2))
            # check if distance less than or equal to rad_gps
            if dist <= rad_gps:
                # check if point_of_intersection lies on the lane line
                # print("dist_criteria: " + str([i,j]))
                # print("point_of_intersection: " + str(point_of_intersection))
                # canvas.create_oval(point_of_intersection[0] - 3,point_of_intersection[1] - 3,point_of_intersection[0] + 3, point_of_intersection[1] + 3, fill = 'red')
                # tk.update()
                # input("press enter 1... ")
                length_of_lane_line = math.sqrt(((line_point_2_y - line_point_1_y)**2) + ((line_point_2_x - line_point_1_x)**2))
                length_of_lane_line_margin = length_of_lane_line + rad_gps #+ rad_gps
                dist_point_intersection_and_line_point_1 = math.sqrt(((line_point_1_y - point_of_intersection[1])**2) + ((line_point_1_x - point_of_intersection[0])**2))
                dist_point_intersection_and_line_point_2 = math.sqrt(((line_point_2_y - point_of_intersection[1])**2) + ((line_point_2_x - point_of_intersection[0])**2))

                tot_dist_with_point_of_intersection = dist_point_intersection_and_line_point_1 + dist_point_intersection_and_line_point_2

                # print("length_of_lane_line_margin: " + str(length_of_lane_line_margin))
                # print("dist_point_intersection_and_line_point_1: " +str(dist_point_intersection_and_line_point_1))
                # print("dist_point_intersection_and_line_point_2: " +str(dist_point_intersection_and_line_point_2))
                # print("tot_dist_with_point_of_intersection: " + str(tot_dist_with_point_of_intersection))
                # input("press enter 2...")
                # check if distance from line points to the point of intersceiton are with the margin for the length between the line points
                if tot_dist_with_point_of_intersection <= length_of_lane_line_margin:
                    # add rad_gps to this
                    # this confirms that the coord could be provided by a car of this line in lane
                    # add this lane and lane's line to potenial_lanes
                    potential_lane_temp.append(i)
                    potential_lane_line_temp.append([i,j,point_of_intersection])
                    # potential_lane_line_temp.append(point_of_intersection)
    temp_2 = []
    for val in potential_lane_temp:  # to remove duplicates in the potential lane list
           if val not in temp_2:
              temp_2.append(val)
    potential_lane_temp = temp_2
    ###
    temp_3 = []
    for val_line in potential_lane_line_temp:  # to remove duplicates in the potential lane list
           if val_line not in temp_3:
              temp_3.append(val_line)
    potential_lane_line_temp = temp_3
    ###
    # set the variables in the new class
    cars[car_id].potential_lanes_1 = potential_lane_temp
    cars[car_id].potential_lanes_lines_1 = potential_lane_line_temp
def find_potential_lane_2_angle_method(cars,lanes_test,car_id):
    cars[car_id].potential_lanes_2= []
    potential_lane_temp = []
    potential_lane_line_temp = []
    for i in range(len(lanes_test)):
        # now loop thorugh all the lines in the lane
        num_lines_in_lane = len(lanes_test[i].points_with_angles) - 1
        for j in range(num_lines_in_lane):
            line_point_1_x = lanes_test[i].points_with_angles[j][0]
            line_point_1_y = lanes_test[i].points_with_angles[j][1]
            line_point_2_x = lanes_test[i].points_with_angles[j + 1][0]
            line_point_2_y = lanes_test[i].points_with_angles[j + 1][1]
            line_angle = lanes_test[i].points_with_angles[j][2]

            gps_line_angle = line_angle - (math.pi/2)
            gps_point_1_x = cars[car_id].coords[0]
            gps_point_1_y = cars[car_id].coords[1]
            gps_point_2_x = gps_point_1_x + rad_gps*math.sin(gps_line_angle)
            gps_point_2_y = gps_point_1_y - rad_gps*math.cos(gps_line_angle)
            #####
            line_in_lane = [[line_point_1_x,line_point_1_y],[line_point_2_x,line_point_2_y]]
            gps_line = [[gps_point_1_x,gps_point_1_y],[gps_point_2_x,gps_point_2_y]]
            # find point of interssection between lane lane and gps_line
            point_of_intersection = find_intersection_point_between_lines(line_in_lane,gps_line)
            # print("lane_line: " + str([i,j]))
            # print("point_of_intersection: " + str(point_of_intersection))

            # find distance between point_of_intersection and the gps coord
            dist = math.sqrt(((gps_point_1_y - point_of_intersection[1])**2) + ((gps_point_1_x - point_of_intersection[0])**2))
            # check if distance less than or equal to rad_gps
            if dist <= rad_gps:
                # check if point_of_intersection lies on the lane line
                # print("dist_criteria: " + str([i,j]))
                # print("point_of_intersection: " + str(point_of_intersection))
                # canvas.create_oval(point_of_intersection[0] - 3,point_of_intersection[1] - 3,point_of_intersection[0] + 3, point_of_intersection[1] + 3, fill = 'green')
                # tk.update()
                # input("press enter 1... ")
                length_of_lane_line = math.sqrt(((line_point_2_y - line_point_1_y)**2) + ((line_point_2_x - line_point_1_x)**2))
                length_of_lane_line_margin = length_of_lane_line + rad_gps #+ rad_gps
                dist_point_intersection_and_line_point_1 = math.sqrt(((line_point_1_y - point_of_intersection[1])**2) + ((line_point_1_x - point_of_intersection[0])**2))
                dist_point_intersection_and_line_point_2 = math.sqrt(((line_point_2_y - point_of_intersection[1])**2) + ((line_point_2_x - point_of_intersection[0])**2))

                tot_dist_with_point_of_intersection = dist_point_intersection_and_line_point_1 + dist_point_intersection_and_line_point_2

                # print("length_of_lane_line_margin: " + str(length_of_lane_line_margin))
                # print("dist_point_intersection_and_line_point_1: " +str(dist_point_intersection_and_line_point_1))
                # print("dist_point_intersection_and_line_point_2: " +str(dist_point_intersection_and_line_point_2))
                # print("tot_dist_with_point_of_intersection: " + str(tot_dist_with_point_of_intersection))
                # input("press enter 2...")
                # check if distance from line points to the point of intersceiton are with the margin for the length between the line points
                if tot_dist_with_point_of_intersection <= length_of_lane_line_margin:
                    # add rad_gps to this
                    # this confirms that the coord could be provided by a car of this line in lane
                    # add this lane and lane's line to potenial_lanes
                    potential_lane_temp.append(i)
                    potential_lane_line_temp.append([i,j,point_of_intersection])
                    # potential_lane_line_temp.append(point_of_intersection)
    temp_2 = []
    for val in potential_lane_temp:  # to remove duplicates in the potential lane list
           if val not in temp_2:
              temp_2.append(val)
    potential_lane_temp = temp_2
    ###
    temp_3 = []
    for val_line in potential_lane_line_temp:  # to remove duplicates in the potential lane list
           if val_line not in temp_3:
              temp_3.append(val_line)
    potential_lane_line_temp = temp_3
    ###
    # set the variables in the new class
    cars[car_id].potential_lanes_2 = potential_lane_temp
    cars[car_id].potential_lanes_lines_2 = potential_lane_line_temp
def find_dist_to_lane_points_method_potential_lane_1(cars,lanes_test,car_id,rad_gps):
    cars[car_id].dist_lane_forward_points_1 = []
    for q in range(len(cars[car_id].potential_lanes_lines_1)):
        lane_of_int = cars[car_id].potential_lanes_lines_1[q][0]
        line_of_int = cars[car_id].potential_lanes_lines_1[q][1]
        point_of_intersection = cars[car_id].potential_lanes_lines_1[q][2]

        # print("line_of_int: " +str(line_of_int))
        first_point_of_int_index = line_of_int + 1  # this give the point at the end of the line_of_int
        num_of_points_in_lane = len(lanes_test[lane_of_int].points_with_angles)
        # print("first_point_of_int_index: " + str(first_point_of_int_index))
        # print("num_of_points_in_lane: " + str(num_of_points_in_lane))
        # input("press 3")
        temp_dist_lane_forward_points_1 = []
        temp_dist_lane_forward_points_1.append(lane_of_int)

        for k in range(first_point_of_int_index , num_of_points_in_lane): # loop through the first point and all points to the end of lane
            # print("runngins")
            point_index = k
            temp_lane_line_point = lanes_test[lane_of_int].points_with_angles[k][0:2]
            # print("temp_lane_line_point: " + str(temp_lane_line_point))
            # canvas.create_oval(temp_lane_line_point[0] - 2, temp_lane_line_point[1] - 2,temp_lane_line_point[0] + 2,temp_lane_line_point[1] + 2, fill = 'yellow')
            # tk.update()
            dist_to_point = math.sqrt(((temp_lane_line_point[1] - point_of_intersection[1])**2) + ((temp_lane_line_point[0] - point_of_intersection[0])**2))
            # temp_dist_lane_forward_points_1.append(lane_of_int)
            # temp_dist_lane_forward_points_1.append(line_of_int)
            # temp_dist_lane_forward_points_1.append(point_index)
            # temp_dist_lane_forward_points_1.append(dist_to_point)
            temp_dist_lane_forward_points_1.append([point_index,dist_to_point])
            # print("temp_dist_lane_forward_points_1: " + str(temp_dist_lane_forward_points_1))
            # cars[car_id].dist_lane_forward_points_1.append([lane_of_int,line_of_int,dist_to_point])
        # print("temp_dist_lane_forward_points_1_2: " + str(temp_dist_lane_forward_points_1))
        cars[car_id].dist_lane_forward_points_1.append(temp_dist_lane_forward_points_1)
        # if car_id == 10:
        #     print("     here 4 cars[car_id].dist_lane_forward_points_1: " + str(cars[car_id].dist_lane_forward_points_1))
def find_dist_to_lane_points_method_lanes_common(cars,lanes_test,car_id,rad_gps):
    for r in range(len(cars[car_id].potential_lanes_lines_2)):
        if cars[car_id].potential_lanes_lines_2[r][0] in cars[car_id].localisation_lanes_common:
            lane_of_int = cars[car_id].potential_lanes_lines_2[r][0]
            line_of_int = cars[car_id].potential_lanes_lines_2[r][1]
            point_of_intersection = cars[car_id].potential_lanes_lines_2[r][2]

            first_point_of_int_index = line_of_int + 1  # this give the point at the end of the line_of_int
            num_of_points_in_lane = len(lanes_test[lane_of_int].points_with_angles)

            temp_dist_lane_forward_points_lanes_common = []
            temp_dist_lane_forward_points_lanes_common.append(lane_of_int)

            for k in range(first_point_of_int_index , num_of_points_in_lane): # loop through the first point and all points to the end of lane
                point_index = k
                temp_lane_line_point = lanes_test[lane_of_int].points_with_angles[k][0:2]
                # print("temp_lane_line_point: " + str(temp_lane_line_point))
                # canvas.create_oval(temp_lane_line_point[0] - 2, temp_lane_line_point[1] - 2,temp_lane_line_point[0] + 2,temp_lane_line_point[1] + 2, fill = 'yellow')
                # tk.update()
                dist_to_point = math.sqrt(((temp_lane_line_point[1] - point_of_intersection[1])**2) + ((temp_lane_line_point[0] - point_of_intersection[0])**2))
                temp_dist_lane_forward_points_lanes_common.append([point_index,dist_to_point])
                # print("temp_dist_lane_forward_points_lanes_common: " + str(temp_dist_lane_forward_points_lanes_common))
                # cars[car_id].dist_lane_forward_points_1.append([lane_of_int,line_of_int,dist_to_point])
            # print("temp_dist_lane_forward_points_2: " + str(temp_dist_lane_forward_points_lanes_common))
            cars[car_id].dist_lane_forward_points_lanes_common.append(temp_dist_lane_forward_points_lanes_common)
def find_intersection_point_between_lines(line_1,line_2):       # ([[line_1_point_1_x,line_1_point_1_y],[line_1_point_2_x,line_1_point_2_y]],[[line_2_point_1_x,line_2_point_1_y],[line_2_point_2_x,line_2_point_2_y]]):
    # next_lane_first_point = lanes_test[j].points[0][0:2]
    # next_lane_second_point = lanes_test[j].points[1][0:2]
    # next_lane_points = [next_lane_first_point,next_lane_second_point]
    # print("j: " + str(j) + " next_lane_points: " + str(next_lane_points))
    # line_1 = [[line_1_point_1_x,line_1_point_1_y],[line_1_point_2_x,line_1_point_2_y]]
    # line_2 = [[line_2_point_1_x,line_2_point_1_y],[line_2_point_2_x,line_2_point_2_y]]

    xdiff = (line_1[0][0] - line_1[1][0], line_2[0][0] - line_2[1][0])
    ydiff = (line_1[0][1] - line_1[1][1], line_2[0][1] - line_2[1][1])

    # xdiff = (lane_points[0][0] - lane_points[1][0], next_lane_points[0][0] - next_lane_points[1][0])
    # ydiff = (lane_points[0][1] - lane_points[1][1], next_lane_points[0][1] - next_lane_points[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
        intersection_cross = 0 # so do not cross, could be straight ahead or parallel
        # x = next_lane_first_point[0]
        # y = next_lane_first_point[1]
        # canvas.create_oval((x + 2),(y + 2),(x - 2),(y -2))
        # lanes_test[i].next_lanes_intersection.append([j,x,y])
       # raise Exception('lines do not intersect')
    else:
        # d = (det(*lane_points), det(*next_lane_points))
        d = (det(*line_1), det(*line_2))
        x = det(d, xdiff) / div
        y = det(d, ydiff) / div
        x_round = round(x)
        y_round = round(y)
        intersection_cross = 1 # so do cross
        # canvas.create_oval((x + 2),(y + 2),(x - 2),(y -2))
        point_of_intersection = [x,y]
        # lanes_test[i].next_lanes_intersection.append([j,x,y])
        return point_of_intersection

### threads start
# t5 = Find_Lane_Localisation()
t6 = SetTimeLights()
t7 = ExtractCarInfo()
t8 = FindWaitTimeForLanes()
t9 = FindGreenLightLanes()
t10 = Find_Lane_Localisation_from_RealTest()
# t5.daemon = True
t6.daemon = True
t7.daemon = True
t8.daemon = True
t9.daemon = True
t10.daemon = True

# t5.start()
t6.start()  # this thread cycles through the lanes at junc to turn them green for a set time
# t7.start()
# t8.start()
# t9.start() # this thread is the algoritm which selects the lane in the junc to turn green
t10.start()

####

time_limit = 300
# time_interval = 0.05
time_current = 0
time_checker = 0
time_checker_2 = 4
green_light_lanes = []
red_light_lanes_pause_temp = []
for i in range(len(juncs_test)):
    lane_selected_temp = juncs_test[i].light_lanes_at_junc[0]
    lanes_test[lane_selected_temp].time_green = 3
    lanes_test[lane_selected_temp].green_light = 1

cars_intending_to_enter = []
starter_checker = 1
num_cars_entered_system = len(cars_entered_system)
new_cars_per_interval = 15
car_entry_interval_timer = 0
car_entry_interval_timer_limit = 3 # number of seconds between the arrival of a new batch of cars

for i in range(num_initial_internal_cars):
# for i in range(num_cars):
    cars_intending_to_enter.append(cars[i].id)
    cars[i].car_waiting_to_enter_system = 1

time_print_checker = 0
############## running loop

while time_current < time_limit:
    # if starter_checker == 1:
    #     #set starter_checker back to 0
    #     starter_checker = 0
    #     # introduce all num_initial_internal_cars
    #     for i in range(num_initial_internal_cars):
    #     # for i in range(num_cars):
    #         cars_intending_to_enter.append(cars[i].id)

    if car_entry_interval_timer >=  car_entry_interval_timer_limit:
        print("new arrivals")
        # input("new arrivals")
        car_entry_interval_timer = 0
        num_cars_entered_system = len(cars_entered_system)
        # print("num_cars_entered_system: " + str(num_cars_entered_system))
        # input("paused 1")
        # print("num_cars_entered_system = " + str(num_cars_entered_system))
        # print("car_in_lane_12: " + str(lanes_test[12].cars_in_lane_id))
        if num_cars_entered_system + new_cars_per_interval <= num_cars:
            for i in range(num_cars_entered_system,(num_cars_entered_system + new_cars_per_interval)):
                # an interval is every 10 seconds
                # add car_id to cars_to_intending_to_enter
                # check if car already in cars_intending_to_enter
                if (i not in cars_intending_to_enter) and (i not in cars_entered_system):
                    cars_intending_to_enter.append(cars[i].id)
                    cars[i].car_waiting_to_enter_system = 1
                    # if i in cars_entered_system:
                    #     print("cars_in_system: " + str(cars_in_system))
                    #     print("car_i: " + str(i) + " cur_lane: " + str(cars[i].current_lane))
                    #     print("cars_in_cur_lane: " + str(lanes_test[cars[i].current_lane].cars_in_lane_id))
                    #     # input("stop here")
                    #     cars_intending_to_enter.remove(i)
            # print("cars_intending_to_enter: "+ str(cars_intending_to_enter))
        if num_cars_entered_system + new_cars_per_interval > num_cars:
            diff_temp = num_cars - num_cars_entered_system
            # print("diff_temp: " + str(diff_temp))
            if diff_temp > 0:
                new_cars_per_interval_temp = diff_temp
                for i in range(num_cars_entered_system,(num_cars_entered_system + new_cars_per_interval_temp)):
                    # an interval is every 10 seconds
                    # add car_id to cars_to_intending_to_enter
                    # check if car already in cars_intending_to_enter
                    if i not in cars_intending_to_enter:
                        # print("i: " + str(i))
                        cars_intending_to_enter.append(cars[i].id)
                        cars[i].car_waiting_to_enter_system = 1
                # print("cars_intending_to_enter: "+ str(cars_intending_to_enter))



    light_control_function(juncs_test,lanes_test,green_light_lanes,time_interval,red_light_lanes_pause_temp)
    cars_to_wait_this_iter = []
    cars_entering_this_iter = []
    # print("car_in_lane_12: " + str(lanes_test[12].cars_in_lane_id))
    # print("cars_mstatus_79: " + str(cars[79].move_status))
    # print("cars")
    # print("cars_intending_to_enter: " + str(cars_intending_to_enter))
    for car_id in cars_intending_to_enter:
        car_entering_function(cars,lanes_test,Car,car_id,cars_in_system,cars_entered_system,cars_intending_to_enter,cars_to_wait_this_iter,cars_entering_this_iter)

    temp_cars_intending_to_enter = []
    for i in cars_intending_to_enter:
        if i in cars_to_wait_this_iter:
            temp_cars_intending_to_enter.append(i)
    cars_intending_to_enter = temp_cars_intending_to_enter

    # print("ran 4 end pos_in_queue: " + " current_end_step_0: " + str(cars[0].current_end_step))
    move_function_new(cars,lanes_test,Car,green_light_lanes)

    # canvas.itemconfig(cars[10].body, fill='orange')
    # if cars[10].localised_stage == 2:
    #     canvas.itemconfig(cars[10].body, fill='green')
    #
    # if cars[10].sampling_checker == 1:
    #     canvas.create_oval(cars[10].pos_x - rad_gps,cars[10].pos_y - rad_gps,cars[10].pos_x + rad_gps, cars[10].pos_y + rad_gps )
    #     canvas.create_oval(cars[10].coords[0] - 2,cars[10].coords[1] - 2,cars[10].coords[0] + 2, cars[10].coords[1] + 2, fill ='red' )
        # draw car
    # for i in range(len(juncs_test)):
    #     if i == 2:
    #         print("i: " + str(i) + " green_lanes_at_junc: " + str(juncs_test[i].green_lanes_at_junc))
    #         print("map_green_lane: " + str(lanes_test[juncs_test[i].green_lanes_at_junc].map_lane_id))


    time_checker += time_interval
    time_checker_2 -= time_interval

    # for car_temp in cars_in_system:
    #     if cars[car_temp].localised_stage == 1:
    #         canvas.itemconfig(cars[2].body, fill='orange')
    #     if cars[car_temp].localised_stage == 2:
    #         canvas.itemconfig(cars[2].body, fill='green')


    # if cars[0].localised_stage == 1:
    #     canvas.itemconfig(cars[0].body, fill='orange')
    # if cars[0].localised_stage == 2:
    #     canvas.itemconfig(cars[0].body, fill='green')

    # canvas.itemconfig(cars[7].body, fill='green')

    if cars[0].sampling_checker == 1:
        canvas.create_oval(cars[0].pos_x - rad_gps,cars[0].pos_y - rad_gps,cars[0].pos_x + rad_gps, cars[0].pos_y + rad_gps )
        canvas.create_oval(cars[0].coords[0] - 2,cars[0].coords[1] - 2,cars[0].coords[0] + 2, cars[0].coords[1] + 2, fill ='red' )

    # canvas.itemconfig(cars[79].body, fill='red')
    # print("car_57_step: " + str(cars[57].step))
    # print("cars_in_lane_id_5: " + str(lanes_test[5].cars_in_lane_id))



    for i in range(num_cars):
        if (cars[i].current_lane == cars[i].g_lane) or (cars[i].g_lane in lanes_test[cars[i].current_lane].assoc_lanes):
            canvas.itemconfig(cars[i].body, fill='green')
        else:
            canvas.itemconfig(cars[i].body, fill='black')
        # if cars[i].next_lane in lanes_test[cars[i].current_lane].free_turn_next_lanes:
        #     # turne car to pink
        #     # print("turn pink car: "+ str(i))
        #     # print("current_end_step: " + str(cars[i].current_end_step) + " step: " + str(cars[i].step) + " current_lane_end_step: " + str(cars[i].current_lane_end_step))
        #     # print("pink lane: " + str(cars[i].current_lane) + " cars_in_lane_id: " + str(lanes_test[cars[i].current_lane].cars_in_lane_id))
        #     canvas.itemconfig(cars[i].body, fill='pink')
        # else:
        #     canvas.itemconfig(cars[i].body, fill='black')
        if cars[i].car_in_system == 1: # ie. TRUE
            cars[i].time_in_system += time_interval
        if cars[i].car_waiting_to_enter_system == 1: # ie. TRUE
            cars[i].wait_time_to_enter_system += time_interval
        if cars[i].car_waiting_in_queue == 1: # ie. TRUE
            cars[i].wait_time_in_queue += time_interval
        if cars[i].car_moving == 1: #ie. TRUE
            cars[i].move_time += time_interval

    # print("car_76 path: " + str(cars[76].path))
    # print("car_76 cur_lane: " + str(cars[76].current_lane) + " g_lane: " + str(cars[76].g_lane))
    # canvas.itemconfig(cars[76].body, fill='red')
    tk.update()
    time_current += time_interval
    car_entry_interval_timer += time_interval
    # print("time_current: " + str(time_current))
    time_print_checker += time_interval
    if time_print_checker > 5:
        print("time_current: " + str(time_current))
        time_print_checker = 0

    time.sleep(time_interval)

##### end of running loop

tk.update()
running_check = 0 # this should halt the threads
overall_wait_time_in_queue = 0
overall_move_time = 0
overall_wait_time_to_enter_system = 0
overall_time_in_system = 0
for i in range(num_cars):
    overall_wait_time_in_queue += cars[i].wait_time_in_queue
    overall_move_time += cars[i].move_time
    overall_wait_time_to_enter_system += cars[i].wait_time_to_enter_system
    overall_time_in_system += cars[i].time_in_system

    print("car: " + str(i) + " wait_time_to_enter_system: " + str(cars[i].wait_time_to_enter_system))
    print("car: " + str(i) + " time_in_system: " + str(cars[i].time_in_system))
    print("car: " + str(i) + " wait_time_in_queue: " + str(cars[i].wait_time_in_queue))
    print("car: " + str(i) + " move_time: " + str(cars[i].move_time))

    print("overall_wait_time_in_queue: " + str(overall_wait_time_in_queue))
    print("overall_move_time: " + str(overall_move_time))
    print("overall_wait_time_to_enter_system: " + str(overall_wait_time_to_enter_system))
    print("overall_time_in_system: " + str(overall_time_in_system))
input("Press enter to end")
