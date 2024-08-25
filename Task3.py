from flask import Flask, jsonify, request
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError
from connection import connection, Error

workouts = Flask(__name__)
ma = Marshmallow(workout)

class Workoutschema(ma.Schema):
    id = fields.Int(dump_only = True)
    workout_type= fields.String(required=True)
    duration= fields.String(required=True)
    # members_id = fields.Int(dump_only=True)
    members_id = fields.Int(required=True)

    class Meta:
        fields = ("id", "workout_type", "duration", "members_id")

workout_schema = Workoutschema()
workouts_schema = Workoutschema(many = True)

@workouts.route('/')

def home():
    return " Welcome to the Gym, time to get wrecked and bulk up brah!"



@workouts.route('/workouts', methods = ['GET'])

def get_workout():
    conn=connection()
    if conn is not None:
        try:
            cursor = conn.cursor(dictionary =True)

            query = "SELECT * FROM workouts"

            cursor.execute(query)

            workout = cursor.fetchall()

        except Error as e:
            return jsonify ({"error": e})
        
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close() 
                return workouts_schema.jsonify(workout)




@workouts.route("/workouts/<int:id>", methods = ['PUT']) 
def update_workouts(id):
    try:
        workout_data = workout_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 401
    
    conn = connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            check_query = "SELECT * FROM workouts WHERE id = %s;"
            cursor.execute(check_query, (id,))
            workouts = cursor.fetchone()
            if not workouts:
                return jsonify({"error": "workout program was not found."}), 404
            
            
            updated_workouts = (workout_data['type_workout'], workout_data['duration'], workout_data['members_id'], id) 

            query = "UPDATE workouts SET type_workout = %s, duration = %s, members_id = %s  WHERE id = %s;" 

            cursor.execute(query, updated_workouts)
            conn.commit()

            return jsonify({'message': f"Successfully updated workout type {id}"}), 202
        except Error as e:
            return jsonify(e.messages), 501
        
        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({"error": "Database connection failed"}), 500


@workouts.route('/workouts/<int:members_id>', methods = ['GET'])

def mem_workout(members_id):
    conn=connection()
    if conn is not None:
        try:
            cursor = conn.cursor(dictionary =True)

            query = "SELECT * FROM type_workout WHERE members_id = %s"

            cursor.execute(query, (members_id,))

            workout = cursor.fetchall()

        except Error as e:
            return jsonify ({"error": e})
        
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close() 
                return workouts_schema.jsonify(workout)   


@workouts.route("/workouts", methods = ['POST'])
def add_member():
    try:
        workout_data = workout_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    conn = connection()
    if conn is not None:
        try:
            cursor = conn.cursor()

            
            updated_workout = (workout_data['type_workout'], workout_data['duration'], workout_data['members_id'])

            
            query = "INSERT INTO workouts (type_workout , duration , members_id) VALUES (%s,%s,%s)"
            
           
            cursor.execute(query, updated_workout)
            conn.commit()

            return jsonify({'message': 'New workout added brah, we good'}), 201
        
        except Error as e:
            return jsonify(e.messages), 500
        
        finally:
            cursor.close()
            conn.close() 
        
    else:
        return jsonify ({'error': 'Database connection failed'}), 500
    
if __name__ == '__main__':
    workouts.run(debug=True)