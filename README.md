# Distributed Fake Twitter 

A fake, but distributed version of twitter. 

**Contributors**:

1. Alexandre Abreu ([up201800168@up.pt](mailto:up201800168@up.pt))
2. Diana Freitas ([up201806230@up.pt](mailto:up201806230@up.pt))
3. Juliane Marubayashi ([up201800175@up.pt](mailto:up201800175@up.pt))
4. Simão Lúcio ([up201303845@up.pt](mailto:up201303845@up.pt))

## Instalation

To install the program the only needed steps are to clone the repository and install its dependencies.

Assumming you have [pipenv](https://pypi.org/project/pipenv/) installed, just run the following commands:

```console
$ git clone https://git.fe.up.pt/sdle/2021/t3/g14/proj2
$ cd proj2
$ pipenv install
```

The following command is required to be run in every shell that will execute one of the execution commands:

```console
$ pipenv shell
```

## Execution

The repository already has default configurations in the [config folder](config/), so it can be run as follows.

Start by creating a bootstrap peer:

```console
$ python -m src.bootstrap
```

Then, just start peers with different addresses, it's possible to do that with the following command:

```console
$ python -m src 127.0.0.1 3000
```

With _127.0.0.1_ as IP and _3000_ as port.

## Cleaning

To clean the temporary files created after the executions, just run:

```console
$ make clean
```
