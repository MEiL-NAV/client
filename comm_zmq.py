import zmq

def get_subscriber_sock(port, topic, conflate=True):
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    if conflate:
        socket.set(zmq.CONFLATE,1)
    socket.set(zmq.RCVTIMEO,10)
    socket.connect(f"tcp://localhost:{port}")
    socket.subscribe(topic)
    return socket