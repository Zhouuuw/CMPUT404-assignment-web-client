#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

class Error(Exception):
    def __init__(self,ErrorInfo):
        super().__init__(self) 
        self.errorinfo=ErrorInfo
    def __str__(self):
        return self.errorinfo

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        count = 0
        for s in url:
            if s == ":":
                count += 1

        if count == 2:
            url_list = url.split("/")
            if len(url_list) < 3:
                raise Exception 
        
            temp = url_list[2].split(":")
            if len(temp) != 2:
                    raise Exception
            addr = "/"
            if len(url_list) >3 :
                for s in  url_list[3:]:
                    addr += s + "/"
            temp[1] = int(temp[1])
            return (temp[0],temp[1],addr)
        else:
            # use socket to find host and port
            # https://blog.csdn.net/keep_lcm/article/details/81008801
            
            url = url.strip("/")
            print(url)
            print(url[6:])
            lst = socket.getaddrinfo(url[7:],"http")
            print(lst)
            print("--------urg url is ---------")
            print(lst[0])
            print(lst[0][4])
            return (lst[0][4][0],int(lst[0][4][1]),"")
        

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        l = data.split(" ")
        print("attention")
        print(l)
        return int(l[1])

    def get_headers(self,data):
        return None

    def get_body(self, data):
        return None
    
    def strip_response(self, response):
        lst = response.split("\r\n")
        #print("--------response data is ---------")
        #print(lst)
        code = self.get_code(lst[0])
        if lst[-1] == "":
            body = lst[-2]
        else:
            body = lst[-1]
        return code,body

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        code = 500
        body = ""

        host, port, addr = self.get_host_port(url)
        self.connect(host,port)
        get_info = "GET "+addr+ " HTTP/1.1\r\nHost: "+host+"\r\n\r\n"
        #print("--------get info is ---------")
        #print(get_info)
        self.sendall(get_info)
        response = self.recvall(self.socket)
        #print("--------response data is ---------")
        #print(response)
        code,body = self.strip_response(response)
        
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""

        host, port, addr = self.get_host_port(url)
        self.connect(host,port)
        if args == None:
            get_info = "POST "+addr+ " HTTP/1.1\r\nHost: "+host+"\r\n"+"Content-length : 0\r\n\r\n"
        else:
            get_info = "POST "+addr+ " HTTP/1.1\r\nHost: "+host+"\r\n"+"Content-length : "+str(len(args))+"\r\n"+args+"\r\n\r\n"
        #print("--------get info is ---------")
        #print(get_info)
        self.sendall(get_info)
        response = self.recvall(self.socket)
        print("--------response data is ---------")
        print(response)
        code,body = self.strip_response(response)
        
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
