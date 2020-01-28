package chain

import (
	"fmt"
)

// CosmosChain is a struct for identifier blockchains and their forks
type CosmosChain struct {
	ticker  string
	chainID int
}

// NewRequest : Takes signed transaction data as a parameter
// Returns a URL endpoint
func (ec *CosmosChain) NewRequest(rpcURL string, txHex string) (PostRequest, error) {
	URL := fmt.Sprintf("%s/broadcast_tx_async?tx=%s", rpcURL, txHex)
	return PostRequest{URL: URL}, nil
}
