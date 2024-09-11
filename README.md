## Genomator Tests
This repository is used to generate the figures and tables used in the paper "Privacy-hardened and hallucination-resistant synthetic data generation with logic-solvers". There are currently two ways to run these scripts, using Code Ocean and using Docker.

### Code Ocean
Navigate to [https://codeocean.com/capsule/1806639](https://codeocean.com/capsule/1806639) and select "Reproducible Run". This may require making an account for Code Ocean. Please also note that the runtime for all the tests can be in excess of 4 hours. 

When the run is complete the resulting files will be in `results/` organised by test name.

### Docker
From the Code Ocean capsule (accessible at [https://codeocean.com/capsule/1806639](https://codeocean.com/capsule/1806639)), click on `Capsule` and then `Export...`. Opt to include the data. Extract the zip file and inspect `REPRODUCING.md` for detailed instructions on how to run the capsule in Docker.
The simple instructions are below.

To build the docker image:
```shell
cd environment && docker build . --tag genomator-tests; cd ..
```
To run the capsule:
```shell
docker run --platform linux/amd64 --rm --gpus all \
  --workdir /code \
  --volume "$PWD/data":/data \
  --volume "$PWD/code":/code \
  --volume "$PWD/results":/results \
  genomator-tests bash run
```
The completed test files will be stored in the `results/` directory, organised by test name.

### Customising the tests
If skipping a particular test is desired, simply edit that test name (in `code/tests`) to change the suffix from `.sh` to something else. Otherwise the main run script `code/run` can be edited to customise which tests are to be run (for example by specifying a particular test in the for loop or using a continue in the loop if the test is not desired).

For performance reasons, the alternative methods have had their results precomputed and added to the `data/vcfshark` directory. If real-time execution of the alternative methods is desired, edit the relevant script (e.g. `code/tests/attribute.sh`) at the algorithm selection location. This will be a block beginning with something like `if [[ "${alg}" == "GENOMATOR" ]]; then`.