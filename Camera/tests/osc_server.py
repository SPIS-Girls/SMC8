"""Small example OSC server for testing packages."""

from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server

if __name__ == "__main__":
  dispatcher = Dispatcher()
  dispatcher.map("/distance", print)

  server = osc_server.ThreadingOSCUDPServer(
      ("127.0.0.1", 9998), dispatcher)
  print("Serving on {}".format(server.server_address))
  server.serve_forever()