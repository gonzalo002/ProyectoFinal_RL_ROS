import influxdb_client
import os
import time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

def store_robot_data(header, name, position, velocity, effort):
    # Configuración de InfluxDB
    token = "tKxtiDPzRK1EYCmNMgfabXwE-sLFpX6Dq7kaQl5LZaSD2-IbvoPR9aERvkJJUcz6ROKTZUi3UWYZj4lxlbgIFg=="
    org = "deusto"
    url = "https://deusto-influxdb-001-v2qrmk5znqme3f.eu-west-1.timestream-influxdb.amazonaws.com:8086"
    bucket = "Grupo_7"

    # Crear cliente
    client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    # Crear puntos para cada articulación
    for i, joint_name in enumerate(name):
        point = (
            Point("robot_joints")
            .tag("joint_name", joint_name)
            .field("position", position[i])
            .time(header.stamp.secs * 1000000000 + header.stamp.nsecs, WritePrecision.NS)
        )
        write_api.write(bucket=bucket, org=org, record=point)

def query_robot_data(time_range="-10m"):
    # Configuración de InfluxDB
    token = "tKxtiDPzRK1EYCmNMgfabXwE-sLFpX6Dq7kaQl5LZaSD2-IbvoPR9aERvkJJUcz6ROKTZUi3UWYZj4lxlbgIFg=="
    org = "deusto"
    url = "https://deusto-influxdb-001-v2qrmk5znqme3f.eu-west-1.timestream-influxdb.amazonaws.com:8086"

    # Crear cliente
    client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
    query_api = client.query_api()

    # Consulta
    query = f"""from(bucket: "Grupo_7")
        |> range(start: {time_range})
        |> filter(fn: (r) => r._measurement == "robot_joints")"""
    
    tables = query_api.query(query, org=org)
    
    return tables