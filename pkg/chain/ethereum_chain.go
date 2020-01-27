package chain

import (
	"encoding/json"
)

// An ethereum request abstraction.
// Only need it for one method, though.
type ethRequest struct {
	// ChainId to indicate which Ethereum-based network
	ID uint `json:"id"`
	// Indicates which version of JSON RPC to use
	// Since all networks support JSON RPC 2.0,
	// this attribute is a constant
	JSONRPC string `json:"jsonrpc"`
	// Which method you want to call
	METHOD string `json:"method"`
	// Params for the method you want to call
	Params []string `json:"params"`
}

// ETHChain is a struct for identifier blockchains and their forks
type ETHChain struct {
	chainID uint
	ticker  string
}

// NewRequest : Takes signed transaction data as a parameter
// Returns a marshalled request
func (ec *ETHChain) NewRequest(txHex string) ([]byte, error){
	er := ethRequest {
		ID: ec.chainID,
		JSONRPC: "2.0",
		METHOD: "eth_sendRawTransaction",
		Params: []string{txHex},
	}

	marshalledRequest, err := json.Marshal(er)
	return marshalledRequest, err
}