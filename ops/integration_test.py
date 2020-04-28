import os
import subprocess as sp
import tempfile

from setup import warpedBuildFlags, DEFAULT_VALUES

repoPath = os.path.join(tempfile.gettempdir(), "meson-client")
print("PATH: ", repoPath)
try:
    sp.check_output([
        "git",
        "clone",
        "https://github.com/hashcloak/Meson-client",
        repoPath
    ])
except:
    pass

os.chdir(repoPath)
args = ["git", "checkout", DEFAULT_VALUES["HASHCLOAK"]["CLIENT"]["TEST"]["COMMIT"]] 
sp.check_output(args)

service = "gor"
provider = "provider-0"
privateKey = os.getenv("ETHEREUM_PK")

cmd = "go run {0} {1} -c {2} -t {3} -s {3} -k {4} -pk {5}".format(
    warpedBuildFlags,
    os.path.join(repoPath, "integration", "tests.go"),
    os.path.join(tempfile.gettempdir(), "meson-testnet", "client.toml"),
    service,
    os.path.join(tempfile.gettempdir(), "meson-testnet", provider, "currency.toml"),
    privateKey
)
print(sp.check_output(["ls", os.path.join(repoPath, "integration")]).decode("utf-8"))
print("RUNNING: \n"+cmd)
os.system(cmd)
