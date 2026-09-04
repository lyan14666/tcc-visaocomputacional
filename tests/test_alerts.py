import time

from init import ALERT_COOLDOWN


class AlertManager:

    def __init__(self):

        self.last_alert = 0.0

        self.cooldown = ALERT_COOLDOWN

        self.active = False

    def update(self, confirmed):

        current_time = time.time()

        if not confirmed:

            self.active = False

            return False

        if (
            current_time -
            self.last_alert
            < self.cooldown
        ):

            return False

        self.last_alert = current_time

        self.active = True

        print(
            "\n"
            "==============================\n"
            "       ALERTA: FACA DETECTADA\n"
            "==============================\n"
        )

        return True