from flask import Flask, jsonify, request
from config import app, db
from models import Contact
from flask_restx import Api, Resource, fields

# Initialize the API with Flask-RestX
api = Api(app, version='1.0', title='Contacts API', description='A simple Contacts API using Flask-RestX', doc='/swagger/')

ns = api.namespace('contacts', description='Contacts operations')

# Swagger model for Contact
contact_model = api.model('Contact', {
    'firstName': fields.String(required=True, description='The first name of the contact'),
    'lastName': fields.String(required=True, description='The last name of the contact'),
    'email': fields.String(required=True, description='The email of the contact')
})

contact_update_model = api.model('ContactUpdate', {
    'firstName': fields.String(description='The first name of the contact'),
    'lastName': fields.String(description='The last name of the contact'),
    'email': fields.String(description='The email of the contact')
})


@ns.route("/")
class ContactList(Resource):
    @ns.doc('list_contacts')
    @ns.marshal_with(contact_model, envelope='contacts', as_list=True)
    def get(self):
        """List all contacts"""
        contacts = Contact.query.all()
        return list(map(lambda x: x.to_json(), contacts))

    @ns.doc('create_contact')
    @ns.expect(contact_model)
    @ns.response(201, 'Contact created successfully')
    @ns.response(400, 'Missing required fields or invalid data')
    def post(self):
        """Create a new contact"""
        first_name = request.json.get("firstName")
        last_name = request.json.get("lastName")
        email = request.json.get("email")
        
        if not first_name or not last_name or not email:
            api.abort(400, 'Missing required fields')
        
        new_contact = Contact(first_name=first_name, last_name=last_name, email=email)
        try:
            db.session.add(new_contact)
            db.session.commit()
            return {"message": "Contact created successfully"}, 201
        except Exception as e:
            api.abort(400, str(e))


@ns.route("/<int:user_id>")
@ns.response(404, 'Contact not found')
class ContactResource(Resource):
    @ns.doc('update_contact')
    @ns.expect(contact_update_model)
    @ns.response(200, 'Contact updated successfully')
    def patch(self, user_id):
        """Update an existing contact"""
        contact = Contact.query.get(user_id)
        
        if not contact:
            api.abort(404, 'Contact not found')
        
        data = request.json
        contact.first_name = data.get("firstName", contact.first_name)
        contact.last_name = data.get("lastName", contact.last_name)
        contact.email = data.get("email", contact.email)
        
        db.session.commit()
        
        return {"message": "Contact updated successfully"}, 200
    
    @ns.doc('delete_contact')
    @ns.response(200, 'Contact deleted successfully')
    def delete(self, user_id):
        """Delete a contact"""
        contact = Contact.query.get(user_id)
        
        if not contact:
            api.abort(404, 'Contact not found')
        
        db.session.delete(contact)
        db.session.commit()
        
        return {"message": "Contact deleted successfully"}, 200


# Add the namespace to the API
api.add_namespace(ns, path='/contacts')


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
