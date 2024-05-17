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
        self.ROTATION_ENDPOINT = "/rotation"
        self.ROTATION_AMPLITUDE_ENDPOINT = "/rotation_amplitude"
        self.STOP_ENDPOINT = "/stop"
        self.TILT_ENDPOINT = "/tilt"
        self.CRUNCH_ENDPOINT = "/crunch"

    def send_distance(self, distance):
        self.client.send_message(self.DISTANCE_ENDPOINT, distance)

    def send_stop_position(self, is_stop_position):
        self.client.send_message(self.STOP_ENDPOINT, bool(is_stop_position))

    def send_weigth_effort(self, torsos_effort):
        for idx, effort in enumerate(torsos_effort):
            endpoint = self.TORSO_ENDPOINT + str(idx)
            self.client.send_message(endpoint, float(effort))

    def send_rotation(self, rotation):
        self.client.send_message(self.ROTATION_ENDPOINT, rotation)

    def send_rotation_amplitude(self, rotation_amplitude):
        self.client.send_message(self.ROTATION_AMPLITUDE_ENDPOINT, rotation_amplitude)

    def send_crunch(self, crunch):
        self.client.send_message(self.CRUNCH_ENDPOINT, crunch)

    def send_tilt(self, tilt):
        self.client.send_message(self.TILT_ENDPOINT, tilt)

    def send_body_parts(self, wrists_left, wrists_right):
        for idx, wrist in enumerate(wrists_left):
            endpoint = self.WRIST_L_ENDPOINT + str(idx)
            self.client.send_message(endpoint, wrist)

        for idx, wrist in enumerate(wrists_right):
            endpoint = self.WRIST_R_ENDPOINT + str(idx)
            self.client.send_message(endpoint, wrist)

