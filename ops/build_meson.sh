#!/usr/bin/env bash
source ops/common.sh
set -e

cat - > /tmp/meson.Dockerfile<<EOF
FROM golang:alpine AS builder
RUN apk update && \
    apk add --no-cache git make ca-certificates && \
    update-ca-certificates
WORKDIR /go/Meson
COPY . .
RUN go build -o Meson cmd/main.go 

FROM $katzenServerContainer:$katzenServerTag
COPY --from=builder /go/Meson/Meson /go/bin/Meson
ENTRYPOINT /go/bin/server -f /conf/katzenpost.toml
EOF

LOG "Using $katzenServerContainer:$katzenServerTag as FROM container. Building $mesonContainer:$mesonBranchHash"
docker build --no-cache -f /tmp/meson.Dockerfile -t $mesonContainer:$mesonBranchHash .
LOG "Tagging $mesonContainer: SOURCE: $mesonBranchHash TARGET: $mesonBranch"
docker tag $mesonContainer:$mesonBranchHash $mesonContainer:$mesonBranch
