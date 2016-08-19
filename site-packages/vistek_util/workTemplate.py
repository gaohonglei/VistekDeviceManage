#!/usr/bin/env python
# -*- coding=utf-8 -*-

import time, sys
try:
    import Queue
except:
    import queue as Queue
from threading import Thread

class Worker(Thread):
    worker_count = 0
    def __init__( self, workQueue, resultQueue, timeout = 0, **kwds):
        Thread.__init__( self, **kwds )
        self.id = Worker.worker_count
        Worker.worker_count += 1
        self.setDaemon( True )
        self.workQueue = workQueue
        self.resultQueue = resultQueue
        self.timeout = timeout
        self.start( )
    def run( self ):
        ''' the get-some-work, do-some-work main loop of worker threads '''
        while True:
            try:
                callable, args, kwds = self.workQueue.get(timeout=self.timeout)
                res = callable(*args, **kwds)
                #print "worker[%2d]: %s" % (self.id, str(res) )
                print("worker[{0}]: {1}".format(self.id, str(res)))
                self.resultQueue.put( res )
            except Queue.Empty:
                continue
            except :
                #print 'worker[%2d]' % self.id, sys.exc_info()[:2]
                print("worker[{0}] {1}".format(self.id, sys.exc_info()[:2]))
            time.sleep(0.1)

class WorkerManager:
    def __init__( self, num_of_workers=10, timeout = 1):
        self.workQueue = Queue.Queue()
        self.resultQueue = Queue.Queue()
        self.workers = []
        self.timeout = timeout
        self._recruitThreads( num_of_workers )
    def _recruitThreads( self, num_of_workers ):
        for i in range( num_of_workers ):
            worker = Worker( self.workQueue, self.resultQueue, self.timeout )
            self.workers.append(worker)
    def result_queue_size(self):
        return self.resultQueue.qsize()
    def result_queue_empty(self):
        return self.resultQueue.empty()
    def wait_for_complete( self):
        # ...then, wait for each of them to terminate:
        while len(self.workers):
            worker = self.workers.pop()
            #worker.join( )
            #if not worker.isAlive():
                #worker.start()
            if worker.isAlive() and not self.workQueue.empty():
                self.workers.append( worker )
        print("{0}, All jobs are are completed.".format(time.asctime(time.localtime(time.time()))))
    def add_job( self, callable, *args, **kwds ):
        self.workQueue.put( (callable, args, kwds) )
    def get_result( self, *args, **kwds ):
        return self.resultQueue.get( *args, **kwds )


