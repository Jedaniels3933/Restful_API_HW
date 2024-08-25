from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
from connection import connection, Error


gym = Flask(__name__)
ma = Marshmallow(gym)

class Memberschema(ma.Schema):
    id = fields.Int(dump_only = True)
    member_name = fields.String(required=True)

    class Meta:
        fields = ("id", "member_name")

member_schema = Memberschema()
members_schema = Memberschema(many = True)

@gym.route('/')

def home():
    return " Welcome to the Gym, time to get wrecked and bulk up brah!"

@gym.route('/members', methods = ['GET'])

def get_members():
    conn= connection()
    if conn is not None:
        try:
            cursor = conn.cursor(dictionary =True)
            query = "SELECT * FROM members"
            cursor.execute(query)
            members = cursor.fetchall()
        except Error as e:
            return jsonify ({"error": e})
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close() 
                return members_schema.jsonify(members)


@gym.route("/members/<int:id>", methods = ['DELETE'])
def delete_member(id):

    conn = connection()
    if conn is not None:
        try:
            cursor = conn.cursor()

            check_query = "SELECT * FROM members WHERE id = %s;"
            cursor.execute(check_query, (id,))
            member = cursor.fetchone()
            if not member:
                return jsonify({"error": "member was not found"}), 400
            
            query = "DELETE FROM members WHERE id = %s;"
            cursor.execute(query, (id,))
            conn.commit()

            return jsonify({"message": f"Member {id} deleted !"})
        except Error as e:
            return jsonify(e.messages), 500
        
        finally:
            cursor.close();conn.close()

    else:
        return jsonify({"error": "Database connection failed"}), 500

@gym.route("/members", methods = ['POST'])
def add_member():
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    conn = connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            new_member = (member_data['member_name'])
            query = "INSERT INTO members (member_name) VALUES (%s)"
            cursor.execute(query, new_member)
            conn.commit()
            return jsonify({'message': 'New member created successfully'}), 200
        except Error as e:
            return jsonify(e.messages), 500
        finally:
            cursor.close(); conn.close() 
        
    else:
        return jsonify ({'error': 'Database connection failed'}), 404
    
@gym.route("/members/<int:id>", methods = ['PUT']) 
def update_member(id):
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    conn = connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            check_query = "SELECT * FROM members WHERE id = %s;"
            cursor.execute(check_query, (id,))
            member = cursor.fetchone()
            if not member:
                return jsonify({"error": "Member was not found."}), 404
            updated_member = (member_data['member_name'],id)
            query = "UPDATE members SET member_name = %s  WHERE id = %s;"
            cursor.execute(query, updated_member)
            conn.commit()
            return jsonify({'message': f"Successfully updated member {id}"}), 200
        except Error as e:
            return jsonify(e.messages), 500
        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({"error": "Database connection failed"}), 500

if __name__ == '__main__':
    gym.run(debug=True)