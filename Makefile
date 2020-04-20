flags=.makeFlags
VPATH=$(flags)
$(shell mkdir -p $(flags))

messagePush=echo "LOG: Image already exists in docker.io/$(dockerRepo). Not pushing: "
messagePull=echo "LOG: Success in pulling image: "
imageNotFound=echo "LOG: Image not found... building: "

default: build_meson

genconfig:
	go get github.com/hashcloak/genconfig
	sed -i '/.genconfig*/d' go.mod # we don't want to add genconfig to go modules
	sed -i '/.genconfig*/d' go.sum # we don't want to add genconfig to go modules

	@touch $(flags)/$@

get_upstream:
	bash ops/get_upstream.sh
	@touch $(flags)/$@

build_meson: get_upstream
	bash ops/build_meson.sh
	@touch $(flags)/$@

testnet: build_meson genconfig
	bash ops/testnet.sh
	@touch $(flags)/$@
	sleep 40

integration_test: testnet
	bash ops/integration_test.sh

stop_testnet:
	docker stack rm mixnet
	rm $(flags)/testnet

push_containers: build_meson
	bash ops/push_containers.sh
	@touch $(flags)/$@

test:
	go test ./pkg/*

clean:
	rm -rf $(flags)
