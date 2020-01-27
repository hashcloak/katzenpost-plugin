# Meson-plugin
A Library for adding cryptocurrencies to Meson.

## Currently Supported Chains
- Major ETH-based forks and their testnets
  - Ethereum (ETH)
  - Ethereum Classic (ETC)
  - Goerli Testnet (GOR)
  - Rinkeby Testnet (RIN)
  - Kotti Testnet (KOT)

## Add a New Chain
To add support for a new chain, the following needs to be done:
1. In the chain package, create a new file named `($NEW_SUPPORTED_CHAIN)_chain.go`
2. In this new file, create a new struct in which the attributes are properties that are needed to create an appropriate JSON object. 
3. This struct must conform to the `IChain` interface defined in chain.go
4. Once this is done, you need to add your chain to `factory.go` in the `GetChain` function

## Usage
TODO
