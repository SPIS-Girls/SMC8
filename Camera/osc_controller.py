from pythonosc import udp_client

class OSCController:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.client = udp_client.SimpleUDPClient(self.ip, self.port)

        self.DISTANCE_ENDPOINT = "/distance"
        self.WRIST_L_ENDPOINT = "/wrists_L"
        self.WRIST_R_ENDPOINT = "/wrists_R"
        self.TORSO_ENDPOINT = "/weight"

    def send_distance(self, distance):
        self.client.send_message(self.DISTANCE_ENDPOINT, distance)

    def send_weigth_effort(self, torsos_effort):
        for idx, effort in enumerate(torsos_effort):
            endpoint = self.TORSO_ENDPOINT + str(idx)
            self.client.send_message(endpoint, float(effort))

    def send_body_parts(self, wrists_left, wrists_right, torsos):
        for idx, wrist in enumerate(wrists_left):
            endpoint = self.WRIST_L_ENDPOINT + str(idx)
            self.client.send_message(endpoint, wrist)

        for idx, wrist in enumerate(wrists_right):
            endpoint = self.WRIST_R_ENDPOINT + str(idx)
            self.client.send_message(endpoint, wrist)

