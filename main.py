import open3d as o3d
import pandas as pd

dataDir = r"D:\tengun\④池尻周辺\0848_202301211433\Output\Color3D_ZF\LaserC01\xyHBLh\C12L1"
# dataDir = r"C:\Users\Ryo_Mitsuda\Downloads\bunny\data"

df = pd.read_csv(dataDir + r"\Laser3D_Color_I_0000_C12-L1.csv", header=None)
for i in range(20):
    print("importing Laser3D_Color_I_0{}_C12-L1.csv ... ".format(str(i+1).zfill(3)))
    df = pd.concat([df,pd.read_csv(dataDir + r"\Laser3D_Color_I_0{}_C12-L1.csv".format(str(i+1).zfill(3)), header=None)], ignore_index=True)
    pcd = o3d.geometry.PointCloud()
    # o3d.visualization.draw_geometries([pcd])
# df = pd.read_csv(dataDir + r"\Laser3D_Color_I_0000_C12-L1.csv", header=None)

print("Create PointCloud ... ")
pcd.points = o3d.utility.Vector3dVector(df.iloc[:, 0:3].values)
pcd.colors = o3d.utility.Vector3dVector(df.iloc[:, 9:12].values / 255)
print("Done.")


o3d.visualization.draw_geometries([pcd])