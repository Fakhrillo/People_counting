# import cv2
# import socket
# import threading
# from time import sleep
# from http.server import BaseHTTPRequestHandler, HTTPServer
# from socketserver import ThreadingMixIn

# HTTP_SERVER_PORT = 8888
    
# def get_ip():
#         s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#         s.settimeout(0)
#         try:
#             # doesn't even have to be reachable
#             s.connect(('10.254.254.254', 1))
#             IP = s.getsockname()[0]
#         except Exception:
#             IP = '127.0.0.1'
#         finally:
#             s.close()
#             print(f"Serving at: {IP}:{HTTP_SERVER_PORT}")
#         return IP


# # HTTPServer MJPEG
# class VideoStreamHandler(BaseHTTPRequestHandler):
#     def do_GET(self):
#         self.send_response(200)
#         self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
#         self.end_headers()
#         while True:
#             sleep(0.1)
#             if hasattr(self.server, 'frametosend'):
#                 ok, encoded = cv2.imencode('.jpg', self.server.frametosend)
#                 self.wfile.write("--jpgboundary".encode())
#                 self.send_header('Content-type', 'image/jpeg')
#                 self.send_header('Content-length', str(len(encoded)))
#                 self.end_headers()
#                 self.wfile.write(encoded)
#                 self.end_headers()
   
             
# class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
#     """Handle requests in a separate thread."""
#     pass


# #start MJPEG HTTP Server
# server_HTTP = ThreadedHTTPServer((get_ip(), HTTP_SERVER_PORT), VideoStreamHandler)
# print("Starting MJPEG HTTP Server...")
# th2 = threading.Thread(target=server_HTTP.serve_forever)
# th2.daemon = True
# th2.start()

