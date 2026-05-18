"""Task state machine for gripper control flow."""


STATES = ["WAIT", "FOUND", "STABLE", "GRAB", "HOLD", "RELEASE", "COOLDOWN"]


class StateMachine:
    """Manages gripper task states and transitions.

    WAIT → FOUND → STABLE → GRAB → HOLD → RELEASE → COOLDOWN → WAIT
    """

    def __init__(self, stable_frame_count=3, hold_sec=2.0, cooldown_sec=5.0):
        self.state = "WAIT"
        self.auto = True
        self.stable_frames = stable_frame_count
        self.hold_sec = hold_sec
        self.cooldown_sec = cooldown_sec
        self.consecutive = 0
        self.timer = 0.0

    def update(self, target_found, now):
        """Run one state transition cycle.

        Returns (action, old_state, new_state).
        action is "GRAB", "OPEN", or None.
        """
        old = self.state
        action = None

        if self.state == "WAIT":
            if target_found:
                self.state = "FOUND"
                self.consecutive = 1
            else:
                self.consecutive = 0

        elif self.state == "FOUND":
            if target_found:
                self.consecutive += 1
                if self.consecutive >= self.stable_frames:
                    self.state = "STABLE"
            else:
                self.state = "WAIT"
                self.consecutive = 0

        elif self.state == "STABLE":
            self.state = "GRAB"
            self.timer = now
            if self.auto:
                action = "GRAB"

        elif self.state == "GRAB":
            self.state = "HOLD"
            self.timer = now

        elif self.state == "HOLD":
            if now - self.timer >= self.hold_sec:
                action = "OPEN"
                self.state = "RELEASE"
                self.timer = now

        elif self.state == "RELEASE":
            self.state = "COOLDOWN"
            self.timer = now

        elif self.state == "COOLDOWN":
            if now - self.timer >= self.cooldown_sec:
                self.state = "WAIT"

        return action, old, self.state

    def reset(self):
        self.state = "WAIT"
        self.consecutive = 0
        self.timer = 0.0
