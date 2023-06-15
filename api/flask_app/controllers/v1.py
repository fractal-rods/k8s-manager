"""
This file contains only the blueprint which defines the API routes.
It is recommended that most of the logic that the routes use is 
to be defined in services/ to keep the codebase simple as possible.
This also leaves more space for middleware of the routes if something
like that is required in the future. If the routes start to clutter 
this file they should be moved and organized inside related folders.
"""

from flask import Blueprint, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
import os

from flask_app.services.service import (
    REQUEST,
    check_create_request,
    check_filename,
    send_request,
)


blueprint = Blueprint("v1", __name__, url_prefix="/api/v1")


@blueprint.route("/version", methods=["GET"])
def index():
    return jsonify({"version": "1.0"}), 200


@blueprint.route("/tasks", methods=["GET"])
def get_tasks():
    req = REQUEST.copy()
    req["cmd"] = "GET-TASKS"
    reply = send_request(req)

    return jsonify(reply), 200


@blueprint.route("/tasks/<string:task_name>", methods=["POST"])
def create_task(task_name: str):
    """
    1. check if the task_name does not exist
    2. create the task folder
    3. TODO: send the task to backend service to be scheduled
    """
    # TODO: add example when returning error

    try:
        file, command, return_type = check_create_request()
    except Exception:
        error = check_create_request()
        return error

    # TODO: move upload directory to server side.
    if task_name in os.listdir(current_app.config["UPLOAD_DIRECTORY"]):
        return jsonify({"status": "task already exists"}), 400

    if file and check_filename(file.filename):
        filename = secure_filename(file.filename)
        os.makedirs(os.path.join(current_app.config["UPLOAD_DIRECTORY"], task_name))
        file.save(
            os.path.join(current_app.config["UPLOAD_DIRECTORY"], task_name, filename)
        )

        req = REQUEST.copy()
        req["cmd"] = "CREATE-TASK"
        req["args"] = [task_name, command, return_type]
        send_request(req)

        # TODO: This should come as a reply from the server
        return jsonify({"status": f"task: {task_name} created successfuly."}), 201

    else:
        return jsonify({"status": "Error!"}), 500


@blueprint.route("/tasks/<string:task_name>", methods=["DELETE"])
def delete_task(task_name: str):
    # 1. check the task exists
    # 2. shutdown the task if it is running
    # 3. delete the task
    # 4. delete the task folder
    if task_name not in os.listdir(current_app.config["UPLOAD_DIRECTORY"]):
        return jsonify({"status": "task does not exist"}), 204

    req = REQUEST.copy()
    req["cmd"] = "DELETE-TASK"
    req["args"] = [task_name]
    reply = send_request(req)

    os.remove(
        os.path.join(
            current_app.config["UPLOAD_DIRECTORY"],
            task_name,
            os.listdir(os.path.join(current_app.config["UPLOAD_DIRECTORY"], task_name))[
                0
            ],
        )
    )
    os.rmdir(os.path.join(current_app.config["UPLOAD_DIRECTORY"], task_name))

    return (
        jsonify(
            {
                "status": f"task: {task_name} deleted successfuly from API host.",
                "backend-status": reply,
            }
        ),
        200,
    )


@blueprint.route("/tasks/<string:task_name>", methods=["PUT"])
def update_task(task_name: str):
    # TODO:
    # 1. check the task exists
    # 2. shutdown the task if it is running
    # 3. update the task

    return jsonify({"task": task_name}), 200


@blueprint.route("/tasks/<string:task_name>/start", methods=["POST"])
def start_task(task_name: str):
    # 1. check the task exists
    # 2. start the task if it is not running
    if task_name not in os.listdir(current_app.config["UPLOAD_DIRECTORY"]):
        return jsonify({"status": "task does not exist"}), 404

    req = REQUEST.copy()
    req["cmd"] = "START-TASK"
    req["args"] = [task_name]
    reply = send_request(req)

    return jsonify(reply), 200


@blueprint.route("/tasks/<string:task_name>/stop", methods=["POST"])
def stop_task(task_name: str):
    # 1. check the task exists
    # 2. stop the task if it is running
    if task_name not in os.listdir(current_app.config["UPLOAD_DIRECTORY"]):
        return jsonify({"status": "task does not exist"}), 404

    req = REQUEST.copy()
    req["cmd"] = "STOP-TASK"
    req["args"] = [task_name]
    reply = send_request(req)

    return jsonify(reply), 200 if reply["status"] == "ok" else 404


@blueprint.route("/tasks/<string:task_name>/status", methods=["GET"])
def task_status(task_name: str):
    # TODO:
    # 1. check the task exists
    # 2. get the task status
    if task_name not in os.listdir(current_app.config["UPLOAD_DIRECTORY"]):
        return jsonify({"status": "task does not exist"}), 404

    req = REQUEST.copy()
    req["cmd"] = "TASK-STATUS"
    req["args"] = [task_name]
    reply = send_request(req)

    return jsonify(reply), 200


@blueprint.route("/tasks/<string:task_name>/results", methods=["GET"])
def task_results(task_name: str):
    # TODO:
    # 1. check the task exists
    # 2. get the task results
    return jsonify({"task": task_name}), 200


@blueprint.route("/tasks/<string:task_name>/download", methods=["GET"])
def download_task(task_name: str):
    uploads = os.path.join(current_app.config["UPLOAD_DIRECTORY"], task_name)
    if len(os.listdir(uploads)) == 0:
        return jsonify({"status": "task does not exist"}), 404

    return send_from_directory(uploads, os.listdir(uploads)[0])
