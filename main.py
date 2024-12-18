import os
import sys

import open3d as o3d
import numpy as np
import pandas as pd
import inquirer

from dotenv import load_dotenv
load_dotenv()

from rich.progress import track
from rich.console import Console
from rich.table import Table
console = Console()



# --- SET PARAMETERS --- #
data_dir = os.getenv("DATA_DIR")

# --- MAIN --- #
def main():
    point = load_csv(int(inquirer.text(message="How many files do you want to import?", validate=lambda _, c: 1<= int(c), default=10)))
    pcd = create_pointcloud(point)

    while True:

        # Textual UI
        menu = inquirer.List('mode', message="Select Visualization Mode", choices=["Show PointCloud", "Create Mesh", "Create .xyz File", "Exit Program", "Reload Program"])
        mode = inquirer.prompt([menu])["mode"]

        # Exit Program
        if mode == "Exit Program": sys.exit(0)

        # Reload Program
        elif mode == "Reload Program": main()
        is_ds = inquirer.confirm("Downsample PointCloud?", default=True)

        # Show PointCloud
        if mode == "Show PointCloud":
            if is_ds:
                downpcd = downsample(pcd)
                o3d.visualization.draw_geometries([downpcd])
                del downpcd
            else:
                o3d.visualization.draw_geometries([pcd])
        # Create Mesh
        elif mode == "Create Mesh":
            if is_ds:
                downpcd = downsample(pcd)
                mesh = create_mesh(downpcd)
            else:
                mesh = create_mesh(pcd)
            o3d.visualization.draw_geometries([mesh])
            del downpcd, mesh
        # Create .xyz File
        elif mode == "Create .xyz File":
            create_xyz(pcd)


# --- LOAD CSV --- #
def load_csv(num):
    col_names = ["x", "y", "z", "r", "g", "b"]
    point = pd.DataFrame()
    for i in track(range(num)):
        fname = f"Laser3D_Color_I_0{str(i).zfill(3)}_C12-L1.csv"
        print("importing {} ...".format(fname))
        point = pd.concat(
            [point, pd.read_csv(data_dir + f"/{fname}", names=col_names, usecols=[0, 1, 2, *range(9, 12)])],
            ignore_index=True)
    console.log("[bold blue]Success:","Import CSV")
    return point

# --- CREATE POINTCLOUD --- #
def create_pointcloud(point):

    # create pointcloud
    with console.status("[bold green]Create PointCloud ...") as status:
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(point[["x","y","z"]].values)
        pcd.colors = o3d.utility.Vector3dVector(point[["r","g","b"]].values / 255)
    console.log("[bold blue]Success:","Create PointCloud")
    return pcd

# --- CREATE MESH --- #
def create_mesh(pcd):

    # コピペ元サイト
    # https://tecsingularity.com/open3d/bpa/

    # estimate normals 法線推定
    radius = float(inquirer.text(message="Input Radius", validate=lambda _, c: 0 < float(c), default=0.1))
    max_nn = int(inquirer.text(message="Input Max NN", validate=lambda _, c: 0 < int(c), default=30))
    with console.status("[bold green]Estimate Normals ...") as status:
        pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=radius, max_nn=max_nn))
    console.log("[bold blue]Success:","Estimate Normals")

    # orient normals 点の方向性の一貫性の考慮
    with console.status("[bold green]Destinational Consistency ...") as status:
        pcd.orient_normals_consistent_tangent_plane(10)
    console.log("[bold blue]Success:","Destinational Consistency")

    # create mesh
    with console.status("[bold green]Create Mesh ..."):
        distances = pcd.compute_nearest_neighbor_distance()
        avg_dist = np.mean(distances)
        radius = 2 * avg_dist
        radii = [radius, radius * 2]
        mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(pcd, o3d.utility.DoubleVector(radii))
    console.log("[bold blue]Success:","Create Mesh")
    return mesh

# --- CREATE .xyz FILE --- #
def create_xyz(pcd):
    with console.status("[bold green]Create .xyz file ...") as status:
        o3d.io.write_point_cloud("pointcloud.xyz", pcd)
    console.log("[bold blue]Success:","Create .xyz File")
# --- DOWN SAMPLE --- #
def downsample(pcd):

    ds_mode_ui = inquirer.List('dsmode', message="Select DownSampling Mode", choices=["Voxel", "FPS", "Uniform"])
    ds_mode = inquirer.prompt([ds_mode_ui])["dsmode"]

    if ds_mode == "FPS":
        ds_param = int(inquirer.text(message="Input num_samples", validate=lambda _, c: 0 < int(c), default=100))
    elif ds_mode == "Uniform":
        ds_param = int(inquirer.text(message="Input k points ", validate=lambda _, c: 0 < int(c), default=30))
    elif ds_mode == "Voxel":
        ds_param = float(inquirer.text(message="Input Voxel Size ", validate=lambda _, c: 0 < float(c), default=0.1))

    # downsample pointcloud
    with console.status("[bold green]Downsampling PointCloud ...") as status:
        if ds_mode == "FPS":
            downpcd = pcd.farthest_point_down_sample(num_samples=ds_param)
        elif ds_mode == "Uniform":
            downpcd = pcd.uniform_down_sample(every_k_points=ds_param)
        elif ds_mode == "Voxel":
            downpcd = pcd.voxel_down_sample(voxel_size=ds_param)

    # result table
    result = Table(title="Downsampling Result")
    result.add_column("name"  ,justify="right",style="cyan")
    result.add_column("value" ,justify="left" ,style="magenta")
    result.add_row("before",f"{len(pcd.points)} points")
    result.add_row("after" ,f"{len(downpcd.points)} points")
    result.add_row("ratio" ,f"{(len(pcd.points) - len(downpcd.points)) / len(pcd.points) * 100} %")

    print("\n\n")
    console.print(result)
    print("\n\n")

    console.log("[bold blue]Success:","Downsampling PointCloud")

    return downpcd

main()

