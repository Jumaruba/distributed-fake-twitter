# SDLE Project

SDLE Project for group T3G14.

Group members:

1. Alexandre Abreu ([up201800168@up.pt](mailto:up201800168@up.pt))
2. Diana Freitas ([up201806230@up.pt](mailto:up201806230@up.pt))
3. Juliane Marubayashi ([up201800175@up.pt](mailto:up201800175@up.pt))
4. Simão Lúcio ([up201303845@up.pt](mailto:up201303845@up.pt))

## Instalation

To install the program the only needed step is to clone the repository:

```console
git clone https://git.fe.up.pt/sdle/2021/t3/g14/proj2
cd proj2
```

## Execution

The repository already has default configurations in the [config folder](config/), so it can be run as follows.

To create a bootstrap peer:

```console
python -m src.bootstrap
```

Then, just start peers with different addresses, it's possible to do that with the following command:

```console
python -m src 127.0.0.1 3000
```

With _127.0.0.1_ as IP and _3000_ as port.

