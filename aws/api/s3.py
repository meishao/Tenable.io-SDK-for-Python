import boto3
import os
from flask import Flask, jsonify

class S3Api(object):
    
    def __init__(self):
        pass
    
    def response(self, _filename, _resp):
        
        S3_BUCKET = os.environ.get('S3_BUCKET')
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(S3_BUCKET)
        
        PUT_OBJECT_KEY_NAME = self._filename
        obj = bucket.Object(PUT_OBJECT_KEY_NAME)
        
        _response = obj.put(
            Body=self._resp,
            ContentEncoding='utf-8',
            ContentType='text/csv'
        )
        
        return jsonify(_response)
        
