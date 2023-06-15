from flask import jsonify, request
import zmq
import os

ALLOWED_EXTENSIONS = set(
    [
        "py",
    ]
)

REQUEST_TIMEOUT = 2500
REQUEST_RETRIES = 3
REQUEST = {"cmd": None, "args": None}


def check_filename(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def send_request(req: dict):
    """
    This method is for sending request for the backend-service
    it capsulates lot of the logic required to make a successful
    request. The method always returns a reply even when the server doesn't
    respond.
    """

    __context = zmq.Context.instance()
    _client: zmq.Socket = __context.socket(zmq.REQ)
    _client.connect(os.environ.get("SOCKET_ADDRESS", "tcp://0.0.0.0:5555"))

    _poll = zmq.Poller()
    _poll.register(_client, zmq.POLLIN)

    sequence = 0
    retries_left = REQUEST_RETRIES
    while retries_left:
        sequence += 1

        print("Sending request to server")
        _client.send_json(req)

        expect_reply = True
        while expect_reply:
            socks = dict(_poll.poll(REQUEST_TIMEOUT))
            if socks.get(_client) == zmq.POLLIN:
                reply = _client.recv_json()
                # No reply -> Try again.
                if not reply:
                    break
                # Reply received so stop.
                else:
                    print("Response from server", reply)
                    retries_left = REQUEST_RETRIES
                    expect_reply = False
            else:
                reply = {"Error": "No response from server"}
                print("No response from server, retrying…")
                _client.setsockopt(zmq.LINGER, 0)
                _client.close()
                _poll.unregister(_client)
                retries_left -= 1
                if retries_left == 0:
                    print("Server seems to be offline, abandoning")
                    break
                print("Reconnecting and resending request")
                # Create new connection
                _client: zmq.Socket = __context.socket(zmq.REQ)
                _client.connect(os.environ.get("SOCKET_ADDRESS", "tcp://0.0.0.0:5555"))
                _poll.register(_client, zmq.POLLIN)
                _client.send_json(req)

        return reply


def check_create_request():
    if "file" not in request.files:
        return jsonify({"error": "file required in the request"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "no file"}), 400

    if "cmd" not in request.form:
        return jsonify({"error": "command to run is not specified"}), 400

    command = request.form["cmd"]

    if "rt" not in request.form:
        return jsonify({"error": "return type is not specified"}), 400

    return_type = request.form["rt"]

    return file, command, return_type
