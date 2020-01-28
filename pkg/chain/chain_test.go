package chain

import (
	"bytes"
	"encoding/json"
	"testing"
)

const (
	broadcastTxAsync = "/broadcast_tx_async?tx="
)

func TestChainFactoryError(t *testing.T) {
	_, err := GetChain("SOMETHING")
	if err == nil {
		t.Fatalf("Should return an error")
	}
}

func TestChainFactoryErrorEmpty(t *testing.T) {
	_, err := GetChain("")
	if err == nil {
		t.Fatalf("Should return an error")
	}
}

func TestEthereumChainTxnInBody(t *testing.T) {
	chainInterface, _ := GetChain("ETH")
	txn := `"TXN"`
	postRequest, _ := chainInterface.NewRequest("", txn)
	var expectedValue ethRequest
	json.Unmarshal(postRequest.Body, &expectedValue)
	if len(expectedValue.Params) != 1 {
		t.Fatalf("Length expected to be %d, got %d", 1, len(expectedValue.Params))
	}
	if expectedValue.Params[0] != txn {
		t.Fatalf("Expected %s, got %s", txn, expectedValue.Params[0])
	}
}

func TestCosmosChainURLEmpty(t *testing.T) {
	chainInterface, _ := GetChain("TBNB")
	_, err := chainInterface.NewRequest("", "")
	if err == nil {
		t.Fatalf("Should return an error when passed empty URL")
	}
}
func TestCosmosChainBody(t *testing.T) {
	chainInterface, _ := GetChain("TBNB")
	postRequest, _ := chainInterface.NewRequest("URL", "")
	if bytes.Compare(postRequest.Body, []byte{}) != 0 {
		t.Fatalf("Body should be empty for cosmos request")
	}
}
func TestCosmosChainURLAppend(t *testing.T) {
	chainInterface, _ := GetChain("TBNB")
	inputTxn := "EXPECTED_TXN"
	inputURL := "URL"
	expectedResult := inputURL + broadcastTxAsync + inputTxn
	postRequest, _ := chainInterface.NewRequest(inputURL, inputTxn)
	if postRequest.URL != expectedResult {
		t.Fatalf("URL should have value %s, got %s", broadcastTxAsync, postRequest.URL)
	}
}
func TestCosmosChainURL(t *testing.T) {
	chainInterface, _ := GetChain("TBNB")
	expectedURL := "EXPECTED_URL"
	postRequest, _ := chainInterface.NewRequest(expectedURL, "")
	if postRequest.URL != expectedURL+broadcastTxAsync {
		t.Fatalf("URL should have value %s, got %s", broadcastTxAsync, postRequest.URL)
	}
}
