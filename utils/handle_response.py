from flask import jsonify


class ResponseHandler:
    @staticmethod
    def success(data=None, message="Success", status=200):
        # Merge data with the message into the top-level JSON
        response = {"message": message}
        if isinstance(data, dict):  # Only merge if data is a dictionary
            response.update(data)
        return jsonify(response), status

    @staticmethod
    def error(message="Error", status=400, data=None):
        response = {"message": message}
        if data is not None:
            response["data"] = data
        return jsonify(response), status
