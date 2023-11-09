'''接口模块（NARS）
    原文参考：
    为实现OpenNARS 与虚拟环境的持续交互和行为反馈，定制开发了接口模块，用于将小车的感觉信息和
    移动指令与纳思语进行双向转译。同时，这也是实验者对OpenNARS“大脑活动”——其内部信息进行判别
    和记录的对外观察窗口。
    '''

import subprocess
import signal
import threading
import socket


class NARSImplementation:
    """NARS实现
    控制NARS的计算机实现
    实质上就是命令行读写
    """

    def __init__(self, output_hook, operation_hook) -> None:
        "构造函数"
        self.output_hook = output_hook
        "截获输出的钩子函数（优先触发，在NARS有输出时调用，传入输出的内容如'EXE: $0.04;0.00;0.08$ ^left([{SELF}])=null'）"
        self.operation_hook = operation_hook
        "截获NARS操作的钩子函数（在NARS输出操作时调用，传入操作的操作符如'^left'）"

    def _launch_thread(self):
        "开一个并行线程，负责读取nars的输出"
        self.read_line_thread = threading.Thread(
            target=self.read_line,
            args=(self.process.stdout,)
        )
        # 守护进程：在主进程结束时，子进程也会结束
        self.read_line_thread.daemon = True
        self.read_line_thread.start()

    def launch(self, nars_type, executables_path):
        """连接nars

        Args:
            nars_type (str): NARS类型，决定NARS实现的具体类型（如OpenNARS、ONA）
            executables_path (str): 「存放可执行文件的文件夹」的路径
        """
        self.process = subprocess.Popen(["cmd"], bufsize=1,
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        universal_newlines=True,
                                        shell=False)
        # 先找到可执行文件目录
        self.put(f'cd {executables_path}')
        # 然后用命令行启动NARS
        if nars_type == "opennars":
            self.put('java -cp "*" org.opennars.main.Shell')
        elif nars_type == 'ONA':
            self.put('NAR shell')
        elif nars_type == "xiangnars":
            self.put('java -cp "*" nars.main_nogui.Shell')
        self.put('*volume=0')
        self._launch_thread()

    def process_kill(self):
        "结束进程（似乎并未用上）"
        self.process.send_signal(signal.CTRL_C_EVENT)
        self.process.terminate()

    def put(self, str):
        "给nars传入信息"
        self.process.stdin.write(str + '\n')
        self.process.stdin.flush()

    def read_line(self, out):
        '''读取NARS实现的输出
        # !【2023-11-09 21:26:12】目前的实验中，对操作只截取操作符足矣
        '''
        for line in iter(out.readline, b'\n'):  # get operations
            # 调用钩子
            self.output_hook(line)  # 带换行符
            # 截获操作
            if line[0:3] == 'EXE':
                # 截取内容
                # * 样例：'EXE: $0.04;0.00;0.08$ ^left([{SELF}])=null\n'
                content = line.split(' ', 2)[2]
                # 截取操作符
                operator = content.split('(', 1)[0]
                # 调用钩子
                self.operation_hook(operator)
        # 关闭输出流
        out.close()
