import boto3
import os
from flask import Flask, jsonify

class S3Api(object):
    
    def __init__(self, s3=None, bucket=None):
        
        S3_BUCKET = os.environ.get('S3_BUCKET')
        
        self.s3 = boto3.resource('s3')
        self.bucket = s3.Bucket(S3_BUCKET)
    
    def response(self, _filename, _resp):
        
        PUT_OBJECT_KEY_NAME = _filename
        obj = self.bucket.Object(PUT_OBJECT_KEY_NAME)
        
        _response = obj.put(
            Body=_resp,
            ContentEncoding='utf-8',
            ContentType='text/csv'
        )
        
        return jsonify(_response)
        
