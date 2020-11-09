from multiprocessing.managers import BaseManager
import queue
queue = queue.Queue()
class QueueManager(BaseManager): 
    pass
QueueManager.register('get_queue', callable=lambda:queue)
m = QueueManager(address=('', 50000), authkey=b'abracadabra')
s = m.get_server()
s.serve_forever()


#put
from multiprocessing.managers import BaseManager
class QueueManager(BaseManager): 
    pass
QueueManager.register('get_queue')
m = QueueManager(address=('foo.bar.org', 50000), authkey=b'abracadabra')
m.connect()
queue = m.get_queue()
queue.put('hello')

# get

from multiprocessing.managers import BaseManager
class QueueManager(BaseManager): 
    pass
QueueManager.register('get_queue')
m = QueueManager(address=('foo.bar.org', 50000), authkey=b'abracadabra')
m.connect()
queue = m.get_queue()
queue.get()