#!/usr/bin/env bash
source ops/common.sh

cat - > /tmp/meson.Dockerfile<<EOF
FROM golang:alpine AS builder

# Install git & make
RUN apk update && \
    apk add --no-cache git make ca-certificates && \
    update-ca-certificates

WORKDIR /go/Meson
COPY . .
RUN go build -o Meson cmd/main.go 

FROM hashcloak/server:$katzenBaseServerTag
COPY --from=builder /go/Meson/Meson /go/bin/Meson
ENTRYPOINT /go/bin/server -f /conf/katzenpost.toml
EOF

docker build -f /tmp/meson.Dockerfile -t hashcloak/meson:$mesonCurrentBranchHash .
docker tag hashcloak/meson:$mesonCurrentBranchHash hashcloak/meson:$mesonCurrentBranchTag