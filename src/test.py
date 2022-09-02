#!/usr/bin/python3
from lib.client.Client import Client
import logging
import argparse
from threading import Thread
from random import *

filename_server = "enunciado.pdf"
filename_client = "files/copia_enunciado.pdf"

logging.basicConfig(format='[%(levelname)s]: %(message)s', level=logging.INFO) # Es el peor caso! 

def download():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', help='increase output verbosity')
    parser.add_argument('-q', '--quiet', help='decrease output verbosity')
    parser.add_argument('-H', '--host', help='server IP address')
    parser.add_argument('-p', '--port', help='server port')
    parser.add_argument('-d', '--dst', help='destination file path')
    parser.add_argument('-n', '--name', help='file name')

    args = parser.parse_args()

    if(args.dst and args.name):
        dir_client = args.dst+'/'+args.name
        name_server = args.name
    else:
        dir_client = filename_client
        name_server = filename_server 

    if(args.host and args.port):
        host = args.host
        port = args.port
    else:
        host = "127.0.0.1"
        port = 8080

    client = Client(host, port)
    client.download(filename_of_server = name_server, filename_in_client = dir_client)

def upload():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', help='increase output verbosity')
    parser.add_argument('-q', '--quiet', help='decrease output verbosity')
    parser.add_argument('-H', '--host', help='server IP address')
    parser.add_argument('-p', '--port', help='server port')
    parser.add_argument('-s', '--src', help='source file path')
    parser.add_argument('-n', '--name', help='source file path')

    args = parser.parse_args()

    if(args.src and args.name):
        dir_client = args.src+'/'+args.name
        name_server = args.name
    else:
        dir_client = filename_server
        name_server = filename_client 

    if(args.host and args.port):
        host = args.host
        port = args.port
    else:
        host = "127.0.0.1"
        port = 8080

    client = Client(host, port)
    client.upload(filename_of_client = 'files/enunciado.pdf', filename_in_server='copia_enunciado.pdf')

def main_up():
    upload()

def main_down():
    download()

if __name__ == '__main__': 
    try:        
        ths = []
        for i in range(0, 3):
            if (randint(1,10) <= 5):
                th = Thread(target=main_up)
            else:
                th = Thread(target=main_down)
            ths.append(th)
            
        for th in ths:
            th.start()

        for th in ths:
            th.join()

    except KeyboardInterrupt:
        logging.error("Fin.")
    except OSError as o:
        logging.error(f"An error occurred in client download: {str(o)}")
    except Exception as e:
        logging.error(f"An error occurred in client download: {str(e)}")
