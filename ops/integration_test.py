import os
from tempfile import gettempdir
from subprocess import run

from config import warpedBuildFlags, CONFIG, checkoutRepo

repoPath = os.path.join(gettempdir(), "meson-client")
checkoutRepo(
    repoPath,
    "https://github.com/hashcloak/Meson-client",
    CONFIG["TEST"]["CLIENTCOMMIT"]
)

cmd = "go run {} {} -c {} -k {} -pk {}".format(
    warpedBuildFlags if CONFIG["WARPED"] else "",
    os.path.join(repoPath, "integration", "tests.go"),
    os.path.join(gettempdir(), "meson-testnet", "client.toml"),
    os.path.join(gettempdir(), "meson-testnet", "provider-0", "currency.toml"),
    CONFIG["TEST"]["PKS"]["ETHEREUM"]
)
run([cmd], check=True, shell=True, cwd=repoPath)
