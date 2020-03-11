flags=.makeFlags
VPATH=$(flags)
$(shell mkdir -p $(flags))

messagePush=echo "LOG: Image already exists in docker.io/$(dockerRepo). Not pushing: "
messagePull=echo "LOG: Success in pulling image: "
imageNotFound=echo "LOG: Image not found... building: "

clean:
	rm -rf $(flags)

genconfig:
	go get github.com/hashcloak/genconfig
	@touch $(flags)/$@

get_upstream:
	bash ops/get_upstream.sh
	@touch $(flags)/$@

build_meson:  get_upstream
	bash ops/build_containers.sh
	@touch $(flags)/$@

testnet: build_meson genconfig
	bash ops/testnet.sh

stop_testnet:
	docker stack rm mixnet

push_containers: build_meson
	bash ops/push_containers.sh
	@touch $(flags)/$@

test:
	go test ./pkg/*
