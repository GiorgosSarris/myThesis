from flask import Blueprint, jsonify

alive_bp=Blueprint("alive_bp", __name__)

@alive_bp.route("/alive", methods=["GET"])
def server_alive():
    return jsonify({"status": "ok"})
