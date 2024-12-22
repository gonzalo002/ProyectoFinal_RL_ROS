import rospy
from copy import deepcopy
from datetime import datetime
import pytz
from std_msgs.msg import Int8
from sensor_msgs.msg import JointState
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

class InfluxLoader():
    def __init__(self) -> None:
        """
        Inicializa el nodo de ROS y configura la conexión a InfluxDB.
        
        """
        rospy.init_node('influx_node')

        # Configuración de conexión a InfluxDB
        # Token para la autenticación en InfluxDB
        self.token = "PF5pM9ch_T67d9UihOqu00u0CUU6164ZR9_fnKsEBWDSKt_0_jI20i6VXynDx8-yUfYAdtsutnMLYOnipLrXnQ=="
        # Organización en InfluxDB
        self.org = "deusto"
        # URL de InfluxDB
        self.url = "https://deusto-influxdb-001-v2qrmk5znqme3f.eu-west-1.timestream-influxdb.amazonaws.com:8086"
        # Bucket donde se almacenarán los datos
        self.bucket = "Grupo_7"
        
        # Crear el cliente de InfluxDB y la API de escritura
        self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

        # Variables de control y suscripción a los tópicos de ROS
        self.flag = False  # Bandera para controlar el movimiento del robot
        self.subscriber_1 = rospy.Subscriber('control_movimiento', Int8, self.callback_1)
        self.subscriber_2 = rospy.Subscriber('joint_states', JointState, self.callback_2)
        
        # Inicialización de las variables de datos
        self.jointdata = JointState()  # Datos actuales de las articulaciones
        self.previous_state = False  # Estado anterior de la bandera 'flag'
        self.date = int(datetime.now().timestamp())


    def callback_1(self, data: Int8) -> None:
        """
        Función callback para recibir el control de movimiento del robot.

        Parámetros:
        - data (Int8): El mensaje de control de movimiento recibido desde ROS.
        
        Salida:
        - None: Esta función no retorna valores, solo modifica el estado interno de la clase.
        """
        if data.data == 1:
            self.flag = True
        else:
            self.flag = False


    def callback_2(self, data: JointState) -> None:
        """
        Función callback para actualizar los datos de las articulaciones.

        Parámetros:
        - data (JointState): El mensaje de tipo JointState recibido desde ROS.
        
        Salida:
        - None: Esta función no retorna ningún valor, solo modifica el estado interno de la clase.
        """
        self.jointdata = deepcopy(data)


    def store_robot_data(self, joint_state: JointState) -> None:
        """
        Almacena los datos de las articulaciones del robot en InfluxDB.
        
        Parámetros:
        - joint_state (JointState): El estado de las articulaciones a almacenar en la base de datos.
        
        Salida:
        - None: Esta función no retorna valores. Los datos son almacenados directamente en InfluxDB.
        """
        date = deepcopy(self.date)
        for i, joint_name in enumerate(joint_state.name):
            fecha = datetime.now(pytz.timezone('Europe/Madrid'))
            try:
                point = (
                    Point(f"Trayectory_{date}")  # Nombre de la medición
                    .field("position", joint_state.position[i])  # Campo con la posición de la articulación
                    .tag("joint_name", joint_name)  # Etiqueta con el nombre de la articulación
                    .field("velocity", joint_state.velocity[i])
                    .tag("joint_name", joint_name) 
                    .field("effort", joint_state.effort[i])
                    .tag("joint_name", joint_name)
                    .time(fecha, WritePrecision.NS)  # Marca temporal
                )
            except: # Simulación
                point = (
                    Point(f"Trayectory_{date}")  # Nombre de la medición
                    .field("position", joint_state.position[i])  # Campo con la posición de la articulación
                    .tag("joint_name", joint_name)  # Etiqueta con el nombre de la articulación
                    .field("velocity", 0.0)
                    .tag("joint_name", joint_name) 
                    .field("effort", 0.0)
                    .tag("joint_name", joint_name)
                    .time(fecha, WritePrecision.NS)  # Marca temporal
                )
            try:
                # Escribir el punto de datos en InfluxDB
                self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            except Exception as e:
                rospy.logerr(f"Error al escribir en InfluxDB: {e}")

        print('Datos guardados')

    def query_robot_data(self, time_range: str = "-10m") -> list:
        """
        Consulta los datos de las articulaciones almacenados en InfluxDB dentro de un rango de tiempo.
        
        Parámetros:
        - time_range (str): Rango de tiempo de la consulta en formato de cadena, e.g., "-10m" para los últimos 10 minutos.
        
        Salida:
        - list: Una lista de las tablas de resultados obtenidas de la consulta en InfluxDB.
        """
        query_api = self.client.query_api()
        query = f"""from(bucket: "Grupo_7")
            |> range(start: {time_range})  # Rango de tiempo a consultar
            |> filter(fn: (r) => r._measurement == "robot_joints")"""  # Filtrar solo las mediciones de las articulaciones
        
        tables = query_api.query(query, org=self.org)
        return tables


    def main(self) -> None:
        """
        Bucle principal que procesa y almacena los datos de las articulaciones del robot.
        
        Salida:
        - None: Este método no retorna valores. Mantiene el bucle ejecutándose hasta que ROS se cierre.
        """
        rate = rospy.Rate(10)  # Define la tasa de ejecución del bucle (10 Hz)
        
        while not rospy.is_shutdown():  # Bucle de ejecución hasta que ROS se cierre
            save_info = deepcopy(self.flag)  # Guardar el estado actual de la bandera 'flag'
            # Si 'flag' es True (movimiento), almacenar los datos actuales de las articulaciones or all(abs(v) < 0.1 for v in self.jointdata.velocity)
            if save_info:
                jointdata = self.jointdata
                self.store_robot_data(jointdata)
            else:
                self.date = int(datetime.now().timestamp())

            # Actualizar el estado anterior de la bandera 'flag'
            self.previous_state = deepcopy(save_info)

            # Dormir hasta el siguiente ciclo del bucle
            rate.sleep()


# Función principal
if __name__ == '__main__':
    # Instanciar la clase y ejecutar el método main
    coso = InfluxLoader()
    coso.main()
