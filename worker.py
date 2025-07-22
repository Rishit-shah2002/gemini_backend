from redis import Redis
from rq import SimpleWorker, Queue
from dotenv import load_dotenv
load_dotenv()
redis_conn = Redis(host="localhost", port=6379)

listen_queues = ['default']

if __name__ == '__main__':
    worker = SimpleWorker(queues=listen_queues, connection=redis_conn)
    worker.work()