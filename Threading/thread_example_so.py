"""
https://stackoverflow.com/questions/41526832/pyqt5-qthread-signal-not-working-gui-freeze

The main concepts necessary to understand multi-thread programming in PyQt are the following:

Qt threads have their own event loop (specific to each thread). The main thread, aka the GUI thread, is also a QThread, and its event loop is managed by that thread.
Signals between threads are transmitted (asynchronously) via the receiving thread's event loop. Hence responsiveness of GUI or any thread = ability to process events. E.g., if a thread is busy in a function loop, it can't process events, so it won't respond to signals from the GUI until the function returns.
If a worker object (method) in a thread may have to change its course of action based on signals from the GUI (say, to interrupt a loop or a wait), it must call processEvents() on the QApplication instance. This will allow the QThread to process events, and hence to call slots in response to async signals from the GUI. Note that QApplication.instance().processEvents() seems to call processEvents() on every thread, if this is not desired then QThread.currentThread().processEvents() is a valid alternative.
A call to QThread.quit() does not immediately quit its event loop: it must wait for currently executing slot (if any) to return. Hence once a thread is told to quit, you must wait() on it. So aborting a worker thread usually involves signaling it (via a custom signal) to stop whatever it is doing: this requires a custom signal on a GUI object, a connection of that signal to a worker slot, and worker work method must call thread's processEvents() to allow the emitted signal to reach the slot while doing work.
"""


import time
import sys

from PySide2.QtCore import QObject, QThread, Signal, Slot
from PySide2.QtWidgets import QApplication, QPushButton, QTextEdit, QVBoxLayout, QWidget


def trap_exc_during_debug(*args):
    # when app raises uncaught exception, print info
    print(args)


# install exception hook: without this, uncaught exception would cause application to exit
sys.excepthook = trap_exc_during_debug


class Worker(QObject):
    """
    Must derive from QObject in order to emit signals, connect slots to other signals, and operate in a QThread.
    """

    sig_step = Signal(int, str)  # worker id, step description: emitted every step through work() loop
    sig_done = Signal(int)  # worker id: emitted at end of work()
    sig_msg = Signal(str)  # message to be shown to user

    def __init__(self, id: int):
        super().__init__()
        self.__id = id
        self.__abort = False

    @Slot()
    def work(self):
        """
        Pretend this worker method does work that takes a long time. During this time, the thread's
        event loop is blocked, except if the application's processEvents() is called: this gives every
        thread (incl. main) a chance to process events, which in this sample means processing signals
        received from GUI (such as abort).
        """
        thread_name = QThread.currentThread().objectName()
        thread_id = int(QThread.currentThreadId())  # cast to int() is necessary
        self.sig_msg.emit('Running worker #{} from thread "{}" (#{})'.format(self.__id, thread_name, thread_id))

        for step in range(100):
            time.sleep(0.1)
            self.sig_step.emit(self.__id, 'step ' + str(step))

            # check if we need to abort the loop; need to process events to receive signals;
            app.processEvents()  # this could cause change to self.__abort
            if self.__abort:
                # note that "step" value will not necessarily be same for every thread
                self.sig_msg.emit('Worker #{} aborting work at step {}'.format(self.__id, step))
                break

        self.sig_done.emit(self.__id)

    def abort(self):
        self.sig_msg.emit('Worker #{} notified to abort'.format(self.__id))
        self.__abort = True


class MyWidget(QWidget):
    NUM_THREADS = 5

    # sig_start = Signal()  # needed only due to PyCharm debugger bug (!)
    sig_abort_workers = Signal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Thread Example")
        form_layout = QVBoxLayout()
        self.setLayout(form_layout)
        self.resize(400, 800)

        self.button_start_threads = QPushButton()
        self.button_start_threads.clicked.connect(self.start_threads)
        self.button_start_threads.setText("Start {} threads".format(self.NUM_THREADS))
        form_layout.addWidget(self.button_start_threads)

        self.button_stop_threads = QPushButton()
        self.button_stop_threads.clicked.connect(self.abort_workers)
        self.button_stop_threads.setText("Stop threads")
        self.button_stop_threads.setDisabled(True)
        form_layout.addWidget(self.button_stop_threads)

        self.log = QTextEdit()
        form_layout.addWidget(self.log)

        self.progress = QTextEdit()
        form_layout.addWidget(self.progress)

        QThread.currentThread().setObjectName('main')  # threads can be named, useful for log output
        self.__workers_done = None
        self.__threads = None

    def start_threads(self):
        self.log.append('starting {} threads'.format(self.NUM_THREADS))
        self.button_start_threads.setDisabled(True)
        self.button_stop_threads.setEnabled(True)

        self.__workers_done = 0
        self.__threads = []
        for idx in range(self.NUM_THREADS):
            worker = Worker(idx)
            thread = QThread()
            thread.setObjectName('thread_' + str(idx))
            self.__threads.append((thread, worker))  # need to store worker too otherwise will be gc'd
            worker.moveToThread(thread)

            # get progress messages from worker:
            worker.sig_step.connect(self.on_worker_step)
            worker.sig_done.connect(self.on_worker_done)
            worker.sig_msg.connect(self.log.append)

            # control worker:
            self.sig_abort_workers.connect(worker.abort)

            # get read to start worker:
            # self.sig_start.connect(worker.work)  # needed due to PyCharm debugger bug (!); comment out next line
            thread.started.connect(worker.work)
            thread.start()  # this will emit 'started' and start thread's event loop

        # self.sig_start.emit()  # needed due to PyCharm debugger bug (!)

    @Slot(int, str)
    def on_worker_step(self, worker_id: int, data: str):
        self.log.append('Worker #{}: {}'.format(worker_id, data))
        self.progress.append('{}: {}'.format(worker_id, data))

    @Slot(int)
    def on_worker_done(self, worker_id):
        self.log.append('worker #{} done'.format(worker_id))
        self.progress.append('-- Worker {} DONE'.format(worker_id))
        self.__workers_done += 1
        if self.__workers_done == self.NUM_THREADS:
            self.log.append('No more workers active')
            self.button_start_threads.setEnabled(True)
            self.button_stop_threads.setDisabled(True)
            # self.__threads = None

    @Slot()
    def abort_workers(self):
        self.sig_abort_workers.emit()
        self.log.append('Asking each worker to abort')
        for thread, worker in self.__threads:  # note nice unpacking by Python, avoids indexing
            thread.quit()  # this will quit **as soon as thread event loop unblocks**
            thread.wait()  # <- so you need to wait for it to *actually* quit

        # even though threads have exited, there may still be messages on the main thread's
        # queue (messages that threads emitted before the abort):
        self.log.append('All threads exited')


if __name__ == "__main__":
    app = QApplication([])

    form = MyWidget()
    form.show()

    sys.exit(app.exec_())