# services.py
import queue
import socket
import logging
import multiprocessing
from server.helper.consts import (
    NUMBER_OF_SIMULTANEOUS_CLIENTS, READ_QUEUE_SIZE, WRITE_QUEUE_SIZE,
)
from server.helper.enums import ClientStatus


class TCPService:
    """
    This Service performs all the TCP Socket related tasks
    """

    host = ''
    port = ''
    soc = None

    def __init__(self, host, port):
        self.host = host
        self.port = int(port)

    def create_server(self):
        """
        Creates a Server
        """

        logging.info("Creating Server...")
        try:
            self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.soc.bind((self.host, self.port))  # bind host and port together
            logging.info("Server Created")
        except Exception as e:
            logging.error(e)
            raise e

    def start_listening(self, clients=NUMBER_OF_SIMULTANEOUS_CLIENTS):
        """
        Starts Listening for clients
        :param clients: configure how many clients the server can listen to simultaneously
        """

        try:
            self.soc.listen(clients)
            logging.info("Server is Up" +
                         "IP: ", self.host,
                         "Port: ", self.port)
            print("Server is Up" + "IP: ", self.host, "Port: ", self.port)
        except Exception as e:
            logging.error(e)
            raise e


class MessageProcessingService:
    def __init__(self, client_interface):
        logging.info('Creating threads and queue for message processing...')
        self.client_interface = client_interface
        self.read_thread = multiprocessing.Process(target=self.read_message)
        self.process_thread = multiprocessing.Process(target=self.process_message)
        self.write_thread = multiprocessing.Process(target=self.send_message)
        self.read_queue = multiprocessing.Queue(maxsize=READ_QUEUE_SIZE)
        self.write_queue = multiprocessing.Queue(maxsize=WRITE_QUEUE_SIZE)
        self._terminate = False

    def __enter__(self):
        self.start()
        return self

    def __exit__(self):
        self.terminate()
        self.join()

    def start(self):
        logging.info('Starting Threads...')
        self.read_thread.start()
        self.process_thread.start()
        self.write_thread.start()

    def terminate(self):
        logging.info('Terminating Threads...')
        self._terminate = True
        if self.read_thread:
            self.read_thread.terminate()
        if self.process_thread:
            self.process_thread.terminate()
        if self.write_thread:
            self.write_thread.terminate()

    def join(self):
        logging.info('Joining Threads')
        self.read_thread.join()
        self.process_thread.join()
        self.write_thread.join()
