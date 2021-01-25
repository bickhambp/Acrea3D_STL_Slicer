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
        self.resolution = [50,25]

        self.volume_mm3 = None
        
        self.significant_meshes = []
        self.significant_points = []
        self.png_blueprint = [[[] for y in range(self.resolution[1])] for x in range(self.resolution[0])]

        self.pixel_order_of_magnitude = 1e-4
        self.rounding_order_of_magnitude = 1e-8        
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
                temp_data.append(self.print_file_mesh.normals[i][0])
                temp_data.append(self.print_file_mesh.normals[i][1])
                temp_data.append(self.print_file_mesh.normals[i][2])
                self.significant_meshes.append(temp_data)
        return self.significant_meshes

    def round_point_to_nearest_pixel(self, point, round_up):
        if round_up:
            temp_point = int((point + self.pixel_pitch_mm ) / self.pixel_pitch_mm) * self.pixel_pitch_mm - self.pixel_pitch_mm / 2
        else:
            temp_point = int(point / self.pixel_pitch_mm) * self.pixel_pitch_mm - self.pixel_pitch_mm / 2

        return temp_point

    def get_vector_proportions(self, v1,v2,point):
        v2_factor = (point[0] * v1[1] - v1[0] * point[1])/(v2[0] * v1[1]-v1[0] * v2[1])
        v1_factor = (point[0] - v2[0] * v2_factor) / v1[0]

        return v1_factor, v2_factor

    def multiply_vector_by_constant(self, vector, constant):
        new_vector = []
        for value in vector:
            new_val = value * constant
            new_vector.append(new_val)  
        return new_vector

    def add_vectors(self, v1,v2):
        v3 = []
        for index in range(len(v1)):
            new_val = v1[index] + v2[index]
            v3.append(new_val)
        return v3
    
    def subtract_vectors(self, v1, v2):
        v3 = []
        for index in range(len(v1)):
            new_val = v1[index] - v2[index]
            v3.append(new_val)
        return v3

    def check_vector_in_vectors(self, v1, v2, v3):
        v1_factor,v2_factor = get_vector_proportions(v1,v2,v3)
        if v1_factor >= 0 and v2_factor >= 0:
            return True
        return False

    def get_z(self, point,mesh):
        origin = [mesh[0], mesh[1], mesh[2]]
        v1 = [mesh[3] - origin[0], mesh[4] - origin[1], mesh[5] - origin[2]]
        v2 = [mesh[6] - origin[0], mesh[7] - origin[1], mesh[8] - origin[2]]
        p1 = [point[0] - origin[0], point[1] - origin[1]]

        v1_per, v2_per = self.get_vector_proportions(v1,v2,p1)
        v1_part = self.multiply_vector_by_constant(v1, v1_per)
        v2_part = self.multiply_vector_by_constant(v2, v2_per)
        v3 = self.add_vectors(v1_part, v2_part)

        return v3[2] + mesh[2]
    
    def check_point_in_mesh(self, point, mesh):
        origin = [mesh[0], mesh[1]]
        v1 = [mesh[3] - origin[0], mesh[4] - origin[1]]
        v2 = [mesh[6] - origin[0], mesh[7] - origin[1]]
        v3 = [point[0] - origin[0], point[1] - origin[1]]
        v1_per, v2_per = self.get_vector_proportions(v1,v2,v3)
        if v1_per < 0 or v2_per < 0:
            return False
        origin = [mesh[3], mesh[4]]
        v1 = [mesh[0] - origin[0], mesh[1] - origin[1]]
        v2 = [mesh[6] - origin[0], mesh[7] - origin[1]]
        v3 = [point[0] - origin[0], point[1] - origin[1]]
        v1_per, v2_per = self.get_vector_proportions(v1,v2,v3)
        if v1_per < 0 or v2_per < 0:
            return False
        return True        
        

    def get_points_in_mesh(self, mesh):
        x_values = [mesh[0], mesh[3], mesh[6]] 
        y_values = [mesh[1], mesh[4], mesh[7]] 
        x_min = self.round_point_to_nearest_pixel(min(x_values), True) 
        x_max = self.round_point_to_nearest_pixel(max(x_values), True) 
        y_min = self.round_point_to_nearest_pixel(min(y_values), True) 
        y_max = self.round_point_to_nearest_pixel(max(y_values), True) 

        list_points = [] 
        x_range = int((x_max - x_min) / self.pixel_pitch_mm) 
        y_range = int((y_max - y_min) / self.pixel_pitch_mm) 

        for pixel_x in range(x_range):
            for pixel_y in range(y_range):

                x = pixel_x * self.pixel_pitch_mm + x_min
                y = pixel_y * self.pixel_pitch_mm + y_min
                if self.check_point_in_mesh([x,y], mesh):
                    z = self.get_z([x, y], mesh)
                    list_points.append([x, y, z])

        print("MESH: ", mesh) 
        print("X Range: " , x_min, x_max, "Y Range: ", y_min, y_max)
        print("List Points: ", list_points)
        return list_points

    def make_blueprint(self):
        for mesh in self.significant_meshes:
            self.significant_points.extend(self.get_points_in_mesh(mesh))
            
        # print(self.significant_points)
        self.significant_points.sort()
        a = 0
        for points in self.significant_points:
            x_pos = int(round((points[0] - self.pixel_pitch_mm / 2) / self.pixel_pitch_mm,4))
            y_pos = int(round((points[1] - self.pixel_pitch_mm / 2) / self.pixel_pitch_mm,4))
            z_pos = points[2]
            # if a < 10:
            # print(points, x_pos, y_pos,z_pos)
            # a += 1
            # if round(x_pos - self.pixel_pitch_mm / 2, 4) < 10:
            #     print(x_pos, y_pos)
            self.png_blueprint[x_pos][y_pos].append(z_pos)
        for x in range(len(self.png_blueprint)):
            for y in range(len(self.png_blueprint[x])):
                for z_index in range(len(self.png_blueprint[x][y])):
                    if self.png_blueprint.count(self.png_blueprint[x][y][z_index]) > 1:
                        self.png_blueprint[x][y][z_index] = -1
        while self.png_blueprint.count(-1) > 0:
            self.png_blueprint.remove(-1)
        for x in range(len(self.png_blueprint)):
            for y in range(len(self.png_blueprint[x])):
                self.png_blueprint[x][y].sort()        

    def print_blueprint(self):
        png_image = [[0 for x in range(self.resolution[0])] for y in range(self.resolution[1])]
        for layer in range(self.num_layers):
            for y in range(len(png_image)):
                for x in range(len(png_image[y])):
                    for z in self.png_blueprint[x][y]:
                        if layer == 0: 
                            if z == 0: 
                                png_image[y][x] = 255
                        else:
                            if z > (layer - 1) * self.layer_height_mm and z <= layer * self.layer_height_mm:
                                if png_image[y][x] == 0:
                                    png_image[y][x] = 255
                                else:
                                    png_image[y][x] = 0
                            else:
                                pass
            file_name = str(layer).zfill(4)
            export_png([self.resolution[0],self.resolution[1]], file_name, png_image)

def export_png(resolution, file_base_name, png_image):
    path = os.getcwd()
    file_name = "{}/slices/{}.png".format(path, file_base_name)
    png_file = open(file_name, 'wb')
    write_png = png.Writer(resolution[0], resolution[1], greyscale = True)
    write_png.write(png_file, png_image)
    png_file.close()

if __name__ == "__main__":
    my_print = print_data()
    my_print.import_stl("./STL_Files/small_diamond_cutout.stl")
    print("Read Values")
    my_print.read_values()
    # mesh = my_print.get_significant_meshes()
    # my_print.map_mesh_xyz(mesh[0])
    my_print.get_significant_meshes()
    # print(my_print.significant_meshes)
    print("Make Blueprint")
    my_print.make_blueprint()
    print("Print Images")
    my_print.print_blueprint()
    pass


