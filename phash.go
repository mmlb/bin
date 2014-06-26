package main

import (
	"bufio"
	"bytes"
	"crypto/sha1"
	"flag"
	"fmt"
	"io"
	"os"
	"runtime"
	"strings"
	"sync"
)

import _ "net/http/pprof"

type result struct {
	hash []byte
	name string
}

func hasher(wg *sync.WaitGroup, files chan string, results chan result) {
	h := sha1.New()
	for name := range files {
		f, e := os.Open(name)
		if e != nil {
			continue
		}
		h.Reset()
		if _, err := io.Copy(h, f); err == nil {
			results <- result{h.Sum(nil), name}
		}
		f.Close()
	}
	wg.Done()
}

func main() {
	numprocs := runtime.NumCPU()*2 + 1

	files := make(chan string, numprocs)
	results := make(chan result, numprocs)
	done := make(chan struct{})

	wg := &sync.WaitGroup{}
	for i := 0; i < numprocs; i++ {
		wg.Add(1)
		go hasher(wg, files, results)
	}

	c := flag.Bool("c", false, "Check hashes as presented from stdin")
	check := flag.Bool("check", false, "Check hashes as presented from stdin")
	flag.Parse()
	if *c || *check {
		lock := sync.Mutex{}
		outstanding := make(map[string][]byte)
		scanner := bufio.NewScanner(os.Stdin)
		go func() {
			for scanner.Scan() {
				hashAndName := strings.Split(scanner.Text(), "  ")
				hash := []byte{}
				_, err := fmt.Sscanf(hashAndName[0], "%x", &hash)
				if err != nil {
					fmt.Println("Sscanf:", err)
					continue
				}
				name := hashAndName[1]
				lock.Lock()
				outstanding[name] = hash
				lock.Unlock()
				files <- name
			}
			if err := scanner.Err(); err != nil {
				fmt.Fprintln(os.Stderr, "reading standard input:", err)
			}
			close(files)
		}()
		go func() {
			for result := range results {
				lock.Lock()
				hash := outstanding[result.name]
				delete(outstanding, result.name)
				lock.Unlock()

				var outcome string
				if bytes.Equal(hash, result.hash) {
					outcome = "OK"
				} else {
					outcome = "FAILED"
				}
				fmt.Printf("%s: %s\n", result.name, outcome)
			}
			close(done)
		}()
	} else {
		scanner := bufio.NewScanner(os.Stdin)
		go func() {
			for scanner.Scan() {
				files <- scanner.Text()
			}
			if err := scanner.Err(); err != nil {
				fmt.Fprintln(os.Stderr, "reading standard input:", err)
			}
			close(files)
		}()
		go func() {
			for result := range results {
				fmt.Printf("%x  %s\n", result.hash, result.name)
			}
			close(done)
		}()
	}

	wg.Wait()
	close(results)
	<-done

	return
}
