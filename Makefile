flags=.makeFlags
VPATH=$(flags)
$(shell mkdir -p $(flags))

default: build_meson

clean:
	rm -rf $(flags)

genconfig:
	go get -u github.com/hashcloak/genconfig
	@touch $(flags)/$@

build_meson:
	python3 ops/build_containers.py
	@touch $(flags)/$@

testnet: build_meson genconfig
	python3 ops/testnet.py
	@touch $(flags)/$@
	sleep 20

integration_test: testnet
	python3 ops/integration_test.py

stop_testnet:
	docker stack rm mixnet
	rm $(flags)/testnet

push: build_meson
	python3 ops/push_containers.py
	@touch $(flags)/$@

test:
	go test ./pkg/*
