#!/usr/bin/env bash
source ops/common.sh

baseTag=$katzenServerBranch
if [[ -n $warpedBuildFlags ]]; then
  baseTag=warped
fi

dockerFile=/tmp/meson.Dockerfile
cat - > $dockerFile<<EOF
FROM golang:alpine AS builder

# Install git & make
RUN apk update && \
    apk add --no-cache git make ca-certificates && \
    update-ca-certificates

WORKDIR /go/Meson
COPY . .
RUN go build -o Meson cmd/main.go 

FROM $katzenServerContainer:$baseTag
COPY --from=builder /go/Meson/Meson /go/bin/Meson
ENTRYPOINT /go/bin/server -f /conf/katzenpost.toml
EOF

LOG "Using $katzenServerContainer:$baseTag as FROM container"
docker build --no-cache -f $dockerFile -t $mesonContainer:$mesonBranchHash .
LOG "Built $mesonContainer:$mesonBranchHash"
LOG "Tagging $mesonContainer: SOURCE: $mesonBranchHash TARGET: $mesonBranchTag "
docker tag $mesonContainer:$mesonBranchHash $mesonContainer:$mesonBranchTag
