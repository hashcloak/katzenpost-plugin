package chain

import (
	"strings"
)


// GetChain takes a ticker symbol for a supported chain and returns an interface
// for that chain
func GetChain(ticker string) IChain {
	switch strings.ToUpper(ticker) {
	case "ETH":
		return &ETHChain{ticker: "ETH", chainID: 1}
	case "ETC":
		return &ETHChain{ticker: "ETC", chainID: 61}
	case "GOR":
		return &ETHChain{ticker: "GOR", chainID: 5}
	case "RIN":
		return &ETHChain{ticker: "RIN", chainID: 4}
	case "KOT":
		return &ETHChain{ticker: "KOT", chainID: 6}
	}

}

