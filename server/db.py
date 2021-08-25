from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://tjzsrztpwixxqb:1e9e01a0040afb6ba0de508bf69a5ea124fcea4c55f6faeaec8c72538f3cb8ba@ec2-52-214-178-113.eu-west-1.compute.amazonaws.com:5432/d2bmta7b4nhied'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_POOL_SIZE"] = 20
db = SQLAlchemy(app)
