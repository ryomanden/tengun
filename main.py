import open3d as o3d
import pandas as pd


# --- set parameters --- #
imoport_file_num = 40
downsample_voxel_size = 0.1
dataDir = r"D:\tengun\④池尻周辺\0848_202301211433\Output\Color3D_ZF\LaserC01\xyHBLh\C12L1"


df = pd.read_csv(dataDir + r"\Laser3D_Color_I_0000_C12-L1.csv", header=None)
for i in range(imoport_file_num):
    print("importing Laser3D_Color_I_0{}_C12-L1.csv ... ".format(str(i+1).zfill(3)))
    df = pd.concat([df,pd.read_csv(dataDir + r"\Laser3D_Color_I_0{}_C12-L1.csv".format(str(i+1).zfill(3)), header=None)], ignore_index=True)
    # o3d.visualization.draw_geometries([pcd])
# df = pd.read_csv(dataDir + r"\Laser3D_Color_I_0000_C12-L1.csv", header=None)

print("Create PointCloud ... ")
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(df.iloc[:, 0:3].values)
pcd.colors = o3d.utility.Vector3dVector(df.iloc[:, 9:12].values / 255)
print("Done.")

print("Downsampling PointCloud ... ")
downpcd = pcd.voxel_down_sample(voxel_size=downsample_voxel_size)
print("Done.")

print("result\n before : {} points\n after : {} points".format(len(pcd.points), len(downpcd.points)))
o3d.visualization.draw_geometries([downpcd])