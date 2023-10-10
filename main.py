import os

import open3d as o3d
import numpy as np
import pandas as pd

from dotenv import load_dotenv
load_dotenv()

from rich.progress import track
from rich.console import Console
console = Console()



# --- set parameters --- #
imoport_file_num = 50
downsample_voxel_size = 0.1
data_dir = os.getenv("DATA_DIR")

def main():
    col_names = ["x", "y", "z", "r", "g", "b"]
    point = pd.DataFrame()
    for i in track(range(imoport_file_num)):
        fname = f"Laser3D_Color_I_0{str(i).zfill(3)}_C12-L1.csv"
        print("importing {} ...".format(fname))
        point = pd.concat([point,pd.read_csv(data_dir + f"/{fname}", names=col_names, usecols=[0, 1, 2, *range(9,12)])], ignore_index=True)

    pcd = create_pointcloud(point)

    print("Downsampling PointCloud ... ")
    downpcd = pcd.voxel_down_sample(voxel_size=downsample_voxel_size)
    print("-> Done.")

    print("result"
          f"\n before : {len(pcd.points)} points"
          f"\n after  : {len(downpcd.points)} points")

    # o3d.visualization.draw_geometries([pcd])
    o3d.visualization.draw_geometries([downpcd])
    if input("Create Mesh? [y/N]") == "y":
        mesh = create_mesh(downpcd)
        o3d.visualization.draw_geometries([mesh])

def create_pointcloud(point):
    with console.status("[bold green]Create PointCloud ...") as status:
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(point[["x","y","z"]].values)
        pcd.colors = o3d.utility.Vector3dVector(point[["r","g","b"]].values / 255)
    console.log("Create PointCloud [bold blue]Success!")
    return pcd

def create_mesh(pcd):

    # コピペ元サイト
    # https://tecsingularity.com/open3d/bpa/

    # estimate normals 法線推定
    with console.status("[bold green]Estimate Normals ...") as status:
        pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
    console.log("Estimate Normals -> [bold blue]Success!")

    # orient normals 点の方向性の一貫性の考慮
    with console.status("[bold green]Destinational Consistency ...") as status:
        pcd.orient_normals_consistent_tangent_plane(10)
        pcd.orient_normals_consistent_tangent_plane(10)
    console.log("Destinational Consistency -> [bold blue]Success!")

    # create mesh
    with console.status("[bold green]Create Mesh ..."):
        distances = pcd.compute_nearest_neighbor_distance()
        avg_dist = np.mean(distances)
        radius = 2 * avg_dist
        radii = [radius, radius * 2]
        mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(pcd, o3d.utility.DoubleVector(radii))
    console.log("Create Mesh -> [bold blue]Success!")
    return mesh

main()

