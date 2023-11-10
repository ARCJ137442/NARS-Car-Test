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
    - 控制NARS的计算机实现
        - 实质上就是命令行读写
    - 将「感知」「操作」转换成纳思语
    """

    # * 常量集合 * #

    DEFAULT_SELF = '{SELF}'
    "默认用于表示「自我」的词项（用于纳思语表示）"

    NARS_LAUNCH_CMD_DICT = {
        "opennars": 'java -cp "*" org.opennars.main.Shell',
        "ONA": "NAR shell",
        "xiangnars": 'java -cp "*" nars.main_nogui.Shell'
    }
    "NARS启动命令字典，用于统一管理启动命令"

    # * 计算机实现对接 * #

    def __init__(self, output_hook, operation_hook) -> None:
        "构造函数"

        self.output_hook = output_hook
        "截获输出的钩子函数（优先触发，在NARS有输出时调用，传入输出的内容如'EXE: $0.04;0.00;0.08$ ^left([{SELF}])=null'）"

        self.operation_hook = operation_hook
        "截获NARS操作的钩子函数（在NARS输出操作时调用，传入操作的操作符如'^left'）"

        self.SELF = NARSImplementation.DEFAULT_SELF
        "表示「自我」的词项（用于纳思语表示）"

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
        self._put(f'cd {executables_path}')
        # 然后用命令行启动NARS
        self._put(NARSImplementation.NARS_LAUNCH_CMD_DICT[nars_type])
        # 降低音量
        self._put('*volume=0')
        # 启动NARS线程
        self._launch_thread()

    def process_kill(self):
        "结束进程（似乎并未用上）"
        self.process.send_signal(signal.CTRL_C_EVENT)
        self.process.terminate()

    def _put(self, str):
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

    # * 纳思语对接 * #
    def add_sense(self, sensor_name, status_name):
        '''告诉NARS现在指定感受器的状态
        # * NARS语句模板: <{感受器名} --> [状态名]>. :|:
          * 其中`:|:`代指时态「当前」
        '''
        self._put(f"<{'{' + sensor_name + '}'} --> [{status_name}]>. :|:")

    def add_operation_experience(self, operator_name, *operation_args):
        '''告诉NARS现在执行的操作
        # * NARS语句模板: <(*, {SELF}) --> 操作符>. :|:
          * 其中`:|:`代指时态「当前」
        '''
        self._put(
            f"<(*, {', '.join(operation_args)}) --> ^{operator_name}>. :|:")

    def add_self_status(self, status_name, is_negative):
        '''告诉NARS现在的「自我状态」
        # * NARS语句模板/正面: <{SELF} --> [状态名]>. :|:
        # * NARS语句模板/负面: <{SELF} --> [状态名]>. :|: %0%
          * 其中`:|:`代指时态「当前」
        '''
        self._put(
            f"<{self.SELF} --> [{status_name}]>. :|:" + (
                ' %0%' if is_negative else ''))  # ! 注意运算符优先级

    def add_self_status_goal(self, status_goal_name):
        '''告诉NARS现在的「自我状态目标」
        # * NARS语句模板: <{SELF} --> [状态名]>! :|:
          * 其中`:|:`代指时态「当前」
        '''
        self._put(f"<{self.SELF} --> [{status_goal_name}]>! :|:")

    def add_self_sensor_existence(self, *sensor_names):
        '''告诉NARS现在的「自我感受器」
        # * NARS语句模板: <{感受器名称...} --> {SELF}>. :|:
          * 其中`:|:`代指时态「当前」
        '''
        self._put(f"<{'{'+', '.join(sensor_names)+'}'} --> {self.SELF}>. :|:")
