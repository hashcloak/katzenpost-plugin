import os
from tempfile import gettempdir

from setup import warpedBuildFlags, CONFIG, checkoutRepo

repoPath = os.path.join(gettempdir(), "meson-client")
checkoutRepo(
    repoPath,
    "https://github.com/hashcloak/Meson-client",
    CONFIG["CLIENT"]["TESTCOMMIT"]
)

service = "gor"
provider = "provider-0"
privateKey = os.getenv("ETHEREUM_PK")

cmd = "go run {0} {1} -c {2} -t {3} -s {3} -k {4} -pk {5}".format(
    warpedBuildFlags,
    os.path.join(repoPath, "integration", "tests.go"),
    os.path.join(gettempdir(), "meson-testnet", "client.toml"),
    service,
    os.path.join(gettempdir(), "meson-testnet", provider, "currency.toml"),
    privateKey
)
print("RUNNING: \n"+cmd)
os.system(cmd)
