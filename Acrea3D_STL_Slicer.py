import stl
from stl import mesh
import numpy as np
import png
import os

class print_data():

    def __init__(self):
        self.print_file_mesh = None
        self.print_file_path = None
        self.height_print_mm = None
        self.num_layers = None
        self.layer_height_mm = 0.1
        self.pixel_pitch_mm = 0.1
        self.resolution_px2 = [10,10]

        self.volume_mm3 = None
        
        self.significant_meshes = []
        self.significant_points = []
        self.png_blueprint = [[None for y in range(self.resolution_px2[1])] for x in range(self.resolution_px2[0])]
        print("BLUE PRINT", self.png_blueprint)
        pass

    def import_stl(self, stl):
        self.print_file_path = stl
        self.print_file_mesh = mesh.Mesh.from_file(self.print_file_path)          #Import Mesh

    def read_values(self):
        self.volume_mm3 = self.print_file_mesh.get_mass_properties()[0]
        self.height_print_mm = self.print_file_mesh.max_[2]
        self.num_layers = int(self.height_print_mm / self.layer_height_mm)
        pass

    def get_significant_meshes(self):
        for i in range(len(self.print_file_mesh.normals)):
            if self.print_file_mesh.normals[i][2] != 0:
                temp_data = self.print_file_mesh.points[i].tolist()
                #print("Temp Data ", temp_data)
                temp_data.append(self.print_file_mesh.normals[i][0])
                temp_data.append(self.print_file_mesh.normals[i][1])
                temp_data.append(self.print_file_mesh.normals[i][2])
                #print("Temp Data: ", temp_data)
                self.significant_meshes.append(temp_data)
        #print(self.significant_meshes)
        return self.significant_meshes

    def get_mesh_vectors(self, mesh):
        p1 = [mesh[0],mesh[1],mesh[2]]
        p2 = [mesh[3],mesh[4],mesh[5]]
        p3 = [mesh[6],mesh[7],mesh[8]]
        va = p1

        def get_vector(point1, point2):
            print("POINTS ", point1, point2)
            vector = []
            for i in range(3):
                vector.append(point1[i] - point2[i])
            return vector
        #va = p1
        va = []
        va.append(get_vector(p1,p2))
        va.append(get_vector(p1,p3))
        va.append(get_vector(p2, p3))
        #vb = p1
        #vb.append(get_vector(p2,p1))
        #vb.append(get_vector(p2,p3))
        
        #return va, vb
        return va, p1, p2

    def get_border_point(self, vector, point, mesh):
        starting_point_x = int(point[0] / self.pixel_pitch_mm) * self.pixel_pitch_mm
        temp_list_points = []
        num_points_x = 0
        if vector[0] != 0:
            num_points_x = int(int(point[0] /self.pixel_pitch_mm) - int(vector[0] / self.pixel_pitch_mm))
        for num_x in range(num_points_x):
            x = num_x * self.pixel_pitch_mm
            y = 0
            if vector[0] != 0:
                y = vector[1] / vector[0] * x
            temp_point = [round(point[0] + x, 10), round(point[1] + y,5)]
            temp_list_points.append(temp_point)

        return temp_list_points

    def get_points_on_mesh(self, list_points):
        for i in range(0,len(list_points),2):
            self.get_z(point, mesh)

            

    def project_mesh_xyz(self, mesh):
        list_vectors, p1, p2 = self.get_mesh_vectors(mesh)
        list_border_points = []

        list_border_points.extend(self.get_border_point(list_vectors[0], p1, mesh))
        list_border_points.extend(self.get_border_point(list_vectors[1], p1, mesh))
        list_border_points.extend(self.get_border_point(list_vectors[2], p2, mesh))
        list_border_points.sort()

        list_points = []
        print(list_border_points)

        for i in range(0,len(list_border_points),2):
            num_points_y = int(round((list_border_points[i+1][1] /self.pixel_pitch_mm),5)) - int(round((list_border_points[i][1] / self.pixel_pitch_mm),5)) + 1
            # print("#Y", num_points_y)
            for num_y in range(num_points_y):
                x = round(list_border_points[i][0], 8)
                y = round(num_y * self.pixel_pitch_mm + list_border_points[i][1], 8)
                z = self.get_z([x,y], mesh)        
                list_points.append([x,y,z])

        # print("LP: ", list_points)
        list_points.sort()
        print("LP: ", list_points)

        return list_points 

    def get_z(self, point, mesh):
        a,b,c = mesh[9],mesh[10],mesh[11]
        #print(mesh,a,b,c) 
        x,y,z = point[0], point[1], 0
        x1, y1, z1 = mesh[0], mesh[1],  mesh[2]
        if x1 == x and y1 == y:
            z2 = z1
        else:
            z2 = ((a * (x1 - 2 * x) + b * ( y1 - 2 * y)) / c) + z1 - z
        return z2            
            



    # ## returns all the points on a given mesh
    # def map_mesh_xyz(self, mesh):
    #     self.project_mesh_xyz(mesh)
    #     a,b = self.get_mesh_vectors(mesh)
    #     print("GET_MESH_VECTORS ", a, b)
    #     pixel_list = []
    #     for i in range(3):
    #         point = [mesh[3*i], mesh[3*i+1], mesh[3*i+2]]
    #         pixel_list.append(point)
    #     # print("Pixel List: ", pixel_list)

    #     def get_boundaries(axis):
    #         pmax = pixel_list[0][axis]
    #         #print(pmax)
    #         pmin = pixel_list[0][axis]
    #         #print(pmin)
    #         for i in range(len(pixel_list)):
    #             #print("Pixel List", pixel_list[i][axis])
    #             if(int(pixel_list[i][axis]) > pmax):
    #                 pmax = pixel_list[i][axis]
    #             if(int(pixel_list[i][axis]) < pmin):
    #                 pmin = pixel_list[i][axis]
    #         return [pmin, pmax]
                
    #     boundaries_mm = [get_boundaries(0)]
    #     boundaries_mm.append(get_boundaries(1))
    #     boundaries_mm.append(get_boundaries(2))
    #     # print("BOUNDARIES: ", boundaries_mm)

    #     def get_starting_pos(axis):
    #         if(boundaries_mm[axis][0] % self.pixel_pitch_mm < self.pixel_pitch_mm / 2): 
    #             pos = int(boundaries_mm[axis][0] / self.pixel_pitch_mm) * self.pixel_pitch_mm + 1/2 * self.pixel_pitch_mm
    #         else:
    #             pos = int(boundaries_mm[axis][0] / self.pixel_pitch_mm) * self.pixel_pitch_mm + 3/2 * self.pixel_pitch_mm
    #         return pos

    #     starting_point = [get_starting_pos(0)]
    #     starting_point.append(get_starting_pos(1))

    #     # print("Starting Point", starting_point)

    #     def get_angle(temp_point, pivot):
    #         if temp_point[0] >= pivot[0]:
    #             if temp_point[1] >= pivot[1]:       #Quadrant 1
    #                 temp_angle = ((np.arctan((temp_point[1] - pivot[1]) / (temp_point[0] - pivot[0])) + 2 * np.pi)) % (2 * np.pi)
    #                 # print("Q1: ", temp_angle)
    #             else:       #Quandrant 4
    #                 temp_angle = ((np.arctan((temp_point[1] - pivot[1]) / (temp_point[0] - pivot[0])) + 2 * np.pi)) % (2 * np.pi)
    #                 # print("Q4: ", temp_angle)
    #         else:
    #             if temp_point[1] >= pivot[1]:       #Quadrant 2
    #                 temp_angle = np.pi - abs(np.arctan((temp_point[1] - pivot[1]) / (temp_point[0] - pivot[0])))
    #                 # print("Q2: ", temp_angle)
    #             else:                   #Quadrant 3
    #                  temp_angle = np.pi + abs(np.arctan((temp_point[1] - pivot[1]) / (temp_point[0] - pivot[0])))
    #                 #  print("Q3: ", temp_angle)
    #         return temp_angle

    #     def get_min_max_angle_rad(points):
    #         # print(angle1_rad * 360 / (2 * np.pi))
    #         # print(angle2_rad * 360 / (2 * np.pi))

    #         if (points[1][0] - points[0][0]) == 0:
    #             if (points[1][1] - points[0][1] > 0):
    #                 angle1_rad = np.pi/2
    #             else:
    #                 angle1_rad = 3 * np.pi / 2
    #         else:
    #             angle1_rad = get_angle(points[1],points[0])
    #             #angle1_rad = ((np.arctan((points[1][1] - points[0][1]) / (points[1][0] - points[0][0])) + 2 * np.pi)) % (2 * np.pi)
    #         if (points[2][0] - points[0][0]) == 0:
    #             if (points[2][1] - points[0][1] > 0):
    #                 angle2_rad = np.pi/2
    #             else:
    #                 angle2_rad = 3 * np.pi / 2                
    #         else:
    #             angle2_rad = get_angle(points[2],points[0])
    #             #angle2_rad = ((np.arctan((points[2][1] - points[0][1]) / (points[2][0] - points[0][0])) + 2 * np.pi)) % (2 * np.pi)

    #         # print(get_angle(points[1],points[0]))
    #         # print(get_angle(points[2],points[0]))

    #         diff_angle_rad = angle1_rad - angle2_rad
    #         if diff_angle_rad < 0:
    #             if abs(diff_angle_rad) < np.pi:
    #                 min_angle_rad = angle1_rad
    #                 max_angle_rad = angle2_rad
    #             else:
    #                 min_angle_rad = angle2_rad
    #                 max_angle_rad = angle1_rad
    #         else:
    #             if abs(diff_angle_rad) < np.pi:
    #                 min_angle_rad = angle2_rad
    #                 max_angle_rad = angle1_rad
    #             else:
    #                 min_angle_rad = angle1_rad
    #                 max_angle_rad = angle2_rad

    #         # print(min_angle_rad, max_angle_rad)
    #         return [min_angle_rad, max_angle_rad, points[0]]

    #     angle1_min_max_rad = get_min_max_angle_rad(pixel_list)
    #     angle2_min_max_rad = get_min_max_angle_rad([pixel_list[1],pixel_list[2],pixel_list[0]])

    #     list_points = []

    #     num_x_pixels = (boundaries_mm[0][1] - starting_point[0]) / self.pixel_pitch_mm
    #     num_y_pixels = (boundaries_mm[1][1] - starting_point[1]) / self.pixel_pitch_mm

    #     for x in np.arange(num_x_pixels):
    #         for y in np.arange(num_y_pixels):
    #             new_point = [starting_point[0] + x * self.pixel_pitch_mm, starting_point[1] + y * self.pixel_pitch_mm]
    #             list_points.append(new_point)

    #     # print("LIST POINT: ", list_points)
                
    #     def check_point_in_mesh(point):
    #         # angle = round(np.arctan((point[0] - pixel_list[0][0]) / (point[1] - pixel_list[0][1])) + 2 * np.pi, 5)
    #         # print("Flag 123 ",angle)
    #         # print("Flag 124 ", angle1_min_max_rad[0])
    #         # print("Flag 125 ", angle1_min_max_rad[1])

    #         def check_angle(angle_min_max):
    #             reference_point = angle_min_max[2]
    #             angle = round(get_angle(point, reference_point), 5) 
    #             # print("Min Max", angle_min_max)
    #             # print("Angle: ", angle)
    #             # print("Point: ", point)
    #             if point[0] == reference_point[0] and point[1] == reference_point[1]:
    #                 return True
    #             if angle_min_max[0] > angle_min_max[1]:
    #                 # print(1)
    #                 if angle >= round(angle_min_max[0], 5) and angle <= np.pi * 2:
    #                     # print(1.1)
    #                     return True
    #                 elif angle <= round(angle_min_max[1], 5) and angle >= 0:
    #                     # print(1.2)
    #                     return True
    #                 else:
    #                     # print(1.3)
    #                     return False
    #             else:
    #                 # print(2)
    #                 if angle >= round(angle_min_max[0], 5) and angle <= round(angle_min_max[1], 5):
    #                     # print(2.1)
    #                     return True
    #                 else:
    #                     # print(2.2)
    #                     return False

    #         if check_angle(angle1_min_max_rad) and check_angle(angle2_min_max_rad):
    #             return True
    #         else:
    #             return False
    #     #print(mesh)
    #   #  print(check_point_in_mesh([0.5 ,0.5 ,1000]))

    #     def get_z(point):
    #         a,b,c = mesh[9],mesh[10],mesh[11]
    #         #print(mesh,a,b,c) 
    #         x,y,z = point[0], point[1], 0
    #         x1, y1, z1 = mesh[0], mesh[1],  mesh[2]
    #         if x1 == x and y1 == y:
    #             z2 = z1
    #         else:
    #             z2 = ((a * (x1 - 2 * x) + b * ( y1 - 2 * y)) / c) + z1 - z
    #         return z2

    #     #print(get_z([0.5,0.5,0.5]))
    #     points_on_mesh = []
    #     # print("LP: ", list_points)
    #     for i in list_points:
    #         # print ("i: ", i)
    #         if check_point_in_mesh(i):
    #             point = [i[0],i[1],get_z(i)]
    #             points_on_mesh.append(point)
    #     #        print(point)
    #         #print(get_z(i))
    #     #print(len(list_points))
    #     #print("POINTS ON MESH: ", points_on_mesh)
    #     return points_on_mesh
        
    def make_3D_image_blueprint(self): 
        print("Start Get Significant Meshes")
        self.get_significant_meshes()
        print("Stop Get Significant Meshes")
        print("SIGNIFICANT MESHES: ", self.significant_meshes)

        # temp  = self.map_mesh_xyz([1.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0])
        # for points in temp:
        #     self.significant_points.append(points)
        print("Start Get Significant Points")
        print(len(self.png_blueprint), len(self.png_blueprint[0]))
        for mesh in self.significant_meshes:
            print("NUMBER")x
            temp = self.project_mesh_xyz(mesh)
            # print("TEMP: ", temp)
            for points in temp:
                x_pos = int(round(points[0] / self.pixel_pitch_mm, 5))
                y_pos = int(round(points[1] / self.pixel_pitch_mm, 5))
            # print("POS: ", x_pos, y_pos)
                print("XYPOS ", x_pos, y_pos)
                if self.png_blueprint[x_pos][y_pos] is None:
                    self.png_blueprint[x_pos][y_pos] = [points[2]]
                else:
                    self.png_blueprint[x_pos][y_pos].append(points[2])                
                #self.significant_points.append(points)
        print("Stop Get Significant Meshes")
#            print("TEMP", temp)
        # print("SIGNIFICANT POINTS, ", self.significant_points)
        # print("Length SIGNIFICANT POINTS: ", len(self.significant_points))
        # print("PRE BLUPRINT: ", self.png_blueprint)
        print("Start Get Significant Blueprints")
        # for points in self.significant_points:
        #     x_pos = int(round(points[0] / self.pixel_pitch_mm, 5))
        #     y_pos = int(round(points[1] / self.pixel_pitch_mm, 5))
        #     # print("POS: ", x_pos, y_pos)
        #     if self.png_blueprint[x_pos][y_pos] is None:
        #         self.png_blueprint[x_pos][y_pos] = [points[2]]
        #     else:
        #         self.png_blueprint[x_pos][y_pos].append(points[2])
            # print("During BLUPRINT: ", self.png_blueprint)    
        print("Stop Get Significant Blueprints")
        # for i in range(len(self.significant_points)):
        #     x_pos = int(round(self.significant_points[i][0] / self.pixel_pitch_mm, 5))
        #     y_pos = int(round(self.significant_points[i][1] / self.pixel_pitch_mm, 5))
        #     print("POS: ", x_pos, y_pos)
        #     if self.png_blueprint[x_pos][y_pos] is None:
        #         self.png_blueprint[x_pos][y_pos] = [points[2]]
        #     else:
        #         self.png_blueprint[x_pos][y_pos].append(points[2])
        #     print("During BLUPRINT: ", self.png_blueprint)    

        # print("BLUPRINT: ", self.png_blueprint)
        print("Start sort Blueprints")
        for x in self.png_blueprint:
            for y in x:
                #print(self.png_blueprint.index(x), x.index(y), y)
                try:
                    y.sort()
                except:
                    continue
                # print(self.png_blueprint.index(x), x.index(y), y)
                duplicates = True
                temp_index = 0
                while(duplicates):
                    # print("TEMP INDEX: ", temp_index)
                    # print("LENGTH: ", len(y))
                    if(temp_index >= len(y)):
                        break
                    if(y.count(y[temp_index]) > 1):
                        # print("VALUE: ", y[temp_index])
                        y.pop(temp_index)
                    else:
                        temp_index = temp_index + 1
                # print(self.png_blueprint.index(x), x.index(y), y)
        print("Stop sort Blueprints")
        # print("Sorted BLUPRINT: ", self.png_blueprint)   


    def print_png(self):
        png_image = [[255 for y in range(self.resolution_px2[1])] for x in range(self.resolution_px2[0])]

        for layer in range(self.num_layers):
            for x in range(self.resolution_px2[0]):
                for y in range(self.resolution_px2[1]):
                    for z in self.png_blueprint[x][y]:
                        if layer == 0:
                            # print("LAYER: ", layer)
                            if z == 0: 
                                png_image[x][y] = 255
                                # print("PNG Image: ", png_image[x][y])
                        else:
                            # print("LAYER: ", layer)
                            if z > (layer - 1) * self.layer_height_mm and z <= layer * self.layer_height_mm:
                                if png_image[x][y] == 0:
                                    png_image[x][y] = 255
                                    # print("PNG Image: ", png_image[x][y])
                                else:
                                    png_image[x][y] = 0
                                    # print("PNG Image: ", png_image[x][y])
                            else:
                                pass
            # print("IMAGE: ", png_image)
            file_name = layer
            self.export_png(file_name, png_image)

    def export_png(self, file_base_name, png_image):
        # png_image = np.array(png_image)
        # print(png_image)
        path = os.getcwd()
        file_name = "{}/slices/{}.png".format(path, file_base_name)
        png_file = open(file_name, 'wb')
        # png.from_array(png_image, mode="L", info= {height = 2, width = 2}).save("/tmp/foo.png")
        write_png = png.Writer(self.resolution_px2[1], self.resolution_px2[0], greyscale = True)
        write_png.write(png_file, png_image)
        png_file.close()


    


        #for point in self.significant_points:
         #   print(point)
            # if point[0] is not None:
            #     point[0] = int((point[0] - self.pixel_pitch_mm / 2) / self.pixel_pitch_mm)
            #     point[1] = int((point[1] - self.pixel_pitch_mm / 2) / self.pixel_pitch_mm)
            #     print(point)
            
        

    
    



# resolution_px = [2560, 1600]
# #print_height_mm = #Get from STL
# slice_thickness_mm = 0.01

# image_array = np.empty(shape = (2560,1600))

# temp_array = [[None] * 2560] * 1600

# temp_array[100][0] = [5]
# temp_array[100][0].append(32)
# print(temp_array[100][0])



if __name__ == "__main__":
    my_print = print_data()
    my_print.import_stl("./STL_Files/Cube.stl")
    my_print.read_values()
    # mesh = my_print.get_significant_meshes()
    # my_print.map_mesh_xyz(mesh[0])
    my_print.make_3D_image_blueprint()
    my_print.print_png()

    # import png

    # picture = [[0] * 2560] * 1600
    # # print(picture)
    # my_png = open("my_png.png", 'wb')
    # write_png = png.Writer(2560,1600, greyscale = True)
    # write_png.write(my_png, picture)
    # my_png.close()
    pass



# Using an existing closed stl file:
# your_mesh = mesh.Mesh.from_file('Cube.stl')

# print(your_mesh.points)

# volume, cog, inertia = your_mesh.get_mass_properties()
# print("Volume                                  = {0}".format(volume))
# print("Position of the center of gravity (COG) = {0}".format(cog))
# print("Inertia matrix at expressed at the COG  = {0}".format(inertia[0,:]))
# print("                                          {0}".format(inertia[1,:]))
# print("                                          {0}".format(inertia[2,:]))