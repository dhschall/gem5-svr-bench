# Nodeapp Benchmark

This benchmark implements a small online shop websevice written in java script.
The content is served using an `nginx` web server and the application logic is implemented using `nodejs`. Thus the benchmark has two containers, one for the web server and one for the application logic.
Everything is fully containerized using docker.

## Starting the website

Use `docker-compose` to start the benchmark.
```bash
docker compose -f docker-compose.yaml up
```
The website will be served on at port 9999. Thus, to access the content open `localhost:9999` in your browser.

## Invoking the website

To invoke the website you can use a browser or stress the server using the [http-client](./../../client/) provided with this repo.
Alternatively, you can use [siege](https://linux.die.net/man/1/siege). See the Mediawiki benchmark for more details on how to use siege.

#### Using http-client

Build the client and invoke it using the provided `urls.tmpl` file.
Refer to the [README](./../../client/README.md) for additional information to use the client.
The client will send different requests to add items to the shopping cart, checkout, etc.

```bash
./http-client -url localhost -port 9999 -f urls.tmpl
```

