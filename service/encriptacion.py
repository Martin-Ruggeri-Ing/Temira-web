import rsa

def generar_claves():
    clave_publica, clave_privada = rsa.newkeys(2048)
    return clave_publica, clave_privada

def guardar_claves(clave_publica, clave_privada):
    with open('clave_publica.pem', 'wb') as archivo:
        archivo.write(clave_publica.save_pkcs1())
    with open('clave_privada.pem', 'wb') as archivo:
        archivo.write(clave_privada.save_pkcs1())

def leer_clave(tipo):
    clave = None
    with open(f'clave_{tipo}.pem', 'r') as archivo:
        clave = rsa.PrivateKey.load_pkcs1(archivo.read().encode()) if tipo == 'privada' else rsa.PublicKey.load_pkcs1(archivo.read().encode())
    return clave

if __name__ == '__main__':
    clave_publica, clave_privada = generar_claves()
    guardar_claves(clave_publica, clave_privada)


def desencriptar_archivo(clave_privada, archivo_encriptado):
    TAM_BLOQUE = 256  # Tamaño del bloque en bytes

    contenido_desencriptado = b""
    with open(archivo_encriptado, 'rb') as archivo:
        while True:
            bloque_encriptado = archivo.read(TAM_BLOQUE)
            if len(bloque_encriptado) == 0:
                break  # Se llegó al final del archivo encriptado

            bloque_desencriptado = rsa.decrypt(bloque_encriptado, clave_privada)
            contenido_desencriptado += bloque_desencriptado

    return contenido_desencriptado