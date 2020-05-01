# How to use the ops directory:

These ops scripts rely heavily on environment variables to determine which build is the correct build. There are a lot of extra command options to allow for felxibility of which repositories to use and which commits to use. The three environment variables that will probably be used the most are `TEST_CLIENTCOMMIT`, `TEST_PKS_ETHEREUM`, and `TEST_PKS_BINANCE` since the rest either have defaults or are derived from the other variables.

### Environment variables

- `AUTH_CONTAINER`: Name of the authority container, __default__: `hashcloak/authority`.
- `AUTH_REPOSITORY`: Git repository for the authority, __default__: `https://github.com/katzenpost/authority`.
- `AUTH_BRANCH`: Git branch to use from the `AUTH_REPOSITORY` value, __default__: `master`.
- `AUTH_GITHASH`: Git commit hash to use to build the container, __default__: commit at `master`.
- `AUTH_TAGS_NAMED`: Docker tag for the `AUTH_CONTAINER` that __default__s: `AUTH_GITHASH`.
- `AUTH_TAGS_HASH`: Docker tag for the `AUTH_CONTAINER` that __default__s: `AUTH_GITHASH`.
- `SERVER_CONTAINER`: Name of the server container, __default__: `hashcloak/server`.
- `SERVER_REPOSITORY`: Git repository for the server, __default__: `https://github.com/katzenpost/server`.
- `SERVER_BRANCH`: Git branch to use from the `SERVER_REPOSITORY` value, __default__: `master`.
- `SERVER_GITHASH`: Git commit hash to use to build the container, __default__: commit at `master`.
- `SERVER_TAGS_NAMED`: Docker tag for the `SERVER_CONTAINER` that __default__: `SERVER_BRANCH`.
- `SERVER_TAGS_HASH`: Docker tag for the `SERVER_CONTAINER` that __default__: `SERVER_GITHASH`.
- `MESON_CONTAINER`: Name of the meson container, __default__: `hashcloak/meson`.
- `MESON_BRANCH`: Current git branch.
- `MESON_GITHASH`: Current git commit has at the current branch.
- `MESON_TAGS_NAMED`: Docker tag that __default__: `MESON_BRANCH`.
- `MESON_TAGS_HASH`: Docker tag that that __default__: `MESON_GITHASH`.
- `TEST_CLIENTCOMMIT`: Commit hash to use for the integration test.
- `TEST_PKS_ETHEREUM`: Private key to use for testing ethereum.
- `TEST_PKS_BINANCE`: Private key to use for testing binance.
- `TEST_NODES`: Quantity of testnet mixnodes to spawn, __default__: 2.
- `TEST_PROVIDERS`: Quantity of testnet providers to spawn, __default__: 2.
- `WARPED`: Sets the warped epoch variable in katzenpost code to allow for two minute epochs. All prefixes all container names with `warped_`. Default is true on all branches except for `master`.


### Example usage:

```
TEST_CLIENTCOMMIT=42b8682f make integration_test
```

The above will use the `42b8682f` commit for running the integrations tests that live in [Meson-client](https://github.com/hashcloak/Meson-client).


Another tweak is if you want to test the katzenpost/server code that is on another repo. You can do the following:

```
SERVER_REPOSITORY=https://github.com/hashcloak/server make integration_test
```
