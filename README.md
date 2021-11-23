# stock-market-engine

stock-market-engine is a Python microservice application that serves a REST API to create/query/update stock market information.
It's build on top of the [stock-market-lib](https://bitbucket.org/MattiasDC/stock-market-lib.git) library.

## Installation

Use [docker](https://www.docker.com/) to install docker and then build stock-market-engine.

```bash
git clone https://bitbucket.org/MattiasDC/stock-market-engine.git
cd stock-market-engine
docker-compose -f docker-compose-dev.yml build
docker-compose -f docker-compose-dev.yml up
```

Open a web browser at 0.0.0.0:/docs to inspect the REST API

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)