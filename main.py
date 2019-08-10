# TO PAUSE: CTRL-Z
# TO RESUME: fg

from datetime import datetime
import json
import os
import sys
import time

NUM_CYCLES = 3
NUM_REPS = 8
WORKOUT_TIME = 50
WAIT_TIME = 30
REST_TIME = 120
EXERCISE_FILE = "./exercises.json"
BEEP_SOUND = ""


def do_announce(msg):
    if not msg:
        return

    do_exec("echo {}".format(msg))
    do_exec("say {}".format(msg), False)


def do_exec(cmd, save=True):
    if save:
        os.system("{} | tee -a {}".format(cmd, TEE_FILE))
    else:
        os.system(cmd)


class Workout:
    def __init__(self):
        self.last_primary_drill = None
        self.last_secondary_drill = None
        self.set_num = 0
        self.all_primary_drills = DRILLS[WORKOUT_TYPE]
        self.all_secondary_drills = DRILLS["Legs"]
        self.remaining_primary_drills = DRILLS[WORKOUT_TYPE][:]
        self.remaining_secondary_drills = DRILLS["Legs"][:]

    def do_set(self, set_num):
        do_announce("Set {}".format(set_num))
        self.do_exercise("Go!", WORKOUT_TIME)
        self.do_exercise("Rest!", WAIT_TIME, dont_pick=True)

    def do_workout(self):
        for cycle in range(NUM_CYCLES):
            print ""
            do_announce("Cycle {}".format(cycle + 1))
            for set_num in range(NUM_REPS):
                self.set_num = set_num + 1
                self.do_set(self.set_num)
            self.do_exercise("Big Rest!", REST_TIME, dont_pick=True)

    def start(self):
        self.do_workout()
        do_announce("You're done! Good job!")

    def remove_drill(self, drill):
        if self.is_primary_exercise():
            del self.remaining_primary_drills[drill]
        else:
            del self.remaining_secondary_drills[drill]

    def have_drills(self):
        if self.is_primary_exercise():
            print self.remaining_primary_drills
            return len(self.remaining_primary_drills) != 0
        else:
            print self.remaining_secondary_drills
            return len(self.remaining_secondary_drills) != 0

    def reset_drills(self):
        if self.is_primary_exercise():
            self.remaining_primary_drills = self.all_primary_drills[:]
        else:
            self.remaining_secondary_drills = self.all_secondary_drills[:]

    def choose_drill(self):
        drills = self.remaining_secondary_drills
        last_drill = self.last_secondary_drill
        drill = None

        if self.is_primary_exercise():
            drills = self.remaining_primary_drills
            last_drill = self.last_primary_drill

        if self.have_drills() or last_drill.endswith("Left"):
            if (last_drill and last_drill.endswith("Left")):
                drill = last_drill.replace("Left", "Right")
            else:
                drill = drills.pop()

            last_drill = drill
        else:
            self.reset_drills()
            return self.choose_drill()

        if self.is_primary_exercise():
            self.remaining_primary_drills = drills
            self.last_primary_drill = drill
        else:
            self.remaining_secondary_drills = drills
            self.last_secondary_drill = drill

        return drill

    def choose_exercise(self, dont_pick):
        if dont_pick or not self.set_num:
            return

        return self.choose_drill()

    def do_exercise(self, title, duration, dont_pick=False):
        do_announce(title)
        do_announce(self.choose_exercise(dont_pick))
        self.print_timer(duration)
        print ""
        print ""
        self.do_beep()

    @staticmethod
    def do_beep():
        do_exec("afplay /System/Library/Sounds/Glass.aiff", False)

    @staticmethod
    def print_timer(duration):
        for remaining in range(duration, 0, -1):
            sys.stdout.write("\r")
            sys.stdout.write("{:2d} seconds remaining.".format(remaining))
            sys.stdout.flush()
            time.sleep(1)

    def is_primary_exercise(self):
        if not self.set_num:
            return False

        if self.set_num % 2 == 0:
            return False

        return True


if __name__ == "__main__":
    with open(EXERCISE_FILE) as json_file:
        DRILLS = json.load(json_file)
    WORKOUT_TYPE = raw_input("Arms, Back, Chest, or Core? ") or "Arms"
    if WORKOUT_TYPE not in ("Arms", "Back", "Chest", "Core"):
        do_announce("Invalid workout type")
        sys.exit()

    TEE_FILE = "logs/{}_{}.log".format(
        datetime.today().strftime('%Y-%m-%d'), WORKOUT_TYPE)
    workout = Workout()
    workout.start()
