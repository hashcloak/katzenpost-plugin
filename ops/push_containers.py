from subprocess import run
from config import CONFIG

for key in ["AUTH", "SERVER", "MESON"]:
    run(["docker", "push", "{}:{}".format(
        CONFIG[key]["CONTAINER"],
        CONFIG[key]["TAGS"]["NAMED"]
    )])
    run(["docker", "push", "{}:{}".format(
        CONFIG[key]["CONTAINER"],
        CONFIG[key]["TAGS"]["HASH"]
    )])
