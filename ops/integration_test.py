from os import path
from sys import exit
from tempfile import gettempdir
from subprocess import run, STDOUT, PIPE
from time import sleep

from config import CONFIG
from utils import checkoutRepo, log

repoPath = path.join(gettempdir(), "meson-client")
confDir = path.join(gettempdir(), "meson-testnet")
checkoutRepo(
    repoPath,
    "https://github.com/hashcloak/Meson-client",
    CONFIG["TEST"]["CLIENTCOMMIT"]
)

warpedBuildFlags='-ldflags "-X github.com/katzenpost/core/epochtime.WarpedEpoch=true -X github.com/katzenpost/server/internal/pki.WarpedEpoch=true"'
cmd = "go run {warped} {testGo} -c {client} -k {currency} -pk {pk}".format(
    warped=warpedBuildFlags if CONFIG["WARPED"] else "",
    testGo=path.join(repoPath, "integration", "tests.go"),
    client=path.join(confDir, "client.toml"),
    currency=path.join(confDir, "provider-0", "currency.toml"),
    pk=CONFIG["TEST"]["PKS"]["ETHEREUM"]
)

# The attempts are needed until the stability of the mixnet gets improved.
# This issue is a step in that direction: https://github.com/hashcloak/Meson-plugin/issues/29
attempts = CONFIG["TEST"]["ATTEMPTS"]
while True:
    log("Attempt {}: {}".format(attempts, cmd))
    output = run([cmd], stdout=PIPE, stderr=STDOUT, shell=True)
    # Travis has issues printing a huge string.
    # Creating seperate print statements helps with this
    for line in output.stdout.decode().split("\n"):
        log(line, output.returncode == 1)

    if output.returncode == 0:
        exit(0)

    attempts -= 1
    if attempts == 0:
        exit(1)
    sleep(10)
