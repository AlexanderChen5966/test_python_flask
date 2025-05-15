from flask import Flask, jsonify, request
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)

# 假資料
FAKE_DB = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"}
]

@app.route('/users', methods=['GET'])
def get_users():
    """
    Get all users
    ---
    responses:
      200:
        description: A list of users
        examples:
          application/json: [{"id":1,"name":"Alice"},{"id":2,"name":"Bob"}]
    """
    return jsonify(FAKE_DB)

@app.route('/users', methods=['POST'])
def add_user():
    """
    Add a new user
    ---
    parameters:
      - name: user
        in: body
        required: true
        schema:
          id: User
          required:
            - name
          properties:
            name:
              type: string
              description: The user's name
              example: Charlie
    responses:
      201:
        description: User created
        examples:
          application/json: {"id":3,"name":"Charlie"}
    """
    data = request.get_json()
    new_user = {
        "id": len(FAKE_DB) + 1,
        "name": data["name"]
    }
    FAKE_DB.append(new_user)
    return jsonify(new_user), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0')
