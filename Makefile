bins := phash

all: $(bins)

phash: phash.go
	go build $^
