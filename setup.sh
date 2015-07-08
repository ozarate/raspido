#!/bin/bash


sudo apt-get update
sudo apt-get -y upgrade

echo "Instalando servidor FTP"
sudo apt-get install vsftpd
cp /home/pi/setup/vsftpd.conf /etc/vsftpd.conf
sudo service vsftpd restart


echo "Instalando servidor DHCP"
cp /home/pi/setup/interfaces /etc/network/interfaces
sudo apt-get install isc-dhcp-server
cp /home/pi/setup/dhcpd.conf /etc/dhcp/dhcpd.conf
cp /home/pi/setup/isc-dhcp-server /etc/default/isc-dhcp-server
sudo service isc-dhcp-server restart


echo "Instalando HOSTAP"
sudo apt-get install hostapd
cp /home/pi/setup/hostapd.conf /etc/hostapd/hostapd.conf
cp /home/pi/setup/hostapd /etc/default/hostapd


echo "Instalando libreria GPIO"
sudo apt-get -y install python-dev
cd /home/pi/setup/RPi.GPIO-0.5.11/
sudo python setup.py install

echo "Creando carpeta"
sudo mkdir /home/pi/ftpDocuments
sudo chown pi /home/pi/ftpDocuments/

echo "Instalando Raspido"
cp /home/pi/setup/raspido.py /usr/sbin/raspido
cd /usr/sbin/
sudo chmod +x raspido
cp /home/pi/setup/scratch.old /usr/bin/scratch.old
sudo chmod +x scratch.old

echo "Instalando arranque automatico - crontab"
cp /home/pi/setup/raspido /etc/init.d/raspido
cd /etc/init.d/
sudo chmod +x raspido
cd /home/pi/setup/
sudo crontab tarea.cron

echo -n "¿Desea reiniciar ahora? (SI/NO):" 
read RESPUESTA
case $RESPUESTA in
	S* | s*)
		RESPUESTA="SI";;
	N* | n*)
		RESPUESTA="NO";;
	*)
		RESPUESTA="";;
esac

if [ "$RESPUESTA" = "SI" ]
then
	sudo reboot
fi

