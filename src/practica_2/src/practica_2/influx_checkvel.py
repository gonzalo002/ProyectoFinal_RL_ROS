import rospy
from copy import deepcopy
from datetime import datetime
from sensor_msgs.msg import JointState
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

class InfluxLoader():
    def __init__(self) -> None:
        """
        Inicializa el nodo de ROS y configura la conexión a InfluxDB.
        """
        rospy.init_node('publicador')

        # Configuración de conexión a InfluxDB
        # Token para la autenticación en InfluxDB
        self.token = "CjYRQt0YcxGfqAUMi-_ImVRBbvlpFZx-25E9U3iKp6T6w2Ky4iBraa2v-uRGI3Nn88_10jo_9flCpOKmy9Tv_Q=="
        # Organización en InfluxDB
        self.org = "deusto"
        # URL de InfluxDB
        self.url = "https://deusto-influxdb-001-v2qrmk5znqme3f.eu-west-1.timestream-influxdb.amazonaws.com:8086"
        # Bucket donde se almacenarán los datos
        self.bucket = "Grupo_7"
        
        # Crear el cliente InfluxDB y la API de escritura
        self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

        # Variable de control para saber si se debe almacenar datos
        self.flag = False
        self.date = int(datetime.now().timestamp())
        
        # Suscripción al tópico 'joint_states'
        self.subscriber_2 = rospy.Subscriber('joint_states', JointState, self.callback_2)
        
        # Variables para almacenar los estados anteriores y actuales de las articulaciones
        self.prev_jointdata = JointState()
        self.jointdata = JointState()


    def callback_2(self, data: JointState) -> None:
        """
        Función callback para actualizar los datos de las articulaciones.
        
        Parámetros:
        - data (JointState): El mensaje de tipo JointState recibido desde ROS.
        
        Salida:
        - None: Esta función no retorna ningún valor.
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
        
        for i, joint_name in enumerate(joint_state.name):
                
            point = (
                Point(f"Trayectory_{self.date}")  # Nombre de la medición
                .field("position", joint_state.position[i])  # Campo con la posición de la articulación
                .tag("joint_name", joint_name)  # Etiqueta con el nombre de la articulación
                .field("velocity", joint_state.velocity[i])
                .tag("joint_name", joint_name) 
                .field("effort", joint_state.effort[i])
                .tag("joint_name", joint_name)
                .time(joint_state.header.stamp.secs * 1000000000 + joint_state.header.stamp.nsecs, WritePrecision.NS)  # Marca temporal
            )

            try:
                # Escribir el punto de datos en InfluxDB
                self.write_api.write(bucket=self.bucket, org=self.org, record=point)
                print('Datos guardados')
            except Exception as e:
                rospy.logerr(f"Error al escribir en InfluxDB: {e}")


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
        save_data = False  # Variable para controlar cuándo guardar los datos
        
        while not rospy.is_shutdown():  # Bucle de ejecución hasta que ROS se cierre
            # Verifica si las articulaciones están detenidas (velocidad es cero)
            if all(abs(v) < 0.1 for v in self.jointdata.velocity):
                self.prev_jointdata = deepcopy(self.jointdata)  # Guarda el estado actual antes del movimiento
                self.flag = False
            else:
                self.flag = True  # El robot está en movimiento
                print('moviendo')

            # Guardar el primer estado antes del movimiento (si no se ha guardado ya)
            if self.flag and not save_data:
                self.date = int(datetime.now().timestamp())
                jointdata_prev = deepcopy(self.prev_jointdata)
                self.store_robot_data(jointdata_prev)

            # Guardar el último estado tras la parada del robot
            if save_data and not self.flag:
                jointdata_post = deepcopy(self.jointdata)
                self.store_robot_data(jointdata_post)

            # Actualizar el estado de la variable de control
            save_data = deepcopy(self.flag)

            rate.sleep()  # Dormir hasta el siguiente ciclo del bucle


# Función principal
if __name__ == '__main__':
    # CjYRQt0YcxGfqAUMi-_ImVRBbvlpFZx-25E9U3iKp6T6w2Ky4iBraa2v-uRGI3Nn88_10jo_9flCpOKmy9Tv_Q==
    # Instanciar la clase y ejecutar el método main
    coso = InfluxLoader()
    coso.main()
