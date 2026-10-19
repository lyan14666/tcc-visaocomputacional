import time

from init import ALERT_COOLDOWN


class AlertSystem:

    def __init__(self):

        self.last_alert = 0.0

    def update(self, detected, confirmed):

        if not detected or not confirmed:
            return False

        now = time.time()

        if now - self.last_alert < ALERT_COOLDOWN:
            return False

        self.last_alert = now

        print("[ALERTA] FACA CONFIRMADA")

        return True

    def reset(self):

        self.last_alert = 0.0