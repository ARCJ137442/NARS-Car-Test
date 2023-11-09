import threading
import subprocess
import signal
import socket
import time


def get_jar_launch_cmd(file_name):
    return f'java -jar {file_name}'


class NARS:
    def __init__(
        self,
        host, port,
        # self.add_to_cmd('java -Xmx2048m -jar opennars.jar')
        launch_cmd=get_jar_launch_cmd('opennars.jar')
    ):  # nars_type: 'opennars' or 'ONA'
        # set too large will get delayed and slow down the game
        self.inference_cycle_frequency = 1
        self.operation_left = False
        self.operation_right = False
        self.launch_nars(host, port, launch_cmd)
        self.launch_thread()

    def launch_sever(self):
        while True:
            data = self.car.readline()
            sensorinfo = data.decode().strip()  # 去掉\n
            if sensorinfo == 'quit':
                self.process_kill()
                break
            self.add_to_cmd(sensorinfo)
        self.conn.close()

    def launch_nars(
        self,
        host, port,
        # self.add_to_cmd('java -Xmx2048m -jar opennars.jar')
        launch_cmd
    ):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))
        server.listen(1)
        self.conn, _ = server.accept()
        self.car = self.conn.makefile('rwb')
        self.process = subprocess.Popen(["cmd"], bufsize=1,
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        universal_newlines=True,  # convert bytes to text/string
                                        shell=False)

        self.add_to_cmd(launch_cmd)
        # self.add_to_cmd('NAR shell')
        self.add_to_cmd('*volume=0')

    def launch_thread(self):
        self.read_line_thread = threading.Thread(target=self.read_line,
                                                 args=(self.process.stdout,))
        self.read_line_thread.daemon = True  # thread dies with the exit of the program
        self.read_line_thread.start()

    def read_line(self, out):  # read line without blocking
        for line in iter(out.readline, b'\n'):  # get operations
            if (line[0:3] == 'EXE'):
                print(time.strftime("$___%H:%M:%S\t", time.localtime()), end='')
                print(line)  # 条件输出NARS信息
                subline = line.split(' ', 2)[2]
                operation = subline.split('(', 1)[0]
                self.conn.send(operation.encode() + b'\n')
            else:
                print(time.strftime("#___%H:%M:%S\t", time.localtime()), end='')
                print(line)
        out.close()

    def process_kill(self):
        self.process.send_signal(signal.CTRL_C_EVENT)
        self.process.terminate()

    def add_to_cmd(self, str):
        self.process.stdin.write(str + '\n')
        self.process.stdin.flush()

    def add_inference_cycles(self, num):
        self.process.stdin.write(f'{num}\n')
        self.process.stdin.flush()


def main(host, port, launch_cmd):
    nars = NARS(host, port,
                launch_cmd=launch_cmd)
    nars.launch_sever()
    print('NARS服务器已于')


if __name__ == '__main__':
    main(
        host='127.0.0.1',
        port=8888,
        launch_cmd=get_jar_launch_cmd('opennars1.jar')
    )
