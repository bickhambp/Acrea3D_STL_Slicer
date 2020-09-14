import stl
from stl import mesh

class StlFileData():
    def __init__(self, filename):
        self.filename = filename
        self.meshList = []
        # self.significant_meshes = []
    
    def getMeshList(self):
        tempList = mesh.Mesh.from_file(self.filename)
        pointsList = tempList.points
        normalsList = tempList.normals.tolist()

        for i in range(len(pointsList)):
            tempData = pointsList[i].tolist()
            tempData.append(normalsList[i][0])
            tempData.append(normalsList[i][1])
            tempData.append(normalsList[i][2])
            self.meshList.append(tempData)
        

    # def get_significant_meshes(self):
    #     for i in range(len(self.meshList.normals)):
    #         if self.meshList.normals[i][2] != 0:
    #             temp_data = self.meshList.points[i].tolist()
    #             # print("Significant mesh:  ", round(temp_data[0],5), round(temp_data[1],5), round(temp_data[2],5), round(temp_data[3],5), round(temp_data[4],5), round(temp_data[5],5), round(temp_data[6],5), round(temp_data[7],5), round(temp_data[8],5))
    #             temp_data.append(self.meshList.normals[i][0])
    #             temp_data.append(self.meshList.normals[i][1])
    #             temp_data.append(self.meshList.normals[i][2])
    #             self.significant_meshes.append(temp_data)
    #     # print("SM: ", self.significant_meshes)
    #     return self.significant_meshes

    def exportMeshList(self, exportName):
        exportFile = open(exportName, "w")
        for mesh in self.meshList:
            exportFile.write(str(mesh))
        exportFile.close()
        pass


if __name__ == "__main__":
    stlFile = StlFileData("./STL_Files/GradientDiffusionPillars2px.stl")
    stlFile.getMeshList()
    # stlFile.get_significant_meshes()
    stlFile.exportMeshList("./temp/stlfiledata.txt")