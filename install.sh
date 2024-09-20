#!/bin/bash

# Actualizar el sistema operativo
sudo apt-get update
sudo apt-get upgrade

# Instalar paquetes necesarios
sudo apt-get install virtualenv -y

# Crear el entorno virtual
virtualenv env

# Activar el entorno virtual
source env/bin/activate

# Actualizar pip
pip install --upgrade pip

# Instalar los requisitos del proyecto
pip3 install -r requirements.txt

