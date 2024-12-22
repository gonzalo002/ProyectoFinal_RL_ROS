def crear_mensaje(mensaje:str, tipo:str='ERROR', nombre_clase:str=""):
    # --- CÓDIGO COLORES ---
    c = {
        "ERROR":   "\033[31m",  # Rojo
        "SUCCESS": "\033[32m",  # Verde
        "WARN":    "\033[33m",  # Amarillo
        "INFO":    "\033[0m" ,  # Restablecer
        "RESET":   "\033[0m" ,  # Restablecer
        "INPUT":   "\033[35m",  # Magenta
    }


    if tipo == "INPUT":
        return input(f"{c[tipo]}[{tipo.rjust(7)}] [{nombre_clase.rjust(20)}]: {mensaje} {c['RESET']}")
    else:
        print(f"{c[tipo]}[{tipo.rjust(7)}] [{nombre_clase.rjust(20)}]: {mensaje} {c['RESET']}")