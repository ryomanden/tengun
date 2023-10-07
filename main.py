import open3d as o3d
import pandas as pd


# --- set parameters --- #
imoport_file_num = 50
downsample_voxel_size = 0.1
dataDir = r"D:\tengun\④池尻周辺\0848_202301211433\Output\Color3D_ZF\LaserC01\xyHBLh\C12L1"



# df = pd.read_csv(dataDir + r"\Laser3D_Color_I_0000_C12-L1.csv", names=col_names, usecols=[0, 1, 2, *range(9,12)])



def main():
    col_names = ["x", "y", "z", "r", "g", "b"]
    df = pd.DataFrame()
    for i in range(imoport_file_num):
        fname = "Laser3D_Color_I_0{}_C12-L1.csv".format(str(i).zfill(3))
        print("importing {} ...".format(fname))
        df = pd.concat([df,pd.read_csv(dataDir + r"\{}".format(fname), names=col_names, usecols=[0, 1, 2, *range(9,12)])], ignore_index=True)
        # o3d.visualization.draw_geometries([pcd])
    # df = pd.read_csv(dataDir + r"\Laser3D_Color_I_0000_C12-L1.csv", header=None)

    print(df)

    print("Create PointCloud ... ")
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(df[["x","y","z"]].values)
    pcd.colors = o3d.utility.Vector3dVector(df[["r","g","b"]].values / 255)
    print("Done.")

    print("Downsampling PointCloud ... ")
    downpcd = pcd.voxel_down_sample(voxel_size=downsample_voxel_size)
    print("Done.")

    print(""
          "result"
          "\n before : {} points"
          "\n after  : {} points".format(len(pcd.points), len(downpcd.points)))

    # o3d.visualization.draw_geometries([pcd])
    o3d.visualization.draw_geometries([downpcd])

main()

