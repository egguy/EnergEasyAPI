def generate_command(name, parameters=None):
    return {
        "name": name,
        "parameters": [parameters] if parameters else []
    }


class Shutter(object):
    def __init__(self, url, name, state="closed", position=100):
        self.state = state
        self.name = name
        self.url = url
        self.position = position

    def close(self):
        return generate_command("close")

    def open(self):
        return generate_command("open")

    def set_position(self, position):
        return generate_command("setClosure", position)

    def dimmed(self):
        return self.set_position(90)
