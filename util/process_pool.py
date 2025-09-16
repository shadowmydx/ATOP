import multiprocessing
import subprocess
import os


def execute_task(target_queue, command):
    str_command = ' '.join(command)
    pid = os.getpid()
    try:      
        result = subprocess.run(
            str_command,
            capture_output=True,
            text=True,
            check=True,
            shell=True
        )
        target_queue.put((pid, result.stdout))
    except subprocess.CalledProcessError as e:
        error_message = f"Execution failed: {e.stderr}"
        target_queue.put((pid, error_message))
    except FileNotFoundError:
        error_message = f"Command '{command[0]}' not found."
        target_queue.put((pid, error_message))
    finally:
        target_queue.put((pid, None))


class ProcessPool:

    def __init__(self):
        self.processes = list()
        self.queue = multiprocessing.Queue()

    def execute(self, command, result_parser, total_tasks=1):
        finished_tasks = 0
        result_lst = list()
        for _ in range(total_tasks):
            process = multiprocessing.Process(
            target=execute_task,
            args=(self.queue, command)
            )
            self.processes.append(process)
            process.start()
        while finished_tasks != total_tasks:
            pid, result = self.queue.get()
            if result is None:
                finished_tasks += 1
            else:
                result_lst.append(result_parser(result))
        self.processes.clear()
        return result_lst
    

if __name__ == "__main__":
    test_pool = ProcessPool()
    test_result = test_pool.execute(["ls"], lambda x: x, 3)
    print(test_result)