import open3d as o3d
import numpy as np
import pandas as pd


# --- set parameters --- #
imoport_file_num = 50
downsample_voxel_size = 0.1
dataDir = r"D:\tengun\④池尻周辺\0848_202301211433\Output\Color3D_ZF\LaserC01\xyHBLh\C12L1"



# df = pd.read_csv(dataDir + r"\Laser3D_Color_I_0000_C12-L1.csv", names=col_names, usecols=[0, 1, 2, *range(9,12)])



def main():
    col_names = ["x", "y", "z", "r", "g", "b"]
    point = pd.DataFrame()
    for i in range(imoport_file_num):
        fname = "Laser3D_Color_I_0{}_C12-L1.csv".format(str(i).zfill(3))
        print("importing {} ...".format(fname))
        point = pd.concat([point,pd.read_csv(dataDir + r"\{}".format(fname), names=col_names, usecols=[0, 1, 2, *range(9,12)])], ignore_index=True)
        # o3d.visualization.draw_geometries([pcd])
    # df = pd.read_csv(dataDir + r"\Laser3D_Color_I_0000_C12-L1.csv", header=None)

    pcd = create_pointcloud(point)

    print("Downsampling PointCloud ... ")
    downpcd = pcd.voxel_down_sample(voxel_size=downsample_voxel_size)
    print("-> Done.")

    print(""
          "result"
          "\n before : {} points"
          "\n after  : {} points".format(len(pcd.points), len(downpcd.points)))

    # o3d.visualization.draw_geometries([pcd])
    o3d.visualization.draw_geometries([downpcd])
    if input("Create Mesh? [y/N]") == "y":
        mesh = create_mesh(downpcd)
        o3d.visualization.draw_geometries([mesh])

def create_pointcloud(point):
    print("Create PointCloud ... ")
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(point[["x","y","z"]].values)
    pcd.colors = o3d.utility.Vector3dVector(point[["r","g","b"]].values / 255)
    print("-> Done.")
    return pcd

def create_mesh(pcd):

    # コピペ元サイト
    # https://tecsingularity.com/open3d/bpa/

    # estimate normals 法線推定
    print("estimate normals ... ")
    pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
    print("-> Done.")

    # orient normals 点の方向性の一貫性の考慮
    print("Directional Consistency Considerations ... ")
    pcd.orient_normals_consistent_tangent_plane(10)
    print("-> Done.")

    # create mesh
    distances = pcd.compute_nearest_neighbor_distance()
    avg_dist = np.mean(distances)
    radius = 2 * avg_dist
    radii = [radius, radius * 2]
    print("create mesh ... ")
    mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(pcd, o3d.utility.DoubleVector(radii))
    print("-> Done.")
    return mesh

main()

