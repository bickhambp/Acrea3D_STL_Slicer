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
        self.layer_height_mm = 0.01
        self.pixel_pitch_mm = 0.0076
        self.resolution_px2 = [10,10]

        self.volume_mm3 = None
        
        self.significant_meshes = []
        self.significant_points = []
        self.png_blueprint = [[[] for y in range(self.resolution_px2[1])] for x in range(self.resolution_px2[0])]
        pass

    def import_stl(self, stl):
        self.print_file_path = stl
        self.print_file_mesh = mesh.Mesh.from_file(self.print_file_path)          #Import Mesh

    def read_values(self):
        self.volume_mm3 = self.print_file_mesh.get_mass_properties()[0]
        self.height_print_mm = self.print_file_mesh.max_[2]
        print("X: ", self.print_file_mesh.max_[0])
        print("Y: ", self.print_file_mesh.max_[1])
        self.num_layers = int(self.height_print_mm / self.layer_height_mm)
        pass

    def get_significant_meshes(self):
        for i in range(len(self.print_file_mesh.normals)):
            if self.print_file_mesh.normals[i][2] != 0:
                temp_data = self.print_file_mesh.points[i].tolist()
                temp_data.append(self.print_file_mesh.normals[i][0])
                temp_data.append(self.print_file_mesh.normals[i][1])
                temp_data.append(self.print_file_mesh.normals[i][2])
                #print("Temp Data: ", temp_data)
                self.significant_meshes.append(temp_data)
        #print("SM: ", self.significant_meshes)
        return self.significant_meshes

    def get_mesh_vectors(self, mesh):
        points = [[mesh[0],mesh[1],mesh[2]],[mesh[3],mesh[4],mesh[5]],[mesh[6],mesh[7],mesh[8]]]
        points.sort()
        p1 = points[0]
        p2 = points[1]
        p3 = points[2]

        def get_vector(point1, point2):
            vector = []
            for i in range(3):
                vector.append(point2[i] - point1[i])
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
        list_border_points = []

        starting_point_x = 0
        if(round(point[0] % self.pixel_pitch_mm == 0),10):
            starting_point_x = point[0]
        else:
            starting_point_x = int(point[0] / self.pixel_pitch_mm + 1) * self.pixel_pitch_mm

        num_points_x = 0

        if (vector[0] > (self.pixel_pitch_mm - (point[0] % self.pixel_pitch_mm))):
            num_points_x = 1
            print(vector[0], point[0])
        if point[0] % self.pixel_pitch_mm == 0:
            num_points_x = 1 + int(vector[0] / self.pixel_pitch_mm)
            print("NUMX1: ", num_points_x)
        else:
            num_points_x = num_points_x + int((vector[0] - (self.pixel_pitch_mm - (point[0] % self.pixel_pitch_mm))) / self.pixel_pitch_mm)
            print("NUMX2: ", num_points_x)

        for num_x in range(num_points_x):
            pos_x = (num_x - 1) * self.pixel_pitch_mm + starting_point_x
            pos_x_relative = starting_point_x - point[0] 
            pos_y = vector[1] / vector[0] * (pos_x_relative + num_x * self.pixel_pitch_mm) + point[1]
            print(num_points_x, pos_x, pos_y)
            border_point = [pos_x, pos_y]
            list_border_points.append(border_point)

        if(num_points_x > 0):
            return list_border_points
        else:
            return None

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


        for i in range(0,len(list_border_points),2):
            num_points_y = int(round((list_border_points[i+1][1] /self.pixel_pitch_mm),5)) - int(round((list_border_points[i][1] / self.pixel_pitch_mm),5))
            # print("#Y", num_points_y)
            for num_y in range(num_points_y):
                x = round(list_border_points[i][0], 8)
                y = round(num_y * self.pixel_pitch_mm + list_border_points[i][1], 8)
                z = self.get_z([x,y], mesh)        
                list_points.append([x,y,z])

        
        list_points.sort()
#        print("LP: ", list_points)
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
            



        
    def make_3D_image_blueprint(self): 
        # print("Start Get Significant Meshes")
        self.get_significant_meshes()
        
        for mesh in self.significant_meshes:
            # print("NUMBER")
            temp = self.project_mesh_xyz(mesh)
            #print("TEMP: ", temp)
            for points in temp:
                x_pos = int(round(points[0] / self.pixel_pitch_mm, 5))
                y_pos = int(round(points[1] / self.pixel_pitch_mm, 5))
                #print("POS: ", x_pos, y_pos)
                #print("XYPOS ", x_pos, y_pos)
                if self.png_blueprint[x_pos][y_pos] == None:
                    #print("Single")
                    self.png_blueprint[x_pos][y_pos] = points[2]
                else:
                    #print("Duplicate", self.png_blueprint[x_pos][y_pos])
                    self.png_blueprint[x_pos][y_pos].append(points[2])  
                    if len(self.png_blueprint[x_pos][y_pos]) > 2: print("Duplicate", self.png_blueprint[x_pos][y_pos])              

        print(self.png_blueprint)

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

    def print_png(self):
        png_image = [[255 for y in range(self.resolution_px2[1])] for x in range(self.resolution_px2[0])]

        #print(self.png_blueprint)

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
    my_print.import_stl("./STL_Files/10x10_7p6um_small_cylinder.stl")
    print("Read Values")
    my_print.read_values()
    # mesh = my_print.get_significant_meshes()
    # my_print.map_mesh_xyz(mesh[0])
    print("Make Blueprint")
    my_print.make_3D_image_blueprint()
    print("Print Images")    
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