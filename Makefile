flags=.makeFlags
VPATH=$(flags)
$(shell mkdir -p $(flags))

default: build_meson

clean:
	rm -rf $(flags)

genconfig:
	go get github.com/hashcloak/genconfig
	sed -i '/.genconfig*/d' go.mod # we don't want to add genconfig to go modules
	sed -i '/.genconfig*/d' go.sum # we don't want to add genconfig to go modules

	@touch $(flags)/$@

get_upstream:
	python3 ops/get_upstream.py
	@touch $(flags)/$@

build_meson: get_upstream
	python3 ops/build_meson.py
	@touch $(flags)/$@

testnet: build_meson genconfig
	python3 ops/testnet.py
	@touch $(flags)/$@
	sleep 40

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
