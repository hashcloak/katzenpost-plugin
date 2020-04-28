from tempfile import NamedTemporaryFile
from os import path, curdir
from subprocess import run

from setup import CONFIG

currentPath = path.abspath(curdir)
dockerFile = path.join(currentPath, "Dockerfile")
tmpDockerFile = NamedTemporaryFile().name

with open(dockerFile, 'r') as df, open(tmpDockerFile, 'w+') as tmpdf:
    for line in df:
        if CONFIG["SERVER"]["CONTAINER"] in line:
            line = "FROM {}:{}\n".format(
                    CONFIG["SERVER"]["CONTAINER"],
                    CONFIG["SERVER"]["TAGS"]["NAMED"],
                )

        tmpdf.write(line)

container = CONFIG["MESON"]["CONTAINER"]
tag = CONFIG["MESON"]["GITHASH"]

print("\nLOG: Building {}:{}\n".format(container, tag))
run([
    "docker",
    "build",
    "-t",
    "{}:{}".format(container, tag),
    "-f",
    tmpDockerFile,
    currentPath
], check=True)

print("\nLOG: Retagging {} from: {} to: {} tag\n".format(
        container,
        tag,
        CONFIG["MESON"]["BRANCH"],
    )
)

run([
    "docker",
    "tag",
    "{}:{}".format(container, tag),
    "{}:{}".format(container, CONFIG["MESON"]["BRANCH"]),
])
