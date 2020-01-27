package chain

// Chain is an abstraction for a cryptocurrency
// It only enables creating raw transactions requests
type IChain interface {
	NewRequest(txHex string) ([]bytes, error)
}