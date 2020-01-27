package chain

// PostRequest is the common struct containing the body and url
type PostRequest struct {
	Body []byte
	URL  string
}

// IChain is an abstraction for a cryptocurrency
// It only enables creating raw transactions requests
type IChain interface {
	NewRequest(rpcURL string, txHex string) (PostRequest, error)
}
